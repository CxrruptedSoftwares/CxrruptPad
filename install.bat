@echo off
setlocal EnableDelayedExpansion

REM Enable ANSI color processing for Windows 10+
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%version%" == "10.0" (
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>nul
)

REM Set console colors with fallback for terminals that don't support ANSI
set "PURPLE=[95m"
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

REM Determine if color is supported
>nul 2>&1 echo [0m && (
  set "USE_COLOR=1"
) || (
  set "USE_COLOR=0"
  set "PURPLE="
  set "BLUE="
  set "GREEN="
  set "YELLOW="
  set "RED="
  set "NC="
)

title CxrruptPad Installer

if "%USE_COLOR%"=="1" (
  echo %PURPLE%=======================================%NC%
  echo %PURPLE%     CxrruptPad Installation Script    %NC%
  echo %PURPLE%=======================================%NC%
  echo %BLUE%      https://github.com/CxrruptedSoftwares/CxrruptPad %NC%
) else (
  echo =======================================
  echo      CxrruptPad Installation Script    
  echo =======================================
  echo       https://github.com/CxrruptedSoftwares/CxrruptPad
)
echo.

REM Check for admin privileges
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if "%USE_COLOR%"=="1" (
      echo %YELLOW%⚠ Administrator privileges not detected.%NC%
      echo %YELLOW%Some features may not work correctly without admin rights.%NC%
      echo %YELLOW%Consider right-clicking and selecting "Run as Administrator"%NC%
    ) else (
      echo WARNING: Administrator privileges not detected.
      echo Some features may not work correctly without admin rights.
      echo Consider right-clicking and selecting "Run as Administrator"
    )
    echo.
    pause
)

REM Check for Python installation
if "%USE_COLOR%"=="1" (
  echo %BLUE%Checking Python installation...%NC%
) else (
  echo Checking Python installation...
)
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if "%USE_COLOR%"=="1" (
        echo %YELLOW%⚠ Python not found. Let's install it now.%NC%
    ) else (
        echo WARNING: Python not found. Let's install it now.
    )
    
    REM Check if winget is available
    where winget >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        if "%USE_COLOR%"=="1" (
            echo %BLUE%Using winget to install Python...%NC%
        ) else (
            echo Using winget to install Python...
        )
        winget install -e --id Python.Python.3.10
        if %ERRORLEVEL% NEQ 0 (
            goto :python_manual_install
        )
    ) else (
        goto :python_manual_install
    )
    
    REM Refresh PATH environment variable to include new Python installation
    call :refresh_path
    goto :python_check
    
    :python_manual_install
    if "%USE_COLOR%"=="1" (
        echo %YELLOW%Automated installation not available.%NC%
        echo %YELLOW%Please visit https://www.python.org/downloads/ to download and install Python 3.8+%NC%
        echo %YELLOW%Make sure to check "Add Python to PATH" during installation.%NC%
    ) else (
        echo Automated installation not available.
        echo Please visit https://www.python.org/downloads/ to download and install Python 3.8+
        echo Make sure to check "Add Python to PATH" during installation.
    )
    echo.
    echo Press any key to open the Python download page, then run this installer again after installing Python...
    pause >nul
    start "" "https://www.python.org/downloads/"
    exit /b 1
)

:python_check
REM Check Python version
for /f "tokens=*" %%I in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set "PYTHON_VERSION=%%I"
for /f "tokens=1 delims=." %%A in ("!PYTHON_VERSION!") do set "PYTHON_MAJOR=%%A"
for /f "tokens=2 delims=." %%B in ("!PYTHON_VERSION!") do set "PYTHON_MINOR=%%B"

if !PYTHON_MAJOR! LSS 3 (
    if "%USE_COLOR%"=="1" (
        echo %RED%✗ Python !PYTHON_VERSION! detected. CxrruptPad requires Python 3.8 or higher.%NC%
    ) else (
        echo ERROR: Python !PYTHON_VERSION! detected. CxrruptPad requires Python 3.8 or higher.
    )
    goto :python_manual_install
)

