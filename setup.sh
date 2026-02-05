#!/bin/bash

echo "========================================"
echo "Agentic Honeypot - Quick Setup Script"
echo "========================================"
echo ""

echo "[1/4] Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.11 or higher"
    exit 1
fi
echo ""

echo "[2/4] Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo ""

echo "[3/4] Checking environment configuration..."
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env file and add your API keys:"
    echo "  - GOOGLE_API_KEY: Get from https://ai.google.dev"
    echo "  - API_KEY: Choose a secure custom key"
    echo ""
    echo "After editing .env, run this script again."
    exit 0
fi
echo "Environment file found!"
echo ""

echo "[4/4] Starting the application..."
echo ""
echo "The API will be available at: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo "API endpoint: http://localhost:8000/api/honeypot"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
python3 main.py
