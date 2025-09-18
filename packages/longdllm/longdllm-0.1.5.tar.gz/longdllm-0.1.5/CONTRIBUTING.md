# Contributing to LongDLLM

Thank you for your interest in contributing to LongDLLM! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/longdllm.git
cd longdllm
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking

Run all checks:
```bash
black longdllm/ tests/ examples/
isort longdllm/ tests/ examples/
flake8 longdllm/ tests/ examples/
mypy longdllm/
```

## Testing

Run tests with pytest:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest --cov=longdllm tests/
```

## Adding New Features

1. **Model Support**: To add support for new models, update the `SUPPORTED_MODELS` dict in `core.py` and add detection logic in `_detect_model_architecture`.

2. **RoPE Methods**: To add new RoPE scaling methods, create a new class in `rope_classes.py` and add it to the method selection in `adapt_for_long_context`.

3. **Tests**: All new features should include comprehensive tests.

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and ensure all tests pass
6. Run code quality checks
7. Commit your changes with clear, descriptive messages
8. Push to your fork and submit a pull request

## Issues

When reporting issues, please include:

- Python version
- PyTorch version
- Transformers version
- Model being used
- Full error traceback
- Minimal code to reproduce the issue

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming environment for all contributors.

## Questions?

Feel free to open an issue for questions about contributing or using the library.
