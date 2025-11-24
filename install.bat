@echo off
echo Setting up StemWaves environment...
cd /d "%~dp0"

REM Install Python 3.10 if needed
python --version | findstr /C:"3.10" >nul
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python 3.10 is required.
    echo Please install Python 3.10 from python.org before running this script.
    pause
    exit /b
)

echo Creating virtual environment...
python -m venv .venv

echo Activating environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Installation complete!
pause