if !PYTHON_MINOR! LSS 8 (
    if "%USE_COLOR%"=="1" (
        echo %RED%✗ Python !PYTHON_VERSION! detected. CxrruptPad requires Python 3.8 or higher.%NC%
    ) else (
        echo ERROR: Python !PYTHON_VERSION! detected. CxrruptPad requires Python 3.8 or higher.
    )
    goto :python_manual_install
)

if "%USE_COLOR%"=="1" (
    echo %GREEN%✓ Python !PYTHON_VERSION! detected%NC%
) else (
    echo SUCCESS: Python !PYTHON_VERSION! detected
)

REM Check for FFmpeg
echo.
if "%USE_COLOR%"=="1" (
    echo %BLUE%Checking for FFmpeg...%NC%
) else (
    echo Checking for FFmpeg...
)
where ffmpeg >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if "%USE_COLOR%"=="1" (
        echo %YELLOW%⚠ FFmpeg not found.%NC%
    ) else (
        echo WARNING: FFmpeg not found.
    )
    
    REM Try using winget to install FFmpeg
    where winget >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        if "%USE_COLOR%"=="1" (
            echo %BLUE%Attempting to install FFmpeg using winget...%NC%
        ) else (
            echo Attempting to install FFmpeg using winget...
        )
        winget install -e --id Gyan.FFmpeg
        if %ERRORLEVEL% EQU 0 (
            call :refresh_path
            if "%USE_COLOR%"=="1" (
                echo %GREEN%✓ FFmpeg installed successfully%NC%
            ) else (
                echo SUCCESS: FFmpeg installed successfully
            )
        ) else (
            if "%USE_COLOR%"=="1" (
                echo %YELLOW%The application will install FFmpeg automatically on first run.%NC%
            ) else (
                echo The application will install FFmpeg automatically on first run.
            )
        )
    ) else (
        if "%USE_COLOR%"=="1" (
            echo %YELLOW%The application will install FFmpeg automatically on first run.%NC%
        ) else (
            echo The application will install FFmpeg automatically on first run.
        )
    )
) else (
    if "%USE_COLOR%"=="1" (
        echo %GREEN%✓ FFmpeg is installed%NC%
    ) else (
        echo SUCCESS: FFmpeg is installed
    )
)

REM Check for pip
echo.
if "%USE_COLOR%"=="1" (
    echo %BLUE%Checking for pip...%NC%
) else (
    echo Checking for pip...
)
python -m pip --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if "%USE_COLOR%"=="1" (
        echo %YELLOW%⚠ pip not found, installing...%NC%
    ) else (
        echo WARNING: pip not found, installing...
    )
    python -m ensurepip --upgrade
    if %ERRORLEVEL% NEQ 0 (
        if "%USE_COLOR%"=="1" (
            echo %RED%✗ Failed to install pip. Please install pip manually.%NC%
        ) else (
            echo ERROR: Failed to install pip. Please install pip manually.
        )
        pause
        exit /b 1
    ) else (
        python -m pip install --upgrade pip
        if "%USE_COLOR%"=="1" (
            echo %GREEN%✓ pip installed and upgraded successfully%NC%
        ) else (
            echo SUCCESS: pip installed and upgraded successfully
        )
    )
) else (
    if "%USE_COLOR%"=="1" (
        echo %GREEN%✓ pip is installed%NC%
        echo %BLUE%Upgrading pip to latest version...%NC%
    ) else (
        echo SUCCESS: pip is installed
        echo Upgrading pip to latest version...
    )
    python -m pip install --upgrade pip >nul 2>&1
)

REM Create virtual environment
echo.
if "%USE_COLOR%"=="1" (
    echo %BLUE%Setting up virtual environment...%NC%
) else (
    echo Setting up virtual environment...
)
if exist venv (
    if "%USE_COLOR%"=="1" (
        echo %YELLOW%⚠ Virtual environment already exists. Using existing environment.%NC%
    ) else (
        echo WARNING: Virtual environment already exists. Using existing environment.
    )
) else (
    python -m pip install --upgrade virtualenv >nul 2>&1
    python -m virtualenv venv
    if %ERRORLEVEL% NEQ 0 (
        if "%USE_COLOR%"=="1" (
            echo %RED%✗ Failed to create virtual environment.%NC%
            echo %YELLOW%⚠ Continuing without virtual environment - this is not recommended.%NC%
        ) else (
            echo ERROR: Failed to create virtual environment.
            echo WARNING: Continuing without virtual environment - this is not recommended.
        )
        set VENV_FAILED=1
    ) else (
        if "%USE_COLOR%"=="1" (
            echo %GREEN%✓ Virtual environment created successfully%NC%
        ) else (
            echo SUCCESS: Virtual environment created successfully
        )
    )
)

