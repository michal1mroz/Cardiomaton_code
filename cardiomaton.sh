#!/bin/bash

set -e  # Exit on error

echo "============================================"
echo " Cardiomaton Application Launcher"
echo "============================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed!"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Found Python version: $python_version"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add Poetry to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"
    
    # Also try to source profile if exists
    if [ -f ~/.profile ]; then
        source ~/.profile
    fi
    
    # Verify installation
    if ! command -v poetry &> /dev/null; then
        echo "ERROR: Poetry installation failed!"
        echo "Please install manually: https://python-poetry.org/docs/#installation"
        exit 1
    fi
fi

echo ""
echo "Step 1: Installing dependencies..."
poetry install --no-root --with dev

echo ""
echo "Step 2: Building Cython extensions..."
poetry run build

echo ""
echo "Step 3: Entering Poetry environment..."
eval $(poetry env activate)

echo ""
echo "Step 4: Starting Cardiomaton..."
echo ""
cd cardiomaton_code
python main_with_front.py

echo ""
echo "Application closed."