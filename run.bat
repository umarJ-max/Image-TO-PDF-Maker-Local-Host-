@echo off
title Image to PDF Converter

echo.
echo  ================================
echo   Image to PDF  --  Local Tool
echo  ================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install from python.org
    pause
    exit /b 1
)

echo  Checking dependencies...

python -m pip show img2pdf >nul 2>&1
if errorlevel 1 (
    echo  Installing img2pdf...
    python -m pip install img2pdf -q
)

python -m pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo  Installing Pillow...
    python -m pip install Pillow -q
)

python -m pip show flask >nul 2>&1
if errorlevel 1 (
    echo  Installing Flask...
    python -m pip install flask -q
)

echo  All dependencies ready.
echo.
echo  Starting server on http://localhost:5050
echo  Browser will open automatically.
echo.
echo  !! Close this window to stop the server !!
echo.

python app.py

pause