REM Activate virtual environment if created successfully
if not defined VENV_FAILED (
    if "%USE_COLOR%"=="1" (
        echo %BLUE%Activating virtual environment...%NC%
    ) else (
        echo Activating virtual environment...
    )
    call venv\Scripts\activate.bat
    if %ERRORLEVEL% NEQ 0 (
        if "%USE_COLOR%"=="1" (
            echo %RED%✗ Failed to activate virtual environment. Continuing without it.%NC%
        ) else (
            echo ERROR: Failed to activate virtual environment. Continuing without it.
        )
    ) else (
        if "%USE_COLOR%"=="1" (
            echo %GREEN%✓ Virtual environment activated%NC%
        ) else (
            echo SUCCESS: Virtual environment activated
        )
    )
)

REM Install Python dependencies
echo.
if "%USE_COLOR%"=="1" (
    echo %BLUE%Installing Python dependencies...%NC%
) else (
    echo Installing Python dependencies...
)
pip install --upgrade -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    if "%USE_COLOR%"=="1" (
        echo %RED%✗ Failed to install dependencies. Please check the error message above.%NC%
    ) else (
        echo ERROR: Failed to install dependencies. Please check the error message above.
    )
    pause
    exit /b 1
) else (
    if "%USE_COLOR%"=="1" (
        echo %GREEN%✓ Dependencies installed successfully%NC%
    ) else (
        echo SUCCESS: Dependencies installed successfully
    )
)

REM Create desktop shortcut with icon
echo.
if "%USE_COLOR%"=="1" (
    echo %BLUE%Creating desktop shortcut...%NC%
) else (
    echo Creating desktop shortcut...
)

REM Check for icon, create a simple one if not present
if not exist "%~dp0icon.ico" (
    if exist "%~dp0icon.png" (
        if "%USE_COLOR%"=="1" (
            echo %BLUE%Converting PNG icon to ICO...%NC%
        ) else (
            echo Converting PNG icon to ICO...
        )
        python -c "from PIL import Image; img = Image.open('icon.png'); img.save('icon.ico')" >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            if "%USE_COLOR%"=="1" (
                echo %YELLOW%⚠ Could not convert PNG icon. Creating default icon.%NC%
            ) else (
                echo WARNING: Could not convert PNG icon. Creating default icon.
            )
            call :create_default_icon
        )
    ) else (
        call :create_default_icon
    )
)

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
    echo title CxrruptPad - Modern Audio Soundboard
    echo cd /d "%%~dp0"
    echo call venv\Scripts\activate.bat 2^>nul
    echo echo Starting CxrruptPad...
    echo python main.py
    echo IF %%ERRORLEVEL%% NEQ 0 pause
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
echo.
echo %BLUE%Press any key to launch CxrruptPad...%NC%
pause >nul

REM Launch CxrruptPad
start "" "%~dp0run_cxrruptpad.bat"

exit /b 0

:refresh_path
REM Function to refresh PATH environment variable
echo %BLUE%Refreshing PATH environment variable...%NC%
for /f "tokens=2*" %%A in ('reg query HKCU\Environment /v PATH') do set "USERPATH=%%B"
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set "SYSTEMPATH=%%B"
set "PATH=%USERPATH%;%SYSTEMPATH%"
exit /b 0

:create_default_icon
REM Function to create a default icon
echo %BLUE%Creating default icon...%NC%
powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $icon = [System.Drawing.Icon]::ExtractAssociatedIcon([System.Windows.Forms.Application]::ExecutablePath); $icon.Save([System.IO.File]::Create('%~dp0icon.ico'))" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%⚠ Could not create default icon. Shortcut will use system default icon.%NC%
)
exit /b 0 