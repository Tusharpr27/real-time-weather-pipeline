#!/bin/bash

echo "======================================"
echo "Real-Time Weather Pipeline Setup"
echo "======================================"
echo ""

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To activate virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the application, run:"
echo "  python main.py"
echo ""
echo "API will be available at:"
echo "  http://localhost:8000"
echo ""
echo "API Documentation:"
echo "  http://localhost:8000/docs"
