"""
GS Tool CLI
===========

Утилита командной строки для работы со скриптами телеметрии (GS scripts):

- Инициализация проекта скрипта (`gs create <name>`)
- Препроцессинг и генерация инклюда (`gs preprocess`)
- Сборка (компиляция) скрипта (`gs build`)
- Подготовка релизного архива (`gs release`)
- Публикация релизов на сервер (`gs push`)
- Выпуск и управление application tokens / PAT (`gs token ...`)

Зависимости и требования:
- Для препроцессинга требуется установленный пакет Jinja2
  (если отсутствует — будет выведена подсказка об установке).
- Для сборки используется компилятор pawncc; если недоступен, на macOS/Linux
  будет автоматически создан dummy AMX для отладки пайплайна.
- Конфигурация сервера и ключей хранится в файле `~/.gs_tool/config.json`.

Быстрые примеры:
  $ gs create my_script
  $ cd my_script && gs build
  $ gs release && gs push --company-id=<COMPANY_ID>
  $ gs token create --email you@example.com  # выпуск PAT и запись в конфиг
"""

import click
import os
import json
import requests
import datetime
import shutil
import uuid
import subprocess
import tempfile
import struct
import binascii
import re
import zipfile
import sys
import hashlib  # Добавлено для SHA-256
from typing import Optional
from pathlib import Path
from .config import load_config
from getpass import getpass
import io

PROJECT_FILE = 'gs_project.json'
HISTORY_DIR = '.gs_history'

def extract_field_signature(field):
    """Извлекает сигнатуру поля для сравнения (idx, type, name, ui.options для enum)."""
    signature = {
        'idx': field.get('idx'),
        'type': field.get('type'),
        'name': field.get('name')
    }
    # Для enum также важны опции
    if field.get('type') == 'ENUM':
        # Нормализуем источник enum: предпочитаем enum_values (каноника)
        enum_values = field.get('enum_values')
        if isinstance(enum_values, dict):
            # сортируем по ключу для стабильности
            signature['enum_options'] = sorted(enum_values.items())
        else:
            # fallback: ui.options
            ui = field.get('ui') or {}
            if isinstance(ui.get('options'), list):
                signature['enum_options'] = [(opt.get('name'), opt.get('value')) for opt in ui['options']]
    return signature

def check_config_compatibility(current_config, previous_configs):
    """
    Проверяет совместимость текущей конфигурации с предыдущими релизами.
    
    Возвращает кортеж (entry_compatible, descriptor_compatible, changes_description)
    где:
    - entry_compatible: bool - нужно ли менять uuid_cfg_entry
    - descriptor_compatible: bool - нужно ли менять uuid_cfg_descriptor  
    - changes_description: str - описание изменений
    """
    changes = []
    entry_breaking_changes = False
    descriptor_breaking_changes = False
    
    current_fields = {f['name']: f for f in current_config.get('fields', [])}
    
    for prev_config in previous_configs:
        prev_fields = {f['name']: f for f in prev_config.get('fields', [])}
        
        # Проверяем изменения в существующих полях
        for field_name, prev_field in prev_fields.items():
            if field_name in current_fields:
                current_field = current_fields[field_name]
                prev_sig = extract_field_signature(prev_field)
                curr_sig = extract_field_signature(current_field)
                
                # Проверка изменений, нарушающих entry compatibility
                if prev_sig != curr_sig:
                    entry_breaking_changes = True
                    changes.append(f"Поле '{field_name}' изменилось: {prev_sig} -> {curr_sig}")
                
                # Любое изменение в полях нарушает descriptor compatibility
                if prev_field != current_field:
                    descriptor_breaking_changes = True
                    if prev_sig == curr_sig:
                        changes.append(f"Поле '{field_name}' изменило метаданные (ui, default, etc)")
            else:
                # Удаление поля - это критическое изменение
                entry_breaking_changes = True
                descriptor_breaking_changes = True
                changes.append(f"Поле '{field_name}' было удалено")
        
        # Проверяем новые поля (это изменяет только descriptor, не entry)
        for field_name in current_fields:
            if field_name not in prev_fields:
                descriptor_breaking_changes = True
                changes.append(f"Добавлено новое поле '{field_name}'")
    
    return entry_breaking_changes, descriptor_breaking_changes, '\n'.join(changes)

def get_previous_releases():
    """Получает конфигурации из предыдущих релизов."""
    if not os.path.exists(HISTORY_DIR):
        return []
    
    previous_configs = []
    releases = [f for f in os.listdir(HISTORY_DIR) if f.startswith('release_v') and f.endswith('.zip')]
    
    for release in sorted(releases):
        try:
            with zipfile.ZipFile(os.path.join(HISTORY_DIR, release), 'r') as zf:
                with zf.open(PROJECT_FILE) as f:
                    data = json.load(f)
                    previous_configs.append(data.get('config', {}))
        except:
            continue
    
    return previous_configs

def crc32(data: bytes) -> int:
    """Вычисляет CRC32 для данных."""
    polynom = 0xEDB88320
    sum_value = 0xFFFFFFFF
    
    for byte in data:
        sum_value ^= byte
        for _ in range(8):
            sum_value = ((-(sum_value & 1) & polynom) ^ (sum_value >> 1)) & 0xFFFFFFFF
    
    return sum_value & 0xFFFFFFFF

def debug_amx_header(bytecode_data: bytes) -> None:
    """Анализирует и выводит информацию о заголовке AMX байткода."""
    if len(bytecode_data) < 56:  # Минимальный размер AMX_HEADER
        click.echo("❌ Байткод слишком короткий для анализа AMX заголовка")
        return
    
    try:
        # Парсим AMX_HEADER структуру
        size = struct.unpack('<I', bytecode_data[0:4])[0]
        magic = struct.unpack('<H', bytecode_data[4:6])[0]
        file_version = bytecode_data[6]
        amx_version = bytecode_data[7]
        flags = struct.unpack('<h', bytecode_data[8:10])[0]
        defsize = struct.unpack('<h', bytecode_data[10:12])[0]
        cod = struct.unpack('<i', bytecode_data[12:16])[0]
        dat = struct.unpack('<i', bytecode_data[16:20])[0]
        hea = struct.unpack('<i', bytecode_data[20:24])[0]
        stp = struct.unpack('<i', bytecode_data[24:28])[0]
        cip = struct.unpack('<i', bytecode_data[28:32])[0]
        publics = struct.unpack('<i', bytecode_data[32:36])[0]
        natives = struct.unpack('<i', bytecode_data[36:40])[0]
        libraries = struct.unpack('<i', bytecode_data[40:44])[0]
        pubvars = struct.unpack('<i', bytecode_data[44:48])[0]
        tags = struct.unpack('<i', bytecode_data[48:52])[0]
        nametable = struct.unpack('<i', bytecode_data[52:56])[0]
        
        click.echo("🔍 === Анализ AMX заголовка ===")
        click.echo(f"📦 Полный размер файла: {size} байт")
        click.echo(f"🔮 Магическое число: 0x{magic:04X} {'✅' if magic == 0xF1E0 else '❌ (ожидается 0xF1E0)'}")
        click.echo(f"📄 Версия формата файла: {file_version}")
        click.echo(f"⚙️  Версия AMX движка: {amx_version}")
        click.echo(f"🏁 Флаги: 0x{flags:04X}")
        click.echo(f"📏 Размер элемента таблицы: {defsize} байт")
        click.echo(f"💾 Offset байткода (cod): 0x{cod:04X} ({cod})")
        click.echo(f"📊 Offset данных (dat): 0x{dat:04X} ({dat})")
        click.echo(f"🗄️  Начальный heap (hea): 0x{hea:04X} ({hea})")
        click.echo(f"📚 Stack top (stp): 0x{stp:04X} ({stp})")
        click.echo(f"🎯 Instruction pointer (cip): 0x{cip:04X} ({cip})")
        click.echo(f"🔧 Public функции: 0x{publics:04X} ({publics})")
        click.echo(f"🛠️  Native функции: 0x{natives:04X} ({natives})")
        click.echo(f"📚 Библиотеки: 0x{libraries:04X} ({libraries})")
        click.echo(f"🌍 Public переменные: 0x{pubvars:04X} ({pubvars})")
        click.echo(f"🏷️  Теги: 0x{tags:04X} ({tags})")
        click.echo(f"📝 Таблица имён: 0x{nametable:04X} ({nametable})")
        
        # Дополнительная валидация
        if size != len(bytecode_data):
            click.echo(f"⚠️  Размер в заголовке ({size}) не соответствует реальному размеру ({len(bytecode_data)})")
        
        # Проверяем основные offset'ы
        if cod > len(bytecode_data):
            click.echo(f"❌ Offset байткода выходит за границы файла")
        if dat > len(bytecode_data):
            click.echo(f"❌ Offset данных выходит за границы файла")
            
        click.echo("🔍 === Конец анализа ===")
        
    except Exception as e:
        click.echo(f"❌ Ошибка при анализе AMX заголовка: {str(e)}")

