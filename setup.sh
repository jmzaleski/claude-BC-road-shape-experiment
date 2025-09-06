#!/bin/bash

# BC FSR Road Merger - Virtual Environment Setup Script
# Run this script to set up the Python environment and dependencies

echo "BC FSR Road Merger Setup"
echo "========================"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or later and try again"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    echo "Make sure python3-venv is installed:"
    echo "  Ubuntu/Debian: sudo apt install python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3-venv"
    exit 1
fi

echo "✓ Virtual environment created in ./venv"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing Python packages..."
echo "This may take a few minutes as GeoPandas has many dependencies..."
echo ""

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to install requirements"
    echo "This often happens due to missing system dependencies for GeoPandas"
    echo ""
    echo "On Ubuntu/Debian, try installing these first:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install gdal-bin libgdal-dev libproj-dev libgeos-dev"
    echo ""
    echo "On macOS with Homebrew:"
    echo "  brew install gdal proj geos"
    echo ""
    echo "Then run this setup script again."
    exit 1
fi

echo ""
echo "✓ All packages installed successfully!"
echo ""

# Check if the main script exists
if [ -f "claude.py" ]; then
    echo "✓ Found claude.py"
else
    echo "⚠ claude.py not found - make sure you've copied the main script"
fi

# Check if data file exists
if [ -f "bc_roads.geojson" ]; then
    echo "✓ Found bc_roads.geojson"
else
    echo "⚠ bc_roads.geojson not found - you'll need to download BC road data"
fi

echo ""
echo "Setup complete! To use the FSR merger:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the script:"
echo "   python claude.py"
echo ""
echo "3. When done, deactivate the environment:"
echo "   deactivate"
echo ""

# Test the installation
echo "Testing installation..."
python -c "import geopandas; print('✓ GeoPandas import successful')" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Installation test passed"
    echo ""
    echo "Ready to process FSR data!"
else
    echo "✗ Installation test failed"
    echo "There may be an issue with the GeoPandas installation"
fi
