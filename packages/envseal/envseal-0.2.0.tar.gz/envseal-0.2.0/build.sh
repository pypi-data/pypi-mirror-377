#!/bin/bash

# Build script for envseal Python package
# Excludes docs/header.png from the build

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Make sure you're in the project root directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_error "Virtual environment (.venv) not found. Please create it first with: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Verify we're using the virtual environment
if [ "$VIRTUAL_ENV" != "$(pwd)/.venv" ]; then
    print_warning "Virtual environment activation may have failed. Current VIRTUAL_ENV: $VIRTUAL_ENV"
fi

print_status "Using Python: $(which python)"
print_status "Python version: $(python --version)"
print_status "Starting build process for envseal package..."

# Clean previous builds
print_status "Cleaning previous build artifacts..."
rm -rf dist/ build/ *.egg-info/

# Create temporary MANIFEST.in to exclude docs/header.png
print_status "Creating temporary MANIFEST.in to exclude docs/header.png..."
cat > MANIFEST.in << 'EOF'
include README.md
include LICENSE
recursive-include src/envseal *.py
global-exclude docs/header.png
global-exclude *.pyc
global-exclude __pycache__
EOF

# Install/upgrade build dependencies
print_status "Installing/upgrading build dependencies..."
python -m pip install --upgrade pip build wheel

# Build the package
print_status "Building source distribution and wheel..."
python -m build

# Clean up temporary MANIFEST.in
print_status "Cleaning up temporary files..."
rm -f MANIFEST.in

# Verify the build
print_status "Verifying build contents..."
if command -v unzip >/dev/null 2>&1; then
    # Check wheel contents
    WHEEL_FILE=$(find dist/ -name "*.whl" | head -n 1)
    if [ -n "$WHEEL_FILE" ]; then
        print_status "Checking wheel contents for excluded files..."
        if unzip -l "$WHEEL_FILE" | grep -q "docs/header.png"; then
            print_warning "docs/header.png found in wheel - exclusion may not have worked properly"
        else
            print_success "docs/header.png successfully excluded from wheel"
        fi
    fi
fi

# List built files
print_status "Built files:"
ls -la dist/

print_success "Build completed successfully!"
print_status "You can now upload to PyPI with: python -m twine upload dist/*"