def create_binary_header(name: str, script_uuid_str: str, config_uuid_str: str, desc_uuid_str: str, version: str, data: bytes, desc_size: int) -> bytes:
    """Создает заголовок для бинарного файла в соответствии со структурой DataHeader (256 байт).

    Обновления:
    - добавлено поле descSize (4 байта, little-endian) — размер zip-дескриптора, который следует сразу после байткода
    - зарезервированная область уменьшена до 24 байт, общий размер заголовка остаётся 256 байт
    """
    # Константы максимальных размеров
    MAX_SCRIPT_NAME_SIZE = 128
    MAX_VERSION_SIZE = 12
    MAX_DATA_SIZE = 1024 * 1024
    
    # Проверки на максимальные размеры
    if len(name.encode('utf-8')) >= MAX_SCRIPT_NAME_SIZE:
        raise ValueError(f"Имя скрипта слишком длинное: {len(name)} символов, максимум {MAX_SCRIPT_NAME_SIZE-1}")
    if len(version.encode('utf-8')) >= MAX_VERSION_SIZE:
        raise ValueError(f"Версия слишком длинная: {len(version)} символов, максимум {MAX_VERSION_SIZE-1}")
    if len(data) > MAX_DATA_SIZE:
        raise ValueError(f"Размер данных превышает максимум: {len(data)} > {MAX_DATA_SIZE}")
    
    header = bytearray(256)  # Фиксированный размер 256 байт
    offset = 0
    
    # 1. scriptUuid (16 байт бинарно)
    script_uuid_bytes = uuid.UUID(script_uuid_str).bytes
    header[offset:offset + 16] = script_uuid_bytes
    offset += 16
    
    # 2. commitHash (32 байта, SHA-256 от данных)
    commit_hash = hashlib.sha256(data).digest()
    header[offset:offset + 32] = commit_hash
    offset += 32
    
    # 3. configUuid (16 байт бинарно)
    config_uuid_bytes = uuid.UUID(config_uuid_str).bytes
    header[offset:offset + 16] = config_uuid_bytes
    offset += 16
    
    # 4. descUuid (16 байт бинарно)
    desc_uuid_bytes = uuid.UUID(desc_uuid_str).bytes
    header[offset:offset + 16] = desc_uuid_bytes
    offset += 16
    
    # 5. name (128 байт, с нуль-терминацией)
    name_bytes = name.encode('utf-8')[:MAX_SCRIPT_NAME_SIZE - 1] + b'\0'
    header[offset:offset + MAX_SCRIPT_NAME_SIZE] = name_bytes.ljust(MAX_SCRIPT_NAME_SIZE, b'\0')
    offset += MAX_SCRIPT_NAME_SIZE
    
    # 6. version (12 байт, с нуль-терминацией)
    version_bytes = version.encode('utf-8')[:MAX_VERSION_SIZE - 1] + b'\0'
    header[offset:offset + MAX_VERSION_SIZE] = version_bytes.ljust(MAX_VERSION_SIZE, b'\0')
    offset += MAX_VERSION_SIZE
    
    # 7. size (4 байта, little-endian)
    struct.pack_into('<I', header, offset, len(data))
    offset += 4
    
    # 8. crc32 (4 байта, little-endian)
    crc = crc32(data)
    struct.pack_into('<I', header, offset, crc)
    offset += 4
    
    # 9. descSize (4 байта, little-endian) — размер zip дескриптора, который идёт сразу после p-кода
    struct.pack_into('<I', header, offset, int(desc_size) if desc_size is not None else 0)
    offset += 4

    # 10. reserved (24 байта, заполненные нулями)
    # Уже инициализированы нулями в bytearray
    
    return bytes(header)


