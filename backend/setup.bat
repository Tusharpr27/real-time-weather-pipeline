@echo off
REM Setup script for Windows

echo ======================================
echo Real-Time Weather Pipeline Setup
echo ======================================
echo.

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Create logs directory
if not exist "logs" mkdir logs

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo To activate virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To start the application, run:
echo   python main.py
echo.
echo API will be available at:
echo   http://localhost:8000
echo.
echo API Documentation:
echo   http://localhost:8000/docs
echo.
pause
