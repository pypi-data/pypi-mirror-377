#!/bin/bash
"""
Build and package LongDLLM for distribution.
"""

set -e

echo "Building LongDLLM Package"
echo "========================"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Install build dependencies
echo "Installing build dependencies..."
pip install build twine

# Build the package
echo "Building package..."
python -m build

# Check the built package
echo "Checking package..."
twine check dist/*

echo ""
echo "✅ Package built successfully!"
echo ""
echo "Files created:"
ls -la dist/

echo ""
echo "To upload to PyPI:"
echo "  Test PyPI: twine upload --repository testpypi dist/*"
echo "  Real PyPI: twine upload dist/*"
echo ""
echo "To install locally:"
echo "  pip install dist/*.whl"
