# LongDLLM Package Structure

This directory contains the complete PyPI package for LongDLLM - a plug-and-play solution for adapting diffusion language models to support long-context inputs.

## Package Structure

```
longdllm/
├── longdllm/                 # Main package directory
│   ├── __init__.py          # Package initialization and exports
│   ├── core.py              # Core adaptation functionality
│   ├── rope_classes.py      # RoPE embedding implementations
│   ├── utils.py             # Utility functions
│   └── data/                # Data files
│       ├── diffucoder_rescale_factors.csv  # Optimized factors for DiffuCoder
│       ├── llada_rescale_factors.csv       # Optimized factors for LLaDA
│       └── example_rescale_factors.txt     # Example/legacy factors
├── examples/                # Usage examples
│   ├── basic_usage.py       # Basic DiffuCoder example
│   ├── llada_example.py     # LLaDA-specific example
│   └── complete_example.py  # Comprehensive demonstration
├── tests/                   # Test suite
│   ├── __init__.py
│   └── test_longdllm.py     # Main test cases
├── setup.py                 # Legacy setup script
├── pyproject.toml           # Modern Python packaging
├── requirements.txt         # Dependencies
├── README.md                # Package documentation
├── LICENSE                  # MIT license
├── CONTRIBUTING.md          # Contribution guidelines
├── .gitignore              # Git ignore rules
├── MANIFEST.in             # Package data inclusion
├── Makefile                # Development commands
└── test_package.py         # Package structure validator
```

## Key Features

1. **Minimal Interface**: Single function call to adapt models
2. **Auto-Detection**: Automatically detects model architecture
3. **Multiple Methods**: Support for LongRoPE, YaRN, NTK scaling
4. **Memory Efficient**: In-place modification with optional FP32 mode
5. **Type Hints**: Full type annotation support
6. **Testing**: Comprehensive test suite

## Main Interface

```python
from longdllm import adapt_for_long_context

# Load your model normally
model = AutoModel.from_pretrained("apple/DiffuCoder-7B-Instruct")

# Adapt for long context (modifies in-place, returns for chaining)
model = adapt_for_long_context(model, rescale_factors='factors.txt')

# Use adapted model
output = model.diffusion_generate(...)
```

## Development Commands

- `make install-dev` - Install in development mode
- `make test` - Run test suite  
- `make format` - Format code with black/isort
- `make lint` - Run linting
- `make build` - Build distribution packages
- `make check-package` - Validate package structure

## Next Steps

1. **Add Real Rescale Factors**: Replace example factors with optimized values
2. **Test with Actual Models**: Validate with real DiffuCoder/LLaDA models  
3. **Documentation**: Add sphinx docs for API reference
4. **CI/CD**: Set up GitHub Actions for automated testing
5. **Benchmarks**: Add performance benchmarks
6. **PyPI Upload**: Publish to PyPI when ready

## Usage Examples

The package supports both officially supported models:

- **apple/DiffuCoder-7B-Instruct**: Code generation diffusion model
- **GSAI-ML/LLaDA-8B-Instruct**: Language diffusion model

Each model has specific generation patterns, but the adaptation interface is identical.
