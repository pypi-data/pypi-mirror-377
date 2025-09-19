#!/usr/bin/env python
"""Setup script for vacancy-predictor package."""
from setuptools import setup, find_packages
from pathlib import Path
import os

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="FreeDynamics-simaf",
    version='2.0.6',  # Increment version
    author="Eduardo Bringa, Santiago Bergamin",
    author_email="santiagobergamin@gmail.com",
    description="A comprehensive ML tool for vacancy prediction with GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/vacancy-predictor",
    project_urls={
        "Bug Tracker": "https://github.com/tuusuario/vacancy-predictor/issues",
        "Documentation": "https://vacancy-predictor.readthedocs.io",
        "Source Code": "https://github.com/tuusuario/vacancy-predictor",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "click>=8.0.0",
        "openpyxl>=3.0.7",
        "xlrd>=2.0.1",
        "joblib>=1.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            # CORREGIDO: Apunta al módulo correcto
            "vacancy-predictor=vacancy_predictor.main:main",
            "freedy=vacancy_predictor.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "machine-learning",
        "vacancy",
        "prediction",
        "gui",
        "data-science",
        "artificial-intelligence",
        "scikit-learn",
        "pandas",
        "visualization"
    ],
)