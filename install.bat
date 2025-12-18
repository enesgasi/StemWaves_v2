@echo off
setlocal

echo ==========================================
echo               WELCOME
echo       StemWave v2.0 Installer
echo ==========================================
echo.

REM 1) Check if Python is already installed
echo Checking for Python...
python -V >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Python is already installed.
    goto :CREATE_VENV
)

echo Python not found. Attempting local installation...

REM 2) Check if local installer exists
set PYINSTALLER=python\python-3.10.9-amd64.exe

if not exist "%PYINSTALLER%" (
    echo.
    echo ERROR: Could not find the Python installer.
    echo Expected at:
    echo     python\python-3.10.9-amd64.exe
    echo.
    echo Please place the Python installer inside the "python" folder.
    echo.
    pause
    exit /b 1
)

REM 3) Install Python silently (per-user, adds to PATH)
echo Running Python 3.10.9 installer...
"%PYINSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=0

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Python installation failed.
    echo Try installing Python manually.
    echo.
    pause
    exit /b 1
)

REM 4) Verify installation
echo Re-checking Python installation...
python -V >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Python still not detected after installation.
    echo Try rebooting your computer or install manually.
    echo.
    pause
    exit /b 1
)

echo Python installation successful!
echo.

:CREATE_VENV
echo ==========================================
echo Creating virtual environment (.venv)
echo ==========================================

python -m venv .venv

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo ERROR: Failed to create virtual environment.
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Installing dependencies...
echo ==========================================

call .venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ==========================================
echo        Installation complete!
echo Run "run.bat" to start StemWave v2.0.
echo ==========================================
echo.
pause
endlocal
