@echo off
setlocal EnableDelayedExpansion

REM Set console colors
set "PURPLE=[95m"
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

echo %PURPLE%=======================================%NC%
echo %PURPLE%     CxrruptPad Installation Script    %NC%
echo %PURPLE%=======================================%NC%

REM Check for Python installation
echo.
echo %BLUE%Checking Python version...%NC%
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%✗ Python not found. Please install Python 3.8 or higher.%NC%
    echo Visit https://www.python.org/downloads/ to download and install Python.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%I in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set "PYTHON_VERSION=%%I"
for /f "tokens=1 delims=." %%A in ("!PYTHON_VERSION!") do set "PYTHON_MAJOR=%%A"
for /f "tokens=2 delims=." %%B in ("!PYTHON_VERSION!") do set "PYTHON_MINOR=%%B"

if !PYTHON_MAJOR! LSS 3 (
    echo %RED%✗ Python !PYTHON_VERSION! detected. CxrruptPad requires Python 3.8 or higher.%NC%
    pause
    exit /b 1
)

if !PYTHON_MINOR! LSS 8 (
    echo %RED%✗ Python !PYTHON_VERSION! detected. CxrruptPad requires Python 3.8 or higher.%NC%
    pause
    exit /b 1
)

echo %GREEN%✓ Python !PYTHON_VERSION! detected%NC%

REM Check for FFmpeg
echo.
echo %BLUE%Checking for FFmpeg...%NC%
where ffmpeg >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%⚠ FFmpeg not found.%NC%
    echo %YELLOW%The application will install FFmpeg automatically on first run.%NC%
) else (
    echo %GREEN%✓ FFmpeg is installed%NC%
)

REM Check for pip
echo.
echo %BLUE%Checking for pip...%NC%
python -m pip --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%⚠ pip not found, attempting to install...%NC%
    python -m ensurepip --upgrade
    if %ERRORLEVEL% NEQ 0 (
        echo %RED%✗ Failed to install pip. Please install pip manually.%NC%
        pause
        exit /b 1
    ) else (
        echo %GREEN%✓ pip installed successfully%NC%
    )
) else (
    echo %GREEN%✓ pip is installed%NC%
)

REM Create virtual environment
echo.
echo %BLUE%Setting up virtual environment...%NC%
if exist venv (
    echo %YELLOW%⚠ Virtual environment already exists. Using existing environment.%NC%
) else (
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo %YELLOW%⚠ Failed to create virtual environment with venv. Trying virtualenv...%NC%
        
        REM Try to install virtualenv if not available
        python -m pip show virtualenv >nul 2>nul
        if %ERRORLEVEL% NEQ 0 (
            echo %BLUE%Installing virtualenv...%NC%
            python -m pip install --user virtualenv
        )
        
        python -m virtualenv venv
        if %ERRORLEVEL% NEQ 0 (
            echo %RED%✗ Failed to create virtual environment. Continuing without it.%NC%
            set VENV_FAILED=1
        )
    )
)

REM Activate virtual environment if created successfully
if not defined VENV_FAILED (
    echo %BLUE%Activating virtual environment...%NC%
    call venv\Scripts\activate.bat
    if %ERRORLEVEL% NEQ 0 (
        echo %RED%✗ Failed to activate virtual environment. Continuing without it.%NC%
    ) else (
        echo %GREEN%✓ Virtual environment activated%NC%
    )
)

REM Install Python dependencies
echo.
echo %BLUE%Installing Python dependencies...%NC%
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo %RED%✗ Failed to install dependencies. Please check the error message above.%NC%
    pause
    exit /b 1
) else (
    echo %GREEN%✓ Dependencies installed successfully%NC%
)

REM Create desktop shortcut
echo.
echo %BLUE%Creating desktop shortcut...%NC%
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\CxrruptPad.lnk'); $Shortcut.TargetPath = '%~dp0run_cxrruptpad.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = '%~dp0icon.ico,0'; $Shortcut.Description = 'Modern Audio Soundboard'; $Shortcut.Save()"
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%⚠ Failed to create desktop shortcut%NC%
) else (
    echo %GREEN%✓ Desktop shortcut created%NC%
)

REM Create executable batch file
echo.
echo %BLUE%Creating executable script...%NC%
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo call venv\Scripts\activate.bat
    echo python main.py
    echo pause
) > "%~dp0run_cxrruptpad.bat"
echo %GREEN%✓ Created executable script at %~dp0run_cxrruptpad.bat%NC%

REM Installation complete
echo.
echo %GREEN%=======================================%NC%
echo %GREEN%     CxrruptPad Installation Complete    %NC%
echo %GREEN%=======================================%NC%
echo.
echo You can now run CxrruptPad in one of the following ways:
echo 1. %BLUE%Double-click run_cxrruptpad.bat%NC%
echo 2. %BLUE%Use the desktop shortcut%NC%
echo.
echo Enjoy using CxrruptPad!

pause 