def build_descriptor_zip(project_data: dict) -> bytes:
    """Формирует zip (DEFLATED) с файлом descriptor.json из тех же данных,
    что отправляются на сервер в поле descriptor_schema.

    Содержимое: один файл 'descriptor.json' (UTF-8), без BOM.
    """
    ds = {
        "config": project_data.get("config", {}),
        "datasources": project_data.get("datasources", {}),
        "subscriptions": project_data.get("subscriptions", []),
        "api": project_data.get("api", {}),
    }
    json_bytes = json.dumps(ds, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('descriptor.json', json_bytes)
    return buffer.getvalue()

@click.group()
def main():
    """GS Tool — утилита управления скриптами телеметрии.

    Основные команды:
    - create: создать новый проект из шаблона
    - preprocess: валидация и генерация `project.inc`
    - build: препроцессинг + компиляция (AMX) + упаковка BIN
    - release: создать zip-архив релиза из текущего состояния проекта
    - push: загрузить все релизы из истории на сервер rmt-cfg
    - token: управление токенами доступа (PAT)

    Запустите `gs --help` или `gs <command> --help` для справки по командам.
    """
    pass

@main.command()
@click.argument('name')
def create(name):
    """Создать новый проект скрипта в папке <name>.

    Действия:
    - создаёт каркас проекта и файл `gs_project.json`
    - генерирует UUID-идентификаторы и заготовку конфигурации
    - копирует `gs_natives.inc` и создаёт `main.p` из шаблона

    Пример:
      gs create my_script
    """
    if os.path.exists(name):
        click.echo(f"Ошибка: Папка {name} уже существует.")
        return
    
    os.makedirs(name, exist_ok=True)
    project_path = os.path.join(name, PROJECT_FILE)
    history_path = os.path.join(name, HISTORY_DIR)
    
    # Загружаем шаблон
    template_path = os.path.join(os.path.dirname(__file__), 'project_template.json')
    with open(template_path, 'r', encoding='utf-8') as f:
        project_data = json.load(f)

    # Заполняем уникальные данные
    script_uuid = str(uuid.uuid4())
    project_data['script_id'] = script_uuid
    project_data['script_commit'] = str(uuid.uuid4())
    project_data['project_name'] = name
    project_data['version'] = '0.0.1'

    # Генерируем uuid_ui_descriptor/descriptor_uuid (один и тот же идентификатор)
    new_desc_uuid = str(uuid.uuid4())
    project_data['uuid_ui_descriptor'] = new_desc_uuid
    project_data['descriptor_uuid'] = new_desc_uuid  # fallback field

    # Обновляем UUID'ы разделов
    project_data['config']['name'] = f"{name}"

    # Спрашиваем о публичности скрипта
    is_public = click.confirm("Сделать скрипт публичным?", default=False)
    project_data['is_public'] = is_public

    # Обновляем UUID'ы для каждого датасорса (список или словарь)
    if 'datasources' in project_data:
        if isinstance(project_data['datasources'], list):
            for ds in project_data['datasources']:
                ds['uuid'] = str(uuid.uuid4())
        elif isinstance(project_data['datasources'], dict):
            for key, ds in project_data['datasources'].items():
                ds['uuid'] = ds.get('uuid', str(uuid.uuid4()))
    
    project_data['api']['uuid'] = str(uuid.uuid4())
    project_data['template']['uuid'] = str(uuid.uuid4())

    # Обновляем UUID'ы разделов
    project_data['config']['uuid_cfg_entry'] = str(uuid.uuid4())
    # Делаем uuid_cfg_descriptor равным uuid_ui_descriptor, чтобы не было расхождений
    project_data['config']['uuid_cfg_descriptor'] = new_desc_uuid
    project_data['config']['name'] = f"{name}"

    # UUID подписок больше не нужны - используется script_id из шаблона

    with open(project_path, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)
    
    os.makedirs(history_path, exist_ok=True)
    visibility_status = "публичный" if is_public else "приватный"
    click.echo(f"Проект {name} успешно создан. Файл настроек создан: {project_path}")
    click.echo(f"Статус видимости: {visibility_status}")
    
    # Копируем файл gs_natives.inc в корень проекта
    natives_src = os.path.join(os.path.dirname(__file__), 'templates', 'gs_natives.inc')
    natives_dst = os.path.join(name, 'gs_natives.inc')
    try:
        shutil.copy2(natives_src, natives_dst)
        click.echo('Файл gs_natives.inc скопирован в проект.')
    except FileNotFoundError:
        click.echo('Ошибка: шаблон gs_natives.inc не найден внутри пакета. Проверьте установку gs_tool.')
        return False

    # Создаем main.p из шаблона
    main_template = os.path.join(os.path.dirname(__file__), 'templates', 'main.p.j2')
    main_dst = os.path.join(name, 'main.p')
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template('main.p.j2')
        rendered_main = template.render(
            config_name=project_data['config'].get('name', 'Config')
        )
        with open(main_dst, 'w', encoding='utf-8') as f_dst:
            f_dst.write(rendered_main)
        click.echo("Файл main.p создан.")
    except ImportError:
        # Fallback если Jinja2 не установлена
        with open(main_template, 'r', encoding='utf-8') as f_tpl, open(main_dst, 'w', encoding='utf-8') as f_dst:
            f_dst.write(f_tpl.read())
        click.echo("Файл main.p создан (без рендеринга шаблона).")
    except FileNotFoundError:
        click.echo("Предупреждение: шаблон main.p.j2 не найден, main.p не создан.")

def run_preprocess() -> bool:
    """Выполнить препроцессинг проекта: валидация и генерация `project.inc`.

    Проверяется корректность `config`, `datasources`, API endpoints и подписок.
    Требуется наличие `gs_natives.inc`. Для генерации используется Jinja2.

    Возвращает True при успехе, иначе False.
    """

    if not os.path.exists(PROJECT_FILE):
        click.echo(f"Ошибка: Файл {PROJECT_FILE} не найден. Инициализируйте проект с помощью 'gs init'.")
        return False

    click.echo("Препроцессинг проекта...")

    # Читаем конфигурацию проекта
    with open(PROJECT_FILE, 'r', encoding='utf-8') as f:
        project_data = json.load(f)

    # Убеждаемся, что в корне проекта присутствует gs_natives.inc
    natives_dst = os.path.join(os.getcwd(), 'gs_natives.inc')
    if not os.path.exists(natives_dst):
        natives_src = os.path.join(os.path.dirname(__file__), 'templates', 'gs_natives.inc')
        if os.path.exists(natives_src):
            try:
                shutil.copy2(natives_src, natives_dst)
                click.echo('Файл gs_natives.inc скопирован в проект.')
            except FileNotFoundError:
                click.echo('Ошибка: шаблон gs_natives.inc отсутствует. Выполните повторно "gs create" или восстановите файл вручную.')
                return False
        else:
            click.echo('Ошибка: шаблон gs_natives.inc отсутствует. Выполните повторно "gs create" или восстановите файл вручную.')
            return False

    # --- Валидация конфигурации ---
    if 'config' not in project_data or 'fields' not in project_data['config']:
        click.echo("Ошибка: Конфигурация не содержит полей.")
        return False

    if 'name' not in project_data['config'] or not project_data['config']['name']:
        click.echo("Ошибка: Конфигурация не содержит имени (config.name).")
        return False
    
    if not isinstance(project_data['config']['name'], str) or not project_data['config']['name'].isidentifier():
        click.echo(f"Ошибка: Имя конфигурации '{project_data['config'].get('name', '')}' некорректно (должно быть на латинице, без пробелов и спецсимволов).")
        return False

    for field in project_data['config']['fields']:
        if 'name' not in field or not field['name']:
            click.echo("Ошибка: Поле конфигурации не содержит имени.")
            return False
        if not isinstance(field['name'], str) or not field['name'].isidentifier():
            click.echo(f"Ошибка: Имя поля '{field.get('name', '')}' не соответствует требованиям (должно быть на латинице, без пробелов и спецсимволов).")
            return False
        if 'type' not in field or field['type'] not in ['INT8','INT16','INT32','UINT8','UINT16','UINT32','FLOAT','DOUBLE','STRING','ENUM','ARRAY','BOOL']:
            click.echo(f"Ошибка: Поле '{field.get('name', '')}' имеет некорректный тип.")
            return False
        # Приведение min/max к числам, если есть
        if 'min' in field and isinstance(field['min'], str):
            try:
                field['min'] = int(field['min']) if field['type'] != 'FLOAT' else float(field['min'])
            except Exception:
                pass
        if 'max' in field and isinstance(field['max'], str):
            try:
                field['max'] = int(field['max']) if field['type'] != 'FLOAT' else float(field['max'])
            except Exception:
                pass
        # ARRAY: убедимся, что задан item_type и корректен
        if field['type'] == 'ARRAY':
            if 'item_type' not in field:
                # попытка вывести из min/max
                try:
                    mn = int(field.get('min', 0))
                    mx = int(field.get('max', 0))
                    if mn >= 0 and mx <= 255:
                        field['item_type'] = 'UINT8'
                    elif mn >= 0 and mx <= 65535:
                        field['item_type'] = 'UINT16'
                    elif mn >= 0 and mx <= 4294967295:
                        field['item_type'] = 'UINT32'
                    else:
                        field['item_type'] = 'INT32'
                except Exception:
                    field['item_type'] = 'INT32'
        # ENUM: нормализуем enum_values из ui.options при отсутствии
        if field['type'] == 'ENUM' and 'enum_values' not in field:
            ui = field.get('ui') or {}
            opts = ui.get('options')
            if isinstance(opts, list):
                enum_values = {}
                for opt in opts:
                    name = opt.get('name')
                    val = opt.get('value')
                    if name is None:
                        continue
                    enum_values[str(name)] = int(val) if val is not None else len(enum_values)
                if enum_values:
                    field['enum_values'] = enum_values

    # --- Валидация датасорсов ---
    if 'datasources' not in project_data:
        click.echo("Ошибка: Datasources отсутствуют в проекте.")
        return False

    # Допускаем два формата: список или словарь {name: {...}}
    if isinstance(project_data['datasources'], dict):
        ds_list = []
        for ds_name, ds_data in project_data['datasources'].items():
            if not isinstance(ds_data, dict):
                click.echo(f"Ошибка: Datasource '{ds_name}' имеет некорректный формат (ожидается объект).")
                return False
            if 'name' not in ds_data:
                ds_data = {**ds_data, 'name': ds_name}
            ds_list.append(ds_data)
        project_data['datasources'] = ds_list
    elif not isinstance(project_data['datasources'], list):
        click.echo("Ошибка: Datasources имеет неподдерживаемый формат (ожидается массив или объект).")
        return False

    if not project_data['datasources']:
        click.echo("Ошибка: Список датасорсов пуст.")
        return False

    for datasource in project_data['datasources']:
        if 'name' not in datasource or not datasource['name']:
            click.echo("Ошибка: Датасорс не содержит имени.")
            return False
        if not isinstance(datasource['name'], str) or not datasource['name'].isidentifier():
            click.echo(f"Ошибка: Имя датасорса '{datasource.get('name', '')}' некорректно.")
            return False
        if 'uuid' not in datasource or not datasource['uuid']:
            click.echo(f"Ошибка: Датасорс '{datasource.get('name', '')}' не содержит UUID.")
            return False
        if 'fields' not in datasource or not isinstance(datasource['fields'], list):
            click.echo(f"Ошибка: Датасорс '{datasource.get('name', '')}' не содержит полей или поля не являются массивом.")
            return False

        for field in datasource['fields']:
            if 'name' not in field or not field['name']:
                click.echo(f"Ошибка: Поле датасорса '{datasource.get('name', '')}' не содержит имени.")
                return False
            if not isinstance(field['name'], str) or not field['name'].isidentifier():
                click.echo(f"Ошибка: Имя поля датасорса '{datasource.get('name', '')}.{field.get('name', '')}' некорректно.")
                return False
            if 'type' not in field or field['type'] not in ['INT8','INT16','INT32','UINT8','UINT16','UINT32','FLOAT','STRING','ENUM','ARRAY','BOOL']:
                click.echo(f"Ошибка: Поле датасорса '{datasource.get('name', '')}.{field.get('name', '')}' имеет некорректный тип.")
                return False

    # --- Валидация API endpoints ---
    if 'api' in project_data and 'endpoints' in project_data['api']:
        for endpoint in project_data['api']['endpoints']:
            if 'name' not in endpoint or not endpoint['name']:
                click.echo("Ошибка: API endpoint не содержит имени.")
                return False
            if not isinstance(endpoint['name'], str) or not endpoint['name'].isidentifier():
                click.echo(f"Ошибка: Имя API endpoint '{endpoint.get('name', '')}' некорректно.")
                return False
            if 'signature' not in endpoint or not isinstance(endpoint['signature'], list):
                click.echo(f"Ошибка: API endpoint '{endpoint.get('name', '')}' не содержит корректной сигнатуры.")
                return False
            for sig in endpoint['signature']:
                if 'type' not in sig or sig['type'] not in ['FST_CELL', 'FST_ARRAY', 'FST_STRING', 'FST_FLOAT', 'FST_FIXED']:
                    click.echo(f"Ошибка: Некорректный тип сигнатуры в API endpoint '{endpoint.get('name', '')}': {sig.get('type', '')}")
                    return False

    # --- Валидация подписок ---
    if 'subscriptions' in project_data:
        for sub in project_data['subscriptions']:
            if 'path' not in sub or not sub['path']:
                click.echo("Ошибка: Подписка не содержит пути.")
                return False
            if 'function' not in sub or not sub['function']:
                click.echo("Ошибка: Подписка не содержит имени функции.")
                return False

    click.echo("Валидация конфигурации, датасорсов, API endpoints и подписок прошла успешно.")

    # --- Генерация Pawn-кода через Jinja2 ---
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        click.echo("Ошибка: Требуется установить Jinja2. Выполните 'pip install jinja2'.")
        return False

    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template('project.inc.j2')

    rendered_code = template.render(
        script_id=project_data['script_id'],
        version=project_data.get('version', '0.0.1'),
        fields=project_data['config']['fields'],
        config_uuid_cfg_entry=project_data['config'].get('uuid_cfg_entry', project_data['config'].get('uuid', '')),
        config_uuid_cfg_descriptor=project_data['config'].get('uuid_cfg_descriptor', project_data['config'].get('uuid', '')),
        config_name=project_data['config'].get('name', 'Config'),
        datasources=project_data['datasources'],
        functions=project_data.get('api', {}).get('endpoints', []),
        subscriptions=project_data.get('subscriptions', [])
    )

    with open('project.inc', 'w', encoding='utf-8') as f:
        f.write(rendered_code)

    click.echo("Препроцессинг завершён. Файл project.inc сгенерирован.")
    return True

@main.command(name='preprocess')
def preprocess_cmd():
    """Выполнить только препроцессинг (валидация + генерация `project.inc`).

    Полезно для проверки корректности проекта без компиляции.
    """
    run_preprocess()

@main.command()
def build():
    """Собрать проект: препроцессинг + компиляция + упаковка BIN.

    Этапы:
    1) Препроцессинг и генерация `project.inc`
    2) Компиляция `main.p` с анализом/подбором размера стека
    3) Создание бинаря `<script_uuid>` (заголовок + AMX)

    Примечания:
    - Если компилятор pawncc недоступен, будет создан dummy AMX.
    - Требует `gs_project.json` и `main.p` в корне проекта.
    """
    click.echo("Сборка проекта...")

    # Проверяем наличие файла проекта
    if not os.path.exists(PROJECT_FILE):
        click.echo(f"Ошибка: Файл {PROJECT_FILE} не найден. Инициализируйте проект с помощью 'gs create'.")
        return

    # Читаем данные проекта
    with open(PROJECT_FILE, 'r', encoding='utf-8') as f:
        project_data = json.load(f)

    # Сначала выполняем препроцессинг. Если он завершился с ошибкой — прерываем сборку.
    if not run_preprocess():
        click.echo("Сборка прервана из-за ошибок препроцессинга.")
        return

    # Проверяем наличие main.p
    if not os.path.exists("main.p"):
        click.echo("Ошибка: Файл main.p не найден.")
        return

    # Ищем компилятор сначала в пакете, затем в PATH
    package_dir = os.path.dirname(__file__)
    compiler_name = "pawncc.exe" if sys.platform == "win32" else "pawncc"
    package_compiler = os.path.join(package_dir, "bin", compiler_name)
    
    if os.path.exists(package_compiler):
        compiler = package_compiler
        click.echo(f"🔧 Используется встроенный компилятор: {compiler}")
    else:
        # Fallback: ищем в PATH
        compiler = "pawncc"
        if shutil.which(compiler) is None:
            # Пробуем с расширением .exe для Windows
            compiler = "pawncc.exe"
            if shutil.which(compiler) is None:
                # Fallback: создаём заглушечный AMX, чтобы не прерывать процесс на macOS/Linux
                click.echo("⚠️  Компилятор pawncc не найден. Создаю заглушечный байткод main.amx.")

                dummy_amx = Path("main.amx")
                if not dummy_amx.exists():
                    # Пишем минимальный заголовок (56 байт) + строку-метку
                    # AMX header начинается с размера файла (uint32). Заполняем корректно.
                    payload = b"DUMMY"  # небольшие данные
                    size = 56 + len(payload)
                    hdr = bytearray(56)
                    # size (uint32 little-endian)
                    struct.pack_into('<I', hdr, 0, size)
                    # magic 0xF1E0
                    struct.pack_into('<H', hdr, 4, 0xF1E0)
                    # versions, остальные поля можно оставить нулевыми
                    dummy_amx.write_bytes(hdr + payload)
                    click.echo("✅ Создан файл main.amx-заглушка.")

                # После создания заглушки продолжаем процесс, используя этот файл
                bytecode_data = dummy_amx.read_bytes()

                # Вычисляем CRC32
                crc = crc32(bytecode_data)

                # Получаем данные project.json
                project_name = project_data.get('project_name', 'unknown')
                script_uuid = project_data.get('script_id', str(uuid.uuid4()))
                config_uuid = project_data['config'].get('uuid_cfg_entry', str(uuid.uuid4()))
                desc_uuid = project_data['config'].get('uuid_cfg_descriptor', str(uuid.uuid4()))
                version = project_data.get('version', '0.0.1')

                # Формируем zip-дескриптор и обновлённый заголовок с descSize
                descriptor_zip = build_descriptor_zip(project_data)
                header = create_binary_header(
                    name=project_name,
                    script_uuid_str=script_uuid,
                    config_uuid_str=config_uuid,
                    desc_uuid_str=desc_uuid,
                    version=version,
                    data=bytecode_data,
                    desc_size=len(descriptor_zip),
                )

                final_data = header + bytecode_data + descriptor_zip
                output_filename = f"{script_uuid}"
                with open(output_filename, 'wb') as f_out:
                    f_out.write(final_data)

                click.echo(f"✅ Создан dummy-script файл: {output_filename} (header + {len(bytecode_data)} байт dummy)")
                click.echo(f"🔒 CRC32: 0x{crc:08X}")

                # Хэш версии устанавливается на этапе release, а не build

                return

    # Этап 1: Первая компиляция для определения размера стека
    click.echo("Этап 1: Первая компиляция для анализа размера стека...")
    
    # Добавляем флаги для более подробного вывода:
    # -v2 = verbose level 2
    # -d3 = debug level 3
    result1 = subprocess.run([compiler, "main.p", "-S=4096", "-O3", "-v2", "-d3"], 
                           capture_output=True, text=True)
    
    if result1.returncode != 0:
        click.echo("Ошибки первой компиляции:")
        if result1.stdout:
            click.echo(result1.stdout)
        if result1.stderr:
            click.echo(result1.stderr)
        click.echo(f"Первая компиляция завершилась с ошибками (код {result1.returncode}).")
        return
    
    # Парсим estimated max use из вывода
    estimated_cells = None
    combined_output = (result1.stdout or "") + "\n" + (result1.stderr or "")
    
    # Диагностика: выводим полный вывод компилятора для анализа
    click.echo("\n🔍 === Диагностика вывода компилятора ===")
    click.echo("📋 Полный вывод компилятора (stdout):")
    click.echo("---")
    if result1.stdout:
        click.echo(result1.stdout)
    else:
        click.echo("(пусто)")
    click.echo("---")
    click.echo("📋 Полный вывод компилятора (stderr):")
    click.echo("---")
    if result1.stderr:
        click.echo(result1.stderr)
    else:
        click.echo("(пусто)")
    click.echo("---")
    click.echo("🔍 === Конец диагностики ===\n")
    
    # Проверяем на рекурсию
    if "due to recursion" in combined_output:
        click.echo("⚠️  Обнаружена рекурсия! Компилятор не может точно оценить использование стека.")
        if "recursive function" in combined_output:
            # Извлекаем имена рекурсивных функций из предупреждений
            recursive_functions = re.findall(r'recursive function "([^"]+)"', combined_output)
            if recursive_functions:
                click.echo(f"📋 Рекурсивные функции: {', '.join(recursive_functions)}")
        
        click.echo("🔧 Компилятор автоматически установил достаточный размер стека для рекурсии")
        click.echo("📝 Используем результат первой компиляции (повторная сборка не требуется)")
        
        # Используем результат первой компиляции - там уже установлен правильный размер стека
        result = result1
    else:
        # Ищем различные форматы вывода размера стека
        # Вариант 1: Ищем в формате "Stack/heap size: XXXX bytes; estimated max. use=YY cells"
        match = re.search(r'estimated max\.\s*use=(\d+)\s*cells', combined_output)
        if match:
            estimated_cells = int(match.group(1))
            click.echo(f"📊 Найден прогноз использования стека: {estimated_cells} cells")
        else:
            # Вариант 2: Если не нашли estimated use, пробуем найти общий размер стека
            match = re.search(r'Stack/heap size:\s*(\d+)\s*bytes', combined_output)
            if match:
                # Конвертируем байты в cells (1 cell = 4 bytes для 32-битной архитектуры)
                stack_bytes = int(match.group(1))
                # Ищем также estimated use в той же строке
                est_match = re.search(r'Stack/heap size:\s*\d+\s*bytes;\s*estimated max\.\s*use=(\d+)\s*cells', combined_output)
                if est_match:
                    estimated_cells = int(est_match.group(1))
                    click.echo(f"📊 Найден размер стека: {stack_bytes} байт, прогноз использования: {estimated_cells} cells")
                else:
                    # Если нет estimated use, используем 10% от общего размера как оценку
                    estimated_cells = stack_bytes // 40  # 10% от размера в байтах, деленное на 4
                    click.echo(f"📊 Найден размер стека: {stack_bytes} байт, расчетная оценка: {estimated_cells} cells")
        
        if not match:
            # Вариант 3: Ищем любое упоминание о стеке
            stack_mentions = re.findall(r'(?:stack|heap).*?(\d+).*?(?:bytes|cells)', combined_output, re.IGNORECASE)
            if stack_mentions:
                click.echo(f"🔍 Найдены упоминания о стеке: {stack_mentions}")
        
        if estimated_cells is not None:
            optimal_stack = estimated_cells + 32
            click.echo(f"📊 Найден прогноз использования стека: {estimated_cells} cells")
            click.echo(f"⚡ Оптимальный размер стека: {optimal_stack} cells")
            
            # Этап 2: Перекомпиляция с оптимальным размером стека
            click.echo("Этап 2: Перекомпиляция с оптимальным размером стека...")
            
            result = subprocess.run([compiler, "main.p", f"-S={optimal_stack}", "-O3", "-d2"], 
                                  capture_output=True, text=True)
        else:
            click.echo("❓ Не удалось найти прогноз использования стека, используем результат первой компиляции")
            click.echo("💡 Подсказка: Возможно, компилятор использует другой формат вывода или требуется дополнительный флаг")
            result = result1
    
    # Выводим результаты финальной компиляции
    if result.stdout:
        click.echo("Вывод компилятора:")
        click.echo(result.stdout)
    if result.stderr:
        click.echo("Ошибки компилятора:")
        click.echo(result.stderr)
    
    if result.returncode != 0:
        click.echo(f"Компиляция завершилась с ошибками (код {result.returncode}).")
        return

    # Ищем файл main.amx, созданный компилятором
    amx_file = "main.amx"
    
    if not os.path.exists(amx_file):
        click.echo("Ошибка: Файл main.amx не найден. Компиляция могла завершиться с ошибками.")
        return

    # Читаем бинарные данные из main.amx
    with open(amx_file, 'rb') as f:
        bytecode_data = f.read()

    click.echo(f"Размер скомпилированного файла: {len(bytecode_data)} байт")

    # Анализируем AMX заголовок байткода
    debug_amx_header(bytecode_data)

    # Вычисляем CRC32
    crc = crc32(bytecode_data)

    # Получаем данные для заголовка
    project_name = project_data.get('project_name', 'unknown')
    script_uuid = project_data.get('script_id', str(uuid.uuid4()))
    config_uuid = project_data['config'].get('uuid_cfg_entry', str(uuid.uuid4()))
    desc_uuid = project_data['config'].get('uuid_cfg_descriptor', str(uuid.uuid4()))
    version = project_data.get('version', '0.0.1')

    # Создаем zip-дескриптор и заголовок с полем descSize
    descriptor_zip = build_descriptor_zip(project_data)
    header = create_binary_header(
        name=project_name,
        script_uuid_str=script_uuid,
        config_uuid_str=config_uuid,
        desc_uuid_str=desc_uuid,
        version=version,
        data=bytecode_data,  # Передаем данные для вычисления hash и crc
        desc_size=len(descriptor_zip),
    )

    # Объединяем заголовок, p-код и zip-дескриптор
    final_data = header + bytecode_data + descriptor_zip

    # Формируем имя выходного файла
    output_filename = f"{script_uuid}"

    # Сохраняем итоговый файл
    with open(output_filename, 'wb') as f:
        f.write(final_data)

    click.echo(f"Компиляция завершена успешно!")
    click.echo(f"✅ Создан файл: {output_filename}")
    click.echo(f"📦 Размер итогового файла: {len(final_data)} байт (заголовок: {len(header)} байт + данные: {len(bytecode_data)} байт)")
    click.echo(f"🔒 CRC32: 0x{crc:08X}")

@main.command()
def release():
    """Создать релизный zip-архив проекта.

    - Имя архива: `.gs_history/release_v<version>.zip`
    - Включает файлы проекта и артефакт `<script_id>.bin`
    - Проверяет совместимость конфигурации с предыдущими релизами и
      при необходимости предлагает сгенерировать новые UUID'ы.

    Перед запуском убедитесь, что выполнен `gs build`.
    """
    if not os.path.exists(PROJECT_FILE):
        click.echo(f"Ошибка: Файл {PROJECT_FILE} не найден. Инициализируйте проект с помощью 'gs create'.")
        return
    
    with open(PROJECT_FILE, 'r', encoding='utf-8') as f:
        project_data = json.load(f)
    
    project_name = project_data.get('project_name', 'unknown')
    version = project_data.get('version', '0.0.0')
    script_uuid = project_data.get('script_id')
    if not script_uuid:
        click.echo(f"Ошибка: Не найден script_id в {PROJECT_FILE}")
        return
    
    # Создаем директорию для истории, если её нет
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    # Имя архива релиза
    archive_name = f"release_v{version}.zip"
    archive_path = os.path.join(HISTORY_DIR, archive_name)
    
    if os.path.exists(archive_path):
        click.echo(f"Ошибка: Релиз для версии {version} уже существует: {archive_path}.")
        return
    
    # Проверяем совместимость с предыдущими релизами
    previous_configs = get_previous_releases()
    if previous_configs:
        current_config = project_data.get('config', {})
        entry_breaking, descriptor_breaking, changes = check_config_compatibility(current_config, previous_configs)
        
        if entry_breaking or descriptor_breaking:
            click.echo("\n⚠️  Обнаружены изменения в конфигурации:")
            click.echo(changes)
            
            config_changed = False
            
            if entry_breaking:
                click.echo("\n❗ Обнаружено нарушение обратной совместимости!")
                click.echo("Изменения затрагивают структуру полей (idx, type, name или enum options).")
                if click.confirm("Сгенерировать новый UUID_CFG_ENTRY?"):
                    new_uuid = str(uuid.uuid4())
                    project_data['config']['uuid_cfg_entry'] = new_uuid
                    config_changed = True
                    click.echo(f"✅ Новый UUID_CFG_ENTRY: {new_uuid}")
            
            if descriptor_breaking:
                click.echo("\n📝 Обнаружены изменения в метаданных конфигурации.")
                if click.confirm("Сгенерировать новый UUID_CFG_DESCRIPTOR?"):
                    new_uuid = str(uuid.uuid4())
                    project_data['config']['uuid_cfg_descriptor'] = new_uuid
                    config_changed = True
                    click.echo(f"✅ Новый UUID_CFG_DESCRIPTOR: {new_uuid}")
            
            if config_changed:
                # Сохраняем обновленный project.json
                with open(PROJECT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2, ensure_ascii=False)
                click.echo("💾 Файл gs_project.json обновлен.")
                
                # Перезапускаем препроцессинг
                click.echo("\n🔄 Перезапуск препроцессинга...")
                if not run_preprocess():
                    click.echo("❌ Ошибка при препроцессинге. Релиз отменен.")
                    return
                
                # Перезапускаем компиляцию
                click.echo("\n🔄 Перезапуск компиляции...")
                # Копируем логику компиляции из команды build
                package_dir = os.path.dirname(__file__)
                compiler_name = "pawncc.exe" if sys.platform == "win32" else "pawncc"
                package_compiler = os.path.join(package_dir, "bin", compiler_name)
                
                if os.path.exists(package_compiler):
                    compiler = package_compiler
                else:
                    compiler = "pawncc"
                    if shutil.which(compiler) is None:
                        compiler = "pawncc.exe"
                        if shutil.which(compiler) is None:
                            click.echo("❌ Компилятор pawncc не найден. Релиз отменен.")
                            return
                
                # Используем ту же логику компиляции, что и в build
                result1 = subprocess.run([compiler, "main.p", "-S=4096", "-O3", "-v2", "-d3"], 
                                      capture_output=True, text=True)
                
                if result1.returncode != 0:
                    click.echo("❌ Ошибка первой компиляции:")
                    if result1.stdout:
                        click.echo(result1.stdout)
                    if result1.stderr:
                        click.echo(result1.stderr)
                    return
                
                # Анализируем вывод для определения размера стека
                combined_output = (result1.stdout or "") + "\n" + (result1.stderr or "")
                estimated_cells = None
                
                # Проверяем на рекурсию
                if "due to recursion" in combined_output:
                    result = result1
                else:
                    # Ищем прогноз использования стека
                    match = re.search(r'estimated max\.\s*use=(\d+)\s*cells', combined_output)
                    if match:
                        estimated_cells = int(match.group(1))
                    else:
                        # Альтернативный поиск
                        est_match = re.search(r'Stack/heap size:\s*\d+\s*bytes;\s*estimated max\.\s*use=(\d+)\s*cells', combined_output)
                        if est_match:
                            estimated_cells = int(est_match.group(1))
                    
                    if estimated_cells is not None:
                        optimal_stack = estimated_cells + 32
                        # Перекомпиляция с оптимальным размером
                        result = subprocess.run([compiler, "main.p", f"-S={optimal_stack}", "-O3", "-d2"], 
                                              capture_output=True, text=True)
                    else:
                        result = result1
                
                if result.returncode != 0:
                    click.echo("❌ Ошибка компиляции:")
                    if result.stdout:
                        click.echo(result.stdout)
                    if result.stderr:
                        click.echo(result.stderr)
                    return
                
                # Создаем .bin файл
                if not os.path.exists("main.amx"):
                    click.echo("❌ Файл main.amx не найден после компиляции.")
                    return
                
                with open("main.amx", 'rb') as f:
                    bytecode_data = f.read()
                
                crc_val = crc32(bytecode_data)
                config_data = project_data.get('config', {})
                descriptor_zip = build_descriptor_zip(project_data)
                header = create_binary_header(
                    name=project_name,
                    script_uuid_str=project_data.get('script_id'),
                    config_uuid_str=config_data.get('uuid_cfg_entry', str(uuid.uuid4())),
                    desc_uuid_str=config_data.get('uuid_cfg_descriptor', str(uuid.uuid4())),
                    version=version,
                    data=bytecode_data,
                    desc_size=len(descriptor_zip),
                )
                
                final_data = header + bytecode_data + descriptor_zip
                bin_filename = f"{script_uuid}"
                
                with open(bin_filename, 'wb') as f:
                    f.write(final_data)
                
                click.echo(f"✅ Файл {bin_filename} пересоздан.")
    
    # Проверяем наличие .bin файла
    bin_filename = f"{script_uuid}"
    if not os.path.exists(bin_filename):
        click.echo(f"⚠️  Скомпилированный файл {bin_filename} не найден.")
        click.echo("🔨 Запустите 'gs build' перед созданием релиза.")
        return
    
    # Перед упаковкой: генерируем случайный 256-битный хэш коммита и сохраняем в project.json
    try:
        with open(PROJECT_FILE, 'r', encoding='utf-8') as f:
            current_project = json.load(f)
    except Exception:
        current_project = project_data

    # 256-битный случайный хэш (64 hex символа)
    random_commit = hashlib.sha256(os.urandom(32)).hexdigest()
    current_project['script_commit'] = random_commit
    with open(PROJECT_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_project, f, indent=2, ensure_ascii=False)
    click.echo(f"🧬 Сгенерирован script_commit: {random_commit}")

    # Создаем zip архив
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Добавляем основные файлы проекта
        for item in os.listdir('.'):
            if item in [HISTORY_DIR, '.git']:
                continue
            
            item_path = Path(item)
            if item_path.is_file():
                zipf.write(item, item)
                click.echo(f"📄 Добавлен файл: {item}")
            elif item_path.is_dir() and item not in [HISTORY_DIR, '.git', '__pycache__', '.venv', 'venv']:
                # Добавляем содержимое папки
                for root, dirs, files in os.walk(item):
                    # Исключаем служебные папки
                    dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.venv', 'venv']]
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, '.')
                        zipf.write(file_path, arcname)
        
        # Обязательно добавляем скомпилированный .bin файл
        zipf.write(bin_filename, bin_filename) 
        click.echo(f"🚀 Добавлен артефакт: {bin_filename}")
    
    click.echo(f"🎉 Релиз для версии {version} создан: {archive_path}")
    click.echo(f"📊 Размер архива: {os.path.getsize(archive_path)} байт")

