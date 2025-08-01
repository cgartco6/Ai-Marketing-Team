@echo off
REM AI Marketing Team - System Setup Script
REM Version: 1.2.0
REM Description: Configures development environment and dependencies

setlocal enabledelayedexpansion

:: Configuration
set PYTHON_VERSION=3.10.6
set VENV_NAME=ai_team_env
set LOG_FILE=..\logs\setup.log
set REQUIREMENTS=..\requirements.txt
set CONFIG_DIR=..\config
set CONFIG_TEMPLATE=%CONFIG_DIR%\api_keys.ini.template
set CONFIG_FILE=%CONFIG_DIR%\api_keys.ini

:: Initialize logging
if not exist "..\logs" mkdir "..\logs"
echo [%date% %time%] Starting setup > %LOG_FILE%
echo [%date% %time%] Python version: %PYTHON_VERSION% >> %LOG_FILE%

:: Check Python installation
echo Checking Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH >> %LOG_FILE%
    echo Python not found. Please install Python %PYTHON_VERSION% or higher
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Verify Python version
for /f "tokens=2 delims= " %%A in ('python --version 2^>^&1') do set INSTALLED_PYTHON=%%A
echo Installed Python version: %INSTALLED_PYTHON% >> %LOG_FILE%

for /f "tokens=1-3 delims=." %%A in ("%PYTHON_VERSION%") do (
    set MAJOR=%%A
    set MINOR=%%B
    set PATCH=%%C
)

for /f "tokens=1-3 delims=." %%A in ("%INSTALLED_PYTHON%") do (
    set INST_MAJOR=%%A
    set INST_MINOR=%%B
    set INST_PATCH=%%C
)

if %INST_MAJOR% lss %MAJOR% (
    echo [ERROR] Python version too old. Required: %PYTHON_VERSION% >> %LOG_FILE%
    echo Python version %INSTALLED_PYTHON% is too old. Please install %PYTHON_VERSION% or higher
    pause
    exit /b 1
)

if %INST_MAJOR% equ %MAJOR% if %INST_MINOR% lss %MINOR% (
    echo [ERROR] Python version too old. Required: %PYTHON_VERSION% >> %LOG_FILE%
    echo Python version %INSTALLED_PYTHON% is too old. Please install %PYTHON_VERSION% or higher
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv ..\%VENV_NAME% >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment >> %LOG_FILE%
    echo Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate and install dependencies
echo Installing dependencies...
call ..\%VENV_NAME%\Scripts\activate >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment >> %LOG_FILE%
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

python -m pip install --upgrade pip >> %LOG_FILE% 2>&1
pip install -r %REQUIREMENTS% >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements >> %LOG_FILE%
    echo Failed to install Python dependencies
    pause
    exit /b 1
)

:: Setup directory structure
echo Creating directory structure...
mkdir ..\data >> %LOG_FILE% 2>&1
mkdir ..\data\campaigns >> %LOG_FILE% 2>&1
mkdir ..\data\analytics >> %LOG_FILE% 2>&1
mkdir ..\assets >> %LOG_FILE% 2>&1
mkdir ..\assets\templates >> %LOG_FILE% 2>&1
mkdir ..\assets\output >> %LOG_FILE% 2>&1

:: Handle configuration
echo Configuring API keys...
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%" >> %LOG_FILE% 2>&1

if not exist "%CONFIG_FILE%" (
    if exist "%CONFIG_TEMPLATE%" (
        copy "%CONFIG_TEMPLATE%" "%CONFIG_FILE%" >> %LOG_FILE% 2>&1
        echo Created new config file from template. Please edit: %CONFIG_FILE%
    ) else (
        echo [WARNING] Config template not found at %CONFIG_TEMPLATE% >> %LOG_FILE%
        echo Warning: API key template not found. You'll need to create config manually
    )
) else (
    echo Config file already exists at %CONFIG_FILE%
)

:: Generate encryption key if needed
echo Generating encryption keys...
python -c "from cryptography.fernet import Fernet; print(f'\nFERNET_KEY={Fernet.generate_key().decode()}')" >> %CONFIG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Failed to generate Fernet key >> %LOG_FILE%
    echo Warning: Failed to generate encryption key
)

:: Validate setup
echo Verifying setup...
python -c "from core.utils import validate_config; exit(0 if validate_config() else 1)" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Configuration validation failed >> %LOG_FILE%
    echo Error: Configuration validation failed. Check %CONFIG_FILE%
    pause
    exit /b 1
)

:: Finalize
echo Setup completed successfully!
echo [%date% %time%] Setup completed successfully >> %LOG_FILE%

echo.
echo Virtual environment: ..\%VENV_NAME%
echo To activate run:
echo    scripts\activate.bat
echo.
echo To start the system:
echo    python main.py
echo.

pause
exit /b 0
