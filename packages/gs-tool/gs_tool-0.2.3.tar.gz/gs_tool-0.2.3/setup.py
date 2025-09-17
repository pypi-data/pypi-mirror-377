import os
from setuptools import setup, find_packages

setup(
    name="gs-tool",
    version="0.2.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.1.3',
        'jinja2>=3.1.2',
        'requests>=2.28.1',
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for managing telemetry scripts",
    long_description=open('README.md', encoding='utf-8').read() if os.path.exists('README.md') else '',
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/gs_tool",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'gs=gs_tool.cli:main',
        ],
    },
    package_data={
        'gs_tool': ['templates/*.j2', '*.json', 'templates/*', 'bin/*'],
    },
) 