@main.command()
@click.option('--company-id', default=None, help='Company ID для заголовка X-Company-ID')
@click.option('--dry-run', is_flag=True, help='Сформировать JSON и вывести его без отправки')
def push(company_id, dry_run):
    """Опубликовать релиз на сервер rmt-cfg (новый атомарный API).

    - Собирает все данные из текущего релиза (последнего в .gs_history).
    - Формирует единый JSON-запрос.
    - Отправляет его на эндпоинт /scripts/publish.
    """
    config = load_config()
    server_url = config.get('server_url')
    if not server_url:
        raise click.ClickException("server_url не указан в ~/.gs_tool/config.json")

    # company_id может быть передан параметром CLI или храниться в конфиге
    target_company_id = company_id or config.get('company_id')
    if not target_company_id:
        raise click.ClickException(
            'Не указан company_id (используйте --company-id или добавьте в ~/.gs_tool/config.json)'
        )

    # Ищем все архивы релизов (по возрастанию)
    if not os.path.exists(HISTORY_DIR):
        raise click.ClickException(f"Папка {HISTORY_DIR} не найдена. Создайте релиз: gs release")
    
    release_archives = sorted([
        f for f in os.listdir(HISTORY_DIR)
        if f.startswith('release_v') and f.endswith('.zip')
    ])
    if not release_archives:
        raise click.ClickException("Не найдено ни одного релиза в .gs_history")

    success_count = 0
    fail_count = 0
    for archive_name in release_archives:
        archive_path = os.path.join(HISTORY_DIR, archive_name)
        click.echo(f"\n📦 Обработка архива {archive_name}")

        # --- Извлекаем project.json и бинарь ---
        try:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                project_bytes = zf.read(PROJECT_FILE)
                project = json.loads(project_bytes.decode('utf-8'))
                script_id = project.get('script_id')
                if not script_id:
                    click.echo('⚠️  script_id отсутствует, пропускаю архив.')
                    fail_count += 1
                    continue
                try:
                    bin_content = zf.read(script_id)
                except KeyError:
                    click.echo('⚠️  Бинарный файл не найден в архиве, пропускаю архив.')
                    fail_count += 1
                    continue
        except (KeyError, zipfile.BadZipFile) as e:
            click.echo(f'❌ Ошибка чтения архива: {e}')
            fail_count += 1
            continue

        # --- Формируем единый JSON payload ---
        sm = {
            "script_id": project.get("script_id"),
            "name": project.get("project_name") or project.get("name"),
            "description": project.get("description"),
            "is_public": project.get("is_public", False),
        }
        # commit_hash: используем из project.json; если не валиден hex-64 — fallback к SHA256(binary)
        commit_hash = project.get("script_commit")
        if not (isinstance(commit_hash, str) and re.fullmatch(r"^[0-9a-fA-F]{64}$", commit_hash or "")):
            commit_hash = hashlib.sha256(bin_content).hexdigest()
        svm = {
            "version": project.get("version"),
            "commit_hash": commit_hash,
            "descriptor_id": (
                project.get("uuid_ui_descriptor")
                or project.get("descriptor_uuid")
                or (project.get("config") or {}).get("uuid_cfg_descriptor")
            )
        }
        ds = {
            "config": project.get("config", {}),
            "datasources": project.get("datasources", {}),
            "subscriptions": project.get("subscriptions", []),
            "api": project.get("api", {}),
        }

        # Проверяем наличие ключевых полей
        if not all([sm.get('script_id'), svm.get('version'), svm.get('commit_hash'), svm.get('descriptor_id')]):
            click.echo("❌ В project.json отсутствуют обязательные поля (script_id, version, script_commit/sha256, uuid_ui_descriptor). Пропуск.")
            fail_count += 1
            continue

        payload = {
            "script_metadata": sm,
            "script_version_metadata": svm,
            "descriptor_schema": ds,
            "binary_payload": binascii.b2a_base64(bin_content).decode('ascii').strip(),
        }

        if dry_run:
            click.echo("--- Dry Run: JSON Payload ---")
            click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
            continue

        # --- Отправляем запрос ---
        api_key = config.get('api_key')
        headers = {'X-Company-ID': target_company_id, 'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        try:
            url = f"{server_url.rstrip('/')}/scripts/publish"
            resp = requests.post(url, json=payload, headers=headers)

            if resp.status_code in (200, 201):
                data = resp.json()
                status = "создана новая версия" if data.get('is_new') else "версия уже существует"
                click.echo(f"✅ {archive_name}: {status}")
                click.echo(f"  - script_id: {data.get('script_id')}")
                click.echo(f"  - version_id: {data.get('version_id')}")
                success_count += 1
            else:
                click.echo(f"❌ {archive_name}: Ошибка публикации: {resp.status_code}")
                try:
                    click.echo(resp.json())
                except:
                    click.echo(resp.text)
                fail_count += 1

        except requests.exceptions.RequestException as e:
            click.echo(f"❌ {archive_name}: Сетевая ошибка: {e}")
            fail_count += 1

    click.echo(f"\n🎉 Готово! Успешно опубликовано {success_count} релиз(ов), ошибок: {fail_count}.")

@main.group()
def token():
    """Управление application tokens (Personal Access Tokens).

    Доступные подкоманды:
    - create: выпустить новый токен (PAT) и, при желании, сохранить его в конфиг
    - list: показать токены текущего пользователя
    - revoke: отозвать токен по `token_id`
    """
    pass


def _get_auth_headers_for_admin_ops(server_url: str, company_id: Optional[str], prefer_api_key: bool = True,
                                    email: Optional[str] = None, password: Optional[str] = None) -> dict:
    config = load_config()
    headers = {}
    if company_id:
        headers['X-Company-ID'] = company_id
    # Prefer API key (PAT) if present
    if prefer_api_key and config.get('api_key'):
        headers['Authorization'] = f"Bearer {config['api_key']}"
        return headers

    # Otherwise login with email/password to get JWT
    if not email:
        email = click.prompt('Email', type=str)
    if not password:
        password = getpass('Password: ')
    try:
        resp = requests.post(f"{server_url.rstrip('/')}/api/v1/auth/login", json={'email': email, 'password': password})
        if resp.status_code not in (200, 201):
            raise click.ClickException(f"Auth failed: {resp.status_code} {resp.text}")
        access_token = resp.json().get('access_token')
        if not access_token:
            raise click.ClickException('Auth response does not contain access_token')
        headers['Authorization'] = f"Bearer {access_token}"
        return headers
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"Network error during auth: {e}")


