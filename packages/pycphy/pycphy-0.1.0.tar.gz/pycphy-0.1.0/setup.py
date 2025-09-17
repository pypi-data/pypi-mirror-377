#!/usr/bin/env python3
"""
Setup script for pycphy package.

Author: Sanjeev Bashyal
Location: https://github.com/SanjeevBashyal/pycphy
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Python: Computational Physics"

# Read requirements if they exist
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="pycphy",
    version="0.1.0",
    author="Sanjeev Bashyal",
    author_email="sanjeev.bashyal@example.com",  # Update with actual email
    description="Python: Computational Physics - Tools for physics dynamics simulation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/SanjeevBashyal/pycphy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    entry_points={
        "console_scripts": [
            "pycphy-foam=pycphy.foamCaseDeveloper.main:main",
        ],
    },
    keywords="computational physics, simulation, openfoam, cfd, physics",
    project_urls={
        "Bug Reports": "https://github.com/SanjeevBashyal/pycphy/issues",
        "Source": "https://github.com/SanjeevBashyal/pycphy",
        "Documentation": "https://github.com/SanjeevBashyal/pycphy#readme",
    },
)
