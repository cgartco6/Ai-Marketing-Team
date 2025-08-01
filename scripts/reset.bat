@echo off
REM AI Marketing Team - Full System Reset Script
REM Version: 2.1.0
REM Description: Resets the entire system to clean state while preserving critical configurations
REM WARNING: This will delete all generated data and campaigns

setlocal enabledelayedexpansion

:: Configuration
set LOG_FILE=..\logs\reset.log
set VENV_NAME=ai_team_env
set CONFIG_DIR=..\config
set CONFIG_FILE=%CONFIG_DIR%\api_keys.ini
set SAFE_FILE_PATTERNS=*.ini *.config *.json *.xml

:: Initialize logging
if not exist "..\logs" mkdir "..\logs"
echo [%date% %time%] Starting system reset > %LOG_FILE%

:: Display warning
echo.
echo #############################################
echo #  WARNING: FULL SYSTEM RESET               #
echo #############################################
echo.
echo This will perform the following actions:
echo - Remove all generated campaign data
echo - Clear analytics databases
echo - Delete all temporary assets
echo - Clean Python cache files
echo - Optionally remove virtual environment
echo.
echo Configuration files and API keys will be preserved.
echo.

:: Confirmation
set /p CONFIRM="Are you sure you want to continue? (type YES to confirm): "
if /i not "!CONFIRM!"=="YES" (
    echo Reset cancelled by user >> %LOG_FILE%
    echo.
    echo Reset cancelled.
    pause
    exit /b 0
)

:: Step 1: Backup critical config files
echo Backing up configuration files... >> %LOG_FILE%
if not exist "..\backups" mkdir "..\backups"
set BACKUP_DIR=..\backups\backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%
mkdir "!BACKUP_DIR!" >> %LOG_FILE% 2>&1

for /r %CONFIG_DIR% %%f in (%SAFE_FILE_PATTERNS%) do (
    if exist "%%f" (
        echo Backing up %%f >> %LOG_FILE%
        copy "%%f" "!BACKUP_DIR!" >> %LOG_FILE% 2>&1
    )
)

:: Step 2: Clean data directories
echo Cleaning data directories... >> %LOG_FILE%
for %%d in (
    "..\data\campaigns"
    "..\data\analytics"
    "..\assets\output"
) do (
    if exist %%~d (
        echo Cleaning %%~d >> %LOG_FILE%
        rmdir /s /q %%~d >> %LOG_FILE% 2>&1
        mkdir %%~d >> %LOG_FILE% 2>&1
    )
)

:: Step 3: Remove Python cache
echo Cleaning Python cache... >> %LOG_FILE%
for /r ..\ %%d in (__pycache__) do (
    if exist "%%d" (
        echo Removing %%d >> %LOG_FILE%
        rmdir /s /q "%%d" >> %LOG_FILE% 2>&1
    )
)
del /s /q ..\*.pyc >> %LOG_FILE% 2>&1
del /s /q ..\*.pyo >> %LOG_FILE% 2>&1
del /s /q ..\*.pyd >> %LOG_FILE% 2>&1

:: Step 4: Optional virtual environment reset
echo.
set /p RESET_VENV="Reset virtual environment? (y/n): "
if /i "!RESET_VENV!"=="y" (
    echo Resetting virtual environment... >> %LOG_FILE%
    if exist "..\%VENV_NAME%" (
        rmdir /s /q "..\%VENV_NAME%" >> %LOG_FILE% 2>&1
        echo Virtual environment removed. Run setup.bat to recreate.
    ) else (
        echo Virtual environment not found >> %LOG_FILE%
    )
)

:: Step 5: Reinitialize directory structure
echo Recreating directory structure... >> %LOG_FILE%
mkdir "..\data\campaigns" >> %LOG_FILE% 2>&1
mkdir "..\data\analytics" >> %LOG_FILE% 2>&1
mkdir "..\data\analytics\temp" >> %LOG_FILE% 2>&1
mkdir "..\assets\output" >> %LOG_FILE% 2>&1
mkdir "..\assets\output\temp" >> %LOG_FILE% 2>&1

:: Step 6: System temp files
echo Cleaning system temp files... >> %LOG_FILE%
del /q /f %temp%\*.* >> %LOG_FILE% 2>&1

:: Finalize
echo.
echo System reset completed successfully!
echo Backup saved to: !BACKUP_DIR!
echo [%date% %time%] Reset completed successfully >> %LOG_FILE%

echo.
echo Summary of actions:
type %LOG_FILE% | find /i "Cleaning"
type %LOG_FILE% | find /i "Removing"
type %LOG_FILE% | find /i "Backing"
echo.
echo Full details in: %LOG_FILE%
echo.

pause
exit /b 0
