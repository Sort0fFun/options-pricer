#!/bin/bash
# Startup script for NSE Options Pricer Flask app

echo "========================================"
echo "NSE Options Pricer - Flask Edition"
echo "========================================"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please create one with: python -m venv venv"
    exit 1
fi

# Activate venv and set environment variables
export FLASK_ENV=development
export FLASK_PORT=5001

echo ""
echo "Starting Flask app on port 5001..."
echo "Once started, visit: http://localhost:5001"
echo ""
echo "Press CTRL+C to stop the server"
echo "----------------------------------------"
echo ""

# Use venv Python
venv/bin/python flask_app.py
