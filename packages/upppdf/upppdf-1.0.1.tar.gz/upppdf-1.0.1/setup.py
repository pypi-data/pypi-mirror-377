#!/usr/bin/env python3
"""
Setup script for upppdf - unlock password protected PDF
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="upppdf",
    version="1.0.1",
    author="Abozar Alizadeh",
    author_email="abozar.alizadeh@gmail.com",
    description="Unlock password protected PDF files using multiple methods",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/abozar/PDF_Unlocker",
    packages=find_packages(),
    py_modules=["pdf_unlocker"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "upppdf=upppdf.pdf_unlocker:main",
        ],
    },
    keywords="pdf, unlock, password, decrypt, security",
    project_urls={
        "Bug Reports": "https://github.com/abozar/PDF_Unlocker/issues",
        "Source": "https://github.com/abozar/PDF_Unlocker",
        "Documentation": "https://github.com/abozar/PDF_Unlocker#readme",
    },
)
