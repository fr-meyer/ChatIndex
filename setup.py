"""
Setup script for ICTree package.

This file exists for backward compatibility with older pip versions.
Modern installations should use pyproject.toml.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ictree",
    version="0.1.2",
    description="Incremental Context Tree for hierarchical conversation management",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="ChatIndex contributors",
    url="https://github.com/fr-meyer/ChatIndex",
    project_urls={
        "Documentation": "https://github.com/fr-meyer/ChatIndex#readme",
        "Source": "https://github.com/fr-meyer/ChatIndex",
        "Tracker": "https://github.com/fr-meyer/ChatIndex/issues",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*", "docs", "docs.*"]),
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt") if os.path.exists("requirements-dev.txt") else [],
        "docs": read_requirements("requirements-docs.txt") if os.path.exists("requirements-docs.txt") else [],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="conversation tree nlp context topic-modeling chatbot llm",
    include_package_data=True,
    zip_safe=False,
)
