#!/usr/bin/env python3
"""
Lsetup(
    name="longdllm",
    version="0.1.3",
    author="Albert Ge",LLM: Plug-and-play long context adaptation for diffusion language models.

Supports Apple DiffuCoder and GSAI-ML LLaDA models.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    """Read and return the contents of the README file."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    """Read and return the contents of requirements.txt."""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="longdllm",
    version="0.1.3",
    author="Albert Ge",
    author_email="lbertge@gmail.com",
    description="Plug-and-play long context adaptation for diffusion language models",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/lbertge/longdllm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    include_package_data=True,
    package_data={
        "longdllm": ["data/*.txt", "data/*.csv"],
    },
    keywords="transformer, long-context, rope, diffusion, language-model, llm",
    project_urls={
        "Bug Reports": "https://github.com/lbertge/longdllm/issues",
        "Source": "https://github.com/lbertge/longdllm",
        "Documentation": "https://github.com/lbertge/longdllm#readme",
    },
)
