@echo off
REM Go to the folder where this script lives
cd /d "%~dp0"

REM Check that the venv exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at .venv\Scripts\activate.bat
    echo Run install.bat first to create and install dependencies.
    pause
    exit /b
)

echo Activating virtual environment...
call ".venv\Scripts\activate.bat"

echo Using Python:
python --version

echo Checking demucs in PATH:
where demucs

echo Starting StemWave...
python main.py

echo.
echo [INFO] Program finished.
pause
