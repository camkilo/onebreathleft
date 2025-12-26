#!/bin/bash
# Launcher script for One Breath Left

echo "========================================"
echo "       One Breath Left"
echo "  A Psychological Survival Game"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pygame is installed
python3 -c "import pygame" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Pygame not found. Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "Starting game..."
echo ""
python3 main.py

echo ""
echo "Thank you for playing!"
