#!/usr/bin/env python
"""Setup script for PolyPrime - The Multi-Paradigm Programming Language"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="polyprime",
    version="0.1.0",
    author="Michael Benjamin Crowe",
    author_email="michael@crowelogic.com",
    description="A multi-paradigm programming language that compiles to Python, JavaScript, and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichaelCrowe11/polyprime",
    packages=find_packages(include=["polyprime", "polyprime.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "polyprime=polyprime.cli:main",
            "pp=polyprime.cli:main",
        ],
    },
    keywords="programming-language compiler polyglot code-generator multi-paradigm",
    project_urls={
        "Bug Reports": "https://github.com/MichaelCrowe11/polyprime/issues",
        "Source": "https://github.com/MichaelCrowe11/polyprime",
    },
)