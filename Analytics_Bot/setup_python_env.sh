#!/bin/bash

echo "Checking Python 3.13 installation..."

PYTHON_VERSION=$(python3 --version 2>/dev/null)

if [[ $PYTHON_VERSION == *"3.13"* ]]; then
    echo "Python 3.13 already installed"
else
    echo "Python 3.13 not found. Installing via Homebrew..."

    # Check Homebrew
    if ! command -v brew >/dev/null 2>&1; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    # Remove older Python versions
    echo "🧹 Removing old Python versions..."
    brew uninstall --force python python@3.12 python@3.11 python@3.10 python@3.9 2>/dev/null

    # Install python 3.13
    brew install python@3.13
    brew link python@3.13 --force
fi

echo "Current Python version: $(python3 --version)"

echo "Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
else
    echo "venv already exists"
fi

echo "Activating venv..."
source venv/bin/activate

echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo " Opening VS Code..."
code .