@token.command('create')
@click.option('--name', default=None, help='Имя токена (для удобства)')
@click.option('--company-id', default=None, help='Company ID (если не указать — будет интерактивный выбор)')
@click.option('--scope', 'scopes', multiple=True, help='Права токена (по умолчанию захардкожены для CLI).')
@click.option('--never-expires/--expires', default=True, help='Бессрочный токен (по умолчанию включено)')
@click.option('--expires-at', default=None, help='Дата истечения (ISO-8601), если --expires')
@click.option('--email', default=None, help='Email для входа (интерактивно спросим, если не указать)')
@click.option('--password', default=None, help='Пароль для входа (интерактивно спросим, если не указать)')
def token_create(name, company_id, scopes, never_expires, expires_at, email, password):
    """Выпустить токен (PAT) для CLI и опционально сохранить его в конфиг.

    Процесс:
    1) Аутентификация по email/паролю (получение JWT)
    2) Выбор компании (если не указана)
    3) Выпуск токена с указанными scope'ами
    4) Предложение записать токен в `~/.gs_tool/config.json` как `api_key`

    Примеры:
      gs token create --email you@example.com
      gs token create --name ci-bot --scope scripts:write --scope descriptors:write \
        --never-expires --email you@example.com
    """
    config = load_config()
    server_url = config.get('server_url')
    if not server_url:
        raise click.ClickException('server_url не указан в ~/.gs_tool/config.json')

    # Всегда логинимся email/password для выпуска токена
    headers = _get_auth_headers_for_admin_ops(server_url, None, prefer_api_key=False, email=email, password=password)

    # Шаг 1: список компаний
    chosen_company_id = company_id
    if not chosen_company_id:
        try:
            resp = requests.get(f"{server_url.rstrip('/')}/api/v1/companies", headers=headers)
        except requests.exceptions.RequestException as e:
            raise click.ClickException(f"Сетевая ошибка при получении компаний: {e}")
        if resp.status_code != 200:
            raise click.ClickException(f"Не удалось получить список компаний: {resp.status_code} {resp.text}")
        companies = resp.json() or []
        if not companies:
            raise click.ClickException('За вашим пользователем не найдено ни одной компании. Создайте компанию прежде чем выпускать токен.')
        if len(companies) == 1:
            company = companies[0]
            chosen_company_id = company.get('id')
            click.echo(f"Компания: {company.get('name')} ({chosen_company_id})")
        else:
            click.echo('Доступные компании:')
            for idx, comp in enumerate(companies, start=1):
                click.echo(f"  {idx}) {comp.get('name')} [{comp.get('id')}]")
            idx = click.prompt('Выберите номер компании', type=int)
            if idx < 1 or idx > len(companies):
                raise click.ClickException('Неверный номер компании')
            chosen_company_id = companies[idx - 1].get('id')
    
    # Шаг 2: имя токена
    token_name = name or click.prompt('Имя токена', default='gs-cli')

    payload = {
        'name': token_name,
        'company_id': chosen_company_id,
        # Захардкоженные скоупы для операций CLI (публикация дескрипторов и скриптов)
        'scopes': list(scopes) if scopes else ['scripts:write', 'descriptors:write'],
        'never_expires': bool(never_expires),
        'expires_at': expires_at,
    }

    try:
        resp = requests.post(f"{server_url.rstrip('/')}/api/v1/tokens", json=payload, headers=headers)
        if resp.status_code not in (200, 201):
            raise click.ClickException(f"Ошибка создания токена: {resp.status_code} {resp.text}")
        data = resp.json()
        raw = data.get('token')
        if not raw:
            raise click.ClickException('Сервер не вернул поле token')
        click.echo('\n✅ Токен создан:')
        click.echo(f"token_id: {data.get('token_id')}")
        click.echo(f"created_at: {data.get('created_at')}")
        click.echo('\nВНИМАНИЕ! Сохраните токен сейчас, он будет показан один раз:')
        click.echo(raw)

        if click.confirm('\nЗаписать этот токен в ~/.gs_tool/config.json как api_key?'):
            config['api_key'] = raw
            # ensure company_id stored if provided
            if chosen_company_id:
                config['company_id'] = chosen_company_id
            cfg_path = os.path.expanduser('~/.gs_tool/config.json')
            os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            click.echo('✅ Токен сохранен в конфиг.')
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"Сетевая ошибка: {e}")


