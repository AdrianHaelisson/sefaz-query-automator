"""
Setup script para o Sistema de Consulta SEFAZ
"""
from setuptools import setup, find_packages
import os

# Lê o README para descrição longa
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Lê os requisitos
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sefaz-query-automator",
    version="1.0.0",
    author="Adrian Haelisson",
    author_email="",
    description="Sistema automatizado para consulta e solicitação de arquivos XML no portal SEFAZ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdrianHaelisson/sefaz-query-automator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: Portuguese (Brazilian)",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sefaz-query-automator=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "env.example"],
    },
    keywords="sefaz, xml, automation, selenium, fiscal, contabilidade",
    project_urls={
        "Bug Reports": "https://github.com/AdrianHaelisson/sefaz-query-automator/issues",
        "Source": "https://github.com/AdrianHaelisson/sefaz-query-automator",
    },
)
