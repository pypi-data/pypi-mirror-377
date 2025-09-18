# Building and Publishing FileOrganizer to PyPI

This document provides step-by-step instructions for building and publishing the FileOrganizer package to PyPI.

## Prerequisites

Make sure you have the following installed:

```bash
pip install build twine pytest
```

## Testing the Package

Before building and publishing, run the tests to ensure everything works:

```bash
# From the root directory of the project
pytest
```

Or with coverage:

```bash
pytest --cov=fileorganizer
```

## Building the Package

To build the package, run the following command from the project root:

```bash
# Using the build module (recommended)
python -m build

# Alternatively, using setuptools directly
python setup.py sdist bdist_wheel
```

This will create a `dist` directory containing source archives and wheel files.

## Checking the Package

Before uploading, it's a good idea to check your package:

```bash
twine check dist/*
```

## Publishing to TestPyPI (Optional)

It's good practice to test your package on TestPyPI before publishing to the real PyPI:

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

You can then install your package from TestPyPI to test it:

```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps fileorganizer
```

## Publishing to PyPI

When you're ready to publish to the real PyPI:

```bash
twine upload dist/*
```

You'll be prompted for your PyPI username and password.

## Using API Tokens (Recommended)

For more secure authentication, use API tokens instead of your password:

1. Go to your PyPI account settings
2. Create a new API token with appropriate permissions
3. Use the token as your password when uploading with twine

## Installing the Published Package

After publishing, you can install your package with pip:

```bash
pip install fileorganizer
```

## Development Installation

For development purposes, you can install the package in editable mode:

```bash
pip install -e .
```

## Example CLI Usage

After installation:

```bash
# Organize files in a directory
fileorganizer organize /path/to/messy/directory

# With verbose output
fileorganizer organize /path/to/messy/directory --verbose

# Undo the last operation
fileorganizer undo /path/to/organized/directory
```