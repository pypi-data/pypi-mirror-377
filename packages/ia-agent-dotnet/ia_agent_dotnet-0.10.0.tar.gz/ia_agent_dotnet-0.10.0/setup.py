#!/usr/bin/env python3
"""
Setup script para IA Agent
IA Agent para Generación de Pruebas Unitarias .NET
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Leer requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#') and not line.startswith('==')
        ]

setup(
    name="ia-agent-dotnet",
    version="0.10.0",
    author="Paulo Andrade",
    author_email="paulo_866@hotmail.com",
    description="IA Agent para Generación de Pruebas Unitarias .NET - Sistema multi-agente inteligente",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lopand-Solutions/ia-agent-to-unit-test-api-rest",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ia-agent=cli.main:main",
            "ia-agent-config=cli.config_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md", "*.txt"],
    },
    keywords=[
        "ai", "agent", "dotnet", "testing", "unit-tests", 
        "langchain", "openai", "deepseek", "gemini", 
        "automation", "code-generation"
    ],
    project_urls={
        "Bug Reports": "https://github.com/Lopand-Solutions/ia-agent-to-unit-test-api-rest/issues",
        "Source": "https://github.com/Lopand-Solutions/ia-agent-to-unit-test-api-rest",
        "Documentation": "https://github.com/Lopand-Solutions/ia-agent-to-unit-test-api-rest/blob/develop/docs/USER_GUIDE.md",
    },
)