@token.command('list')
@click.option('--company-id', default=None, help='Company ID заголовок (опционально)')
@click.option('--email', default=None, help='Email для входа, если нет api_key')
@click.option('--password', default=None, help='Пароль для входа, если нет api_key')
def token_list(company_id, email, password):
    """Показать список токенов текущего пользователя.

    Если `api_key` не задан, будет предложен интерактивный вход (email/пароль).
    """
    config = load_config()
    server_url = config.get('server_url')
    if not server_url:
        raise click.ClickException('server_url не указан в ~/.gs_tool/config.json')

    headers = _get_auth_headers_for_admin_ops(server_url, company_id, True, email, password)

    try:
        resp = requests.get(f"{server_url.rstrip('/')}/api/v1/tokens", headers=headers)
        if resp.status_code != 200:
            raise click.ClickException(f"Ошибка: {resp.status_code} {resp.text}")
        items = resp.json()
        if not items:
            click.echo('Нет токенов.')
            return
        for t in items:
            click.echo(f"- token_id={t.get('token_id')} active={t.get('is_active')} created_at={t.get('created_at')} expires_at={t.get('expires_at')}")
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"Сетевая ошибка: {e}")


@token.command('revoke')
@click.argument('token_id')
@click.option('--company-id', default=None, help='Company ID заголовок (опционально)')
@click.option('--email', default=None, help='Email для входа, если нет api_key')
@click.option('--password', default=None, help='Пароль для входа, если нет api_key')
def token_revoke(token_id, company_id, email, password):
    """Отозвать токен по `token_id`.

    Если `api_key` не задан, будет предложен интерактивный вход (email/пароль).
    """
    config = load_config()
    server_url = config.get('server_url')
    if not server_url:
        raise click.ClickException('server_url не указан в ~/.gs_tool/config.json')

    headers = _get_auth_headers_for_admin_ops(server_url, company_id, True, email, password)

    try:
        resp = requests.delete(f"{server_url.rstrip('/')}/api/v1/tokens/{token_id}", headers=headers)
        if resp.status_code not in (200, 204):
            raise click.ClickException(f"Ошибка: {resp.status_code} {resp.text}")
        click.echo('✅ Токен отозван')
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"Сетевая ошибка: {e}")

if __name__ == '__main__':
    main() 