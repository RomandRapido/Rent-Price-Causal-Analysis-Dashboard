#!/bin/bash

echo "============================================"
echo "  Rent-to-Price Dashboard Setup"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed."
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        exit 1
    fi
    echo "      Virtual environment created successfully."
else
    echo "[1/4] Virtual environment already exists. Skipping..."
fi

# Activate virtual environment
echo "[2/4] Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "[3/4] Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies."
    exit 1
fi
echo "      Dependencies installed successfully."

# Run the dashboard
echo "[4/4] Starting dashboard..."
echo ""
echo "============================================"
echo "  Dashboard is starting..."
echo "  Open your browser to: http://localhost:8501"
echo "  Press Ctrl+C to stop the server"
echo "============================================"
echo ""
streamlit run dashboard.py

# Deactivate on exit
deactivate