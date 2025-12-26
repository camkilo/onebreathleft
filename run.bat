@echo off
REM Launcher script for One Breath Left (Windows)

echo ========================================
echo        One Breath Left
echo   A Psychological Survival Game
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is required but not installed.
    pause
    exit /b 1
)

REM Check if pygame is installed
python -c "import pygame" 2>nul
if errorlevel 1 (
    echo Pygame not found. Installing dependencies...
    pip install -r requirements.txt
)

echo Starting game...
echo.
python main.py

echo.
echo Thank you for playing!
pause
