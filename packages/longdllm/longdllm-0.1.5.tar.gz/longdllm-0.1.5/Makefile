.PHONY: help install install-dev test lint format clean build upload test-upload

help:
	@echo "LongDLLM Development Commands"
	@echo "============================="
	@echo "install       Install package in normal mode"
	@echo "install-dev   Install package in development mode with dev dependencies"
	@echo "test          Run tests with pytest"
	@echo "lint          Run linting with flake8"
	@echo "format        Format code with black and isort"
	@echo "type-check    Run type checking with mypy"
	@echo "clean         Clean build artifacts"
	@echo "build         Build distribution packages"
	@echo "upload        Upload to PyPI (requires credentials)"
	@echo "test-upload   Upload to TestPyPI for testing"
	@echo "check-package Test package structure without dependencies"

install:
	pip install .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	flake8 longdllm/ tests/ examples/

format:
	black longdllm/ tests/ examples/
	isort longdllm/ tests/ examples/

type-check:
	mypy longdllm/

check-package:
	python test_package.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	twine upload dist/*

test-upload: build
	twine upload --repository testpypi dist/*

all-checks: format lint type-check test
	@echo "All checks completed!"
