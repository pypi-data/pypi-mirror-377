#!/usr/bin/env python3
"""
Setup script for OpenIDE Python library
"""

from setuptools import setup, find_packages
import os

# Читаем README
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Читаем requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="openide-client",
    version="1.0.0",
    author="ArtemJS",
    author_email="artemjs@example.com",
    description="Python client library for OpenIDE container system",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/artemjs/OpenIDE",
    project_urls={
        "Bug Tracker": "https://github.com/artemjs/OpenIDE/issues",
        "Documentation": "https://github.com/artemjs/OpenIDE/tree/v1",
        "Source Code": "https://github.com/artemjs/OpenIDE/tree/v1",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Build Tools",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "openide-client=openide_client:main",
        ],
    },
    keywords="docker, containers, virtualization, development, api, client",
    include_package_data=True,
    zip_safe=False,
)
