from setuptools import setup, find_packages
import os

# Define o caminho para a pasta do projeto
projeto_path = os.path.dirname(os.path.abspath(__file__))

# Lê o conteúdo do arquivo README.md para usar como descrição longa na PyPI
readme_path = os.path.join(projeto_path, "README.md")
with open(readme_path, "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Lê as dependências do arquivo requirements.txt
requirements_path = os.path.join(projeto_path, "requirements.txt")
with open(requirements_path, "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="csv-parser-utils",
    version="0.0.1",
    author="Thiago Gallo",
    author_email="gallothiago2013@gmail.com",
    description="Um pacote para manipular dados de arquivos CSV, usando pandas.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gallothiago/csv-parser-utils",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)