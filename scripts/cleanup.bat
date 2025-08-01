@echo off
REM AI Marketing Team - System Cleanup Script
REM Version: 1.1.0
REM Description: Cleans temporary files, cache, and resets development environment

setlocal enabledelayedexpansion

:: Configuration
set LOG_FILE=..\logs\cleanup.log
set VENV_NAME=ai_team_env
set DAYS_TO_KEEP=7

:: Initialize logging
echo [%date% %time%] Starting cleanup > %LOG_FILE%

:: Display header
echo.
echo #############################################
echo #   AI Marketing Team - System Cleanup      #
echo #############################################
echo.

:: Clean log files
echo Cleaning log files...
forfiles /P "..\logs" /M *.log /D -%DAYS_TO_KEEP% /C "cmd /c echo Deleting @file >> %LOG_FILE% && del @file" >> %LOG_FILE% 2>&1

:: Clean temporary analytics data
echo Cleaning temporary analytics data...
if exist "..\data\analytics\temp" (
    rmdir /s /q "..\data\analytics\temp" >> %LOG_FILE% 2>&1
    mkdir "..\data\analytics\temp" >> %LOG_FILE% 2>&1
)

:: Clean generated assets
echo Cleaning generated assets...
if exist "..\assets\output\temp" (
    rmdir /s /q "..\assets\output\temp" >> %LOG_FILE% 2>&1
    mkdir "..\assets\output\temp" >> %LOG_FILE% 2>&1
)

:: Clean Python cache files
echo Cleaning Python cache...
for /r ..\ %%d in (__pycache__) do (
    if exist "%%d" (
        echo Cleaning %%d >> %LOG_FILE%
        rmdir /s /q "%%d" >> %LOG_FILE% 2>&1
    )
)
del /s /q ..\*.pyc >> %LOG_FILE% 2>&1
del /s /q ..\*.pyo >> %LOG_FILE% 2>&1
del /s /q ..\*.pyd >> %LOG_FILE% 2>&1

:: Clean virtual environment (optional)
echo.
set /p CLEAN_VENV="Clean virtual environment? (y/n) "
if /i "!CLEAN_VENV!"=="y" (
    echo Cleaning virtual environment... >> %LOG_FILE%
    if exist "..\%VENV_NAME%" (
        rmdir /s /q "..\%VENV_NAME%" >> %LOG_FILE% 2>&1
        echo Virtual environment removed. Run setup.bat to recreate.
    ) else (
        echo Virtual environment not found >> %LOG_FILE%
    )
)

:: Clean temp files
echo Cleaning system temp files...
del /q /f %temp%\*.* >> %LOG_FILE% 2>&1

:: Finalize
echo.
echo Cleanup completed successfully!
echo [%date% %time%] Cleanup completed successfully >> %LOG_FILE%

echo.
echo Summary of actions:
type %LOG_FILE% | find /i "Deleting" 
type %LOG_FILE% | find /i "Cleaning"
echo.
echo Full details in: %LOG_FILE%
echo.

pause
exit /b 0
