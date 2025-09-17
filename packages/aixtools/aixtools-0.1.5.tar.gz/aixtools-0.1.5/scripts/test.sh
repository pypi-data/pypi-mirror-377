#!/bin/bash -eu
set -o pipefail

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

# Install required dependencies
echo "Installing test dependencies..."
uv pip install pytest pytest-asyncio pytest-mock pytest-cov

# Ensure .env exists
touch .env

# Add the project root to PYTHONPATH so imports work correctly
export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH:-}"

# Run all tests using pytest with coverage
echo "Running tests with coverage..."
pytest tests/ -v --cov=aixtools --cov-report=term-missing

# Generate HTML coverage report
# pytest tests/ --cov=aixtools --cov-report=html
