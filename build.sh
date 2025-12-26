#!/usr/bin/env bash
# Build script for deploying with pygame support
# Installs SDL2 system dependencies before installing Python packages

set -e  # Exit on error

echo "Installing SDL2 dependencies..."
apt-get update
apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"
