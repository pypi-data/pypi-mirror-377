#!/bin/bash
set -euo pipefail

# Assumes the src contains a single package to be built
PACKAGE_PATH=$(find src/* -type d -not -path "src/__*" | head -n 1)
PACKAGE_NAME=${PACKAGE_PATH#src/}
echo "Using package path: $PACKAGE_PATH"
echo "Using package name: $PACKAGE_NAME"

# Install development dependencies with pip
pip install .[dev]

# Run formatting checks
echo "Running ruff"
ruff check

echo "Running pylint"
pylint src tests

# Run tests and generate coverage reports
echo "Running pytest"
pytest --cov="$PACKAGE_NAME" \
  -n auto \
  --cov-report term \
  --cov-report html \
  --cov-fail-under=100.00 \
   -o log_cli=true \
   --log-cli-level=INFO

# Check the build
python -m build
twine check --strict dist/*
