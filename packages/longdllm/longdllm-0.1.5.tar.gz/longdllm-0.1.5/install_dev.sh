#!/bin/bash
"""
Development setup script for LongDLLM.
"""

set -e  # Exit on any error

echo "LongDLLM Development Setup"
echo "=========================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Check if in conda environment
if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
    echo "Conda environment: $CONDA_DEFAULT_ENV"
else
    echo "No conda environment detected"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install package in development mode
echo ""
echo "Installing package in development mode..."
pip install -e .

# Run tests
echo ""
echo "Running package tests..."
python quick_test.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "You can now use:"
echo "  from longdllm import adapt_for_long_context"
echo ""
echo "Example usage:"
echo "  model = AutoModel.from_pretrained('apple/DiffuCoder-7B-Instruct')"
echo "  model = adapt_for_long_context(model, rescale_factors='factors.txt')"
