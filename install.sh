#!/bin/bash

# CxrruptPad Installation Script for Linux
# ========================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display a fancy header
display_header() {
    clear
    echo -e "${PURPLE}=======================================${NC}"
    echo -e "${PURPLE}     CxrruptPad Installation Script    ${NC}"
    echo -e "${PURPLE}=======================================${NC}"
    echo -e "${BLUE}https://github.com/CxrruptedSoftwares/CxrruptPad${NC}"
    echo ""
}

display_header

# Function to detect package manager
detect_package_manager() {
    if command -v apt-get &>/dev/null; then
        PKG_MANAGER="apt-get"
        PKG_UPDATE="sudo apt-get update"
        PKG_INSTALL="sudo apt-get install -y"
    elif command -v dnf &>/dev/null; then
        PKG_MANAGER="dnf"
        PKG_UPDATE="sudo dnf check-update"
        PKG_INSTALL="sudo dnf install -y"
    elif command -v pacman &>/dev/null; then
        PKG_MANAGER="pacman"
        PKG_UPDATE="sudo pacman -Sy"
        PKG_INSTALL="sudo pacman -S --noconfirm"
    elif command -v zypper &>/dev/null; then
        PKG_MANAGER="zypper"
        PKG_UPDATE="sudo zypper refresh"
        PKG_INSTALL="sudo zypper install -y"
    elif command -v emerge &>/dev/null; then
        PKG_MANAGER="emerge"
        PKG_UPDATE="sudo emerge --sync"
        PKG_INSTALL="sudo emerge --noreplace"
    elif command -v apk &>/dev/null; then
        PKG_MANAGER="apk"
        PKG_UPDATE="sudo apk update"
        PKG_INSTALL="sudo apk add"
    else
        echo -e "${RED}✗ Could not determine package manager. You may need to install dependencies manually.${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Detected package manager: ${GREEN}$PKG_MANAGER${NC}"
    return 0
}

# Function to install a package
install_package() {
    local package_name=$1
    echo -e "${BLUE}Installing ${package_name}...${NC}"
    $PKG_INSTALL $package_name
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Successfully installed ${package_name}${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to install ${package_name}${NC}"
        return 1
    fi
}

# Check if script is run as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${YELLOW}⚠ Running as root is not recommended. Please run as a regular user with sudo privileges.${NC}"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}Installation aborted.${NC}"
            exit 1
        fi
    fi
}

# Update system before proceeding
update_system() {
    echo -e "\n${BLUE}Updating package repositories...${NC}"
    $PKG_UPDATE
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠ Failed to update package repositories. Continuing anyway...${NC}"
    else
        echo -e "${GREEN}✓ Package repositories updated${NC}"
    fi
}

check_root
detect_package_manager || true

# Check if Python 3.8+ is installed
echo -e "\n${BLUE}Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
        PYTHON_CMD=python3
    else
        echo -e "${YELLOW}⚠ Python $PYTHON_VERSION detected. CxrruptPad requires Python 3.8 or higher.${NC}"
        
        # Try to find a suitable Python version
        for py_cmd in python3.8 python3.9 python3.10 python3.11 python3.12; do
            if command -v $py_cmd &>/dev/null; then
                PYTHON_CMD=$py_cmd
                echo -e "${GREEN}✓ Found $py_cmd, will use this instead${NC}"
                break
            fi
        done
        
        # If no suitable version found, try to install Python 3.10
        if [ -z "$PYTHON_CMD" ]; then
            echo -e "${YELLOW}⚠ No suitable Python version found. Attempting to install Python 3.10...${NC}"
            update_system
            
            if [ "$PKG_MANAGER" = "apt-get" ]; then
                $PKG_INSTALL python3.10 python3.10-venv python3.10-dev
            elif [ "$PKG_MANAGER" = "dnf" ]; then
                $PKG_INSTALL python310
            elif [ "$PKG_MANAGER" = "pacman" ]; then
                $PKG_INSTALL python
            elif [ "$PKG_MANAGER" = "zypper" ]; then
                $PKG_INSTALL python310
            elif [ "$PKG_MANAGER" = "emerge" ]; then
                $PKG_INSTALL dev-lang/python:3.10
            elif [ "$PKG_MANAGER" = "apk" ]; then
                $PKG_INSTALL python3
            fi
            
            # Verify installation
            if command -v python3.10 &>/dev/null; then
                PYTHON_CMD=python3.10
                echo -e "${GREEN}✓ Python 3.10 installed successfully${NC}"
            else
                echo -e "${RED}✗ Failed to install Python 3.8+. Please install manually and run this script again.${NC}"
                exit 1
            fi
        fi
    fi
else
    echo -e "${YELLOW}⚠ Python 3 not found. Attempting to install...${NC}"
    update_system
    install_package python3
    
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        echo -e "${GREEN}✓ Python $PYTHON_VERSION installed${NC}"
        PYTHON_CMD=python3
    else
        echo -e "${RED}✗ Failed to install Python. Please install Python 3.8+ manually and run this script again.${NC}"
        exit 1
    fi
fi

# Check for pip
echo -e "\n${BLUE}Checking for pip...${NC}"
if ! $PYTHON_CMD -m pip --version &>/dev/null; then
    echo -e "${YELLOW}⚠ pip not found, attempting to install...${NC}"
    
    update_system
    
    if [ "$PKG_MANAGER" = "apt-get" ]; then
        $PKG_INSTALL python3-pip
    elif [ "$PKG_MANAGER" = "dnf" ]; then
        $PKG_INSTALL python3-pip
    elif [ "$PKG_MANAGER" = "pacman" ]; then
        $PKG_INSTALL python-pip
    elif [ "$PKG_MANAGER" = "zypper" ]; then
        $PKG_INSTALL python3-pip
    elif [ "$PKG_MANAGER" = "emerge" ]; then
        $PKG_INSTALL dev-python/pip
    elif [ "$PKG_MANAGER" = "apk" ]; then
        $PKG_INSTALL py3-pip
    else
        echo -e "${YELLOW}⚠ Could not determine package manager. Trying with ensurepip...${NC}"
        $PYTHON_CMD -m ensurepip --upgrade
    fi
    
    if ! $PYTHON_CMD -m pip --version &>/dev/null; then
        echo -e "${RED}✗ Failed to install pip. Please install pip manually.${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ pip installed successfully${NC}"
        # Upgrade pip
        $PYTHON_CMD -m pip install --upgrade pip
    fi
else
    echo -e "${GREEN}✓ pip is installed${NC}"
    echo -e "${BLUE}Upgrading pip to latest version...${NC}"
    $PYTHON_CMD -m pip install --upgrade pip
fi

# Detect FFmpeg
echo -e "\n${BLUE}Checking for FFmpeg...${NC}"
if ! command -v ffmpeg &>/dev/null; then
    echo -e "${YELLOW}⚠ FFmpeg not found, attempting to install...${NC}"
    
    update_system
    install_package ffmpeg
    
    if ! command -v ffmpeg &>/dev/null; then
        echo -e "${YELLOW}⚠ Failed to install FFmpeg. The application will still work but some features may be limited.${NC}"
    else
        echo -e "${GREEN}✓ FFmpeg installed successfully${NC}"
    fi
else
    echo -e "${GREEN}✓ FFmpeg is installed${NC}"
fi

# Install other development dependencies
echo -e "\n${BLUE}Installing additional development dependencies...${NC}"
if [ "$PKG_MANAGER" = "apt-get" ]; then
    $PKG_INSTALL build-essential libportaudio2 libasound-dev python3-dev
elif [ "$PKG_MANAGER" = "dnf" ]; then
    $PKG_INSTALL gcc portaudio-devel alsa-lib-devel python3-devel
elif [ "$PKG_MANAGER" = "pacman" ]; then
    $PKG_INSTALL base-devel portaudio alsa-lib
elif [ "$PKG_MANAGER" = "zypper" ]; then
    $PKG_INSTALL -t pattern devel_basis
    $PKG_INSTALL portaudio-devel alsa-devel
elif [ "$PKG_MANAGER" = "emerge" ]; then
    $PKG_INSTALL sys-devel/gcc media-libs/portaudio media-libs/alsa-lib media-sound/sox
elif [ "$PKG_MANAGER" = "apk" ]; then
    $PKG_INSTALL build-base portaudio-dev alsa-lib-dev
fi

# Create virtual environment
echo -e "\n${BLUE}Setting up virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists. Using existing environment.${NC}"
else
    $PYTHON_CMD -m pip install --upgrade virtualenv
    $PYTHON_CMD -m virtualenv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to create virtual environment with virtualenv. Trying venv...${NC}"
        
        $PYTHON_CMD -m venv venv
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}⚠ Failed to create virtual environment. Continuing without it (not recommended).${NC}"
            VENV_FAILED=true
        else
            echo -e "${GREEN}✓ Virtual environment created with venv module${NC}"
        fi
    else
        echo -e "${GREEN}✓ Virtual environment created with virtualenv${NC}"
    fi
fi

# Activate virtual environment if created successfully
if [ -z "$VENV_FAILED" ]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to activate virtual environment. Continuing without it.${NC}"
    else
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    fi
fi

# Install Python dependencies
echo -e "\n${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to install dependencies. Please check the error message above.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
fi

# Create desktop file for easy launching
echo -e "\n${BLUE}Creating desktop shortcut...${NC}"
DESKTOP_FILE="$HOME/.local/share/applications/cxrruptpad.desktop"
mkdir -p "$HOME/.local/share/applications"

# Get absolute path to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# Check for icon and create one if not present
if [ ! -f "$SCRIPT_DIR/icon.png" ]; then
    echo -e "${YELLOW}⚠ No icon found. Creating a simple icon...${NC}"
    
    # Try to create a simple icon using Python and pillow if installed
    $PYTHON_CMD -c "
import sys
try:
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (512, 512), color=(29, 25, 48))
    d = ImageDraw.Draw(img)
    d.ellipse((100, 100, 412, 412), fill=(45, 125, 210))
    d.rectangle((150, 200, 362, 312), fill=(29, 25, 48))
    img.save('$SCRIPT_DIR/icon.png')
    print('Icon created')
except ImportError:
    print('PIL not available')
    sys.exit(1)
" 2>/dev/null || echo -e "${YELLOW}⚠ Could not create icon automatically${NC}"
fi

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=CxrruptPad
Comment=Modern Audio Soundboard
Exec=bash -c "cd $SCRIPT_DIR && source venv/bin/activate && python main.py"
Icon=$SCRIPT_DIR/icon.png
Terminal=false
Type=Application
Categories=Audio;Utility;
EOF

if [ -f "$DESKTOP_FILE" ]; then
    # Make the desktop file executable
    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓ Desktop shortcut created at $DESKTOP_FILE${NC}"
    # Update desktop database
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
else
    echo -e "${YELLOW}⚠ Failed to create desktop shortcut${NC}"
fi

# Create executable script
echo -e "\n${BLUE}Creating executable script...${NC}"
cat > "$SCRIPT_DIR/run_cxrruptpad.sh" << EOF
#!/bin/bash
# CxrruptPad Launcher
cd "$SCRIPT_DIR"
source venv/bin/activate
python main.py
EOF

chmod +x "$SCRIPT_DIR/run_cxrruptpad.sh"
echo -e "${GREEN}✓ Created executable script at $SCRIPT_DIR/run_cxrruptpad.sh${NC}"

# Installation complete
echo -e "\n${GREEN}=======================================${NC}"
echo -e "${GREEN}     CxrruptPad Installation Complete    ${NC}"
echo -e "${GREEN}=======================================${NC}"
echo -e "\nYou can now run CxrruptPad in one of the following ways:"
echo -e "1. ${BLUE}./run_cxrruptpad.sh${NC}"
echo -e "2. ${BLUE}From your applications menu${NC}"
echo -e "\nWould you like to launch CxrruptPad now? (y/n)"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${CYAN}Launching CxrruptPad...${NC}"
    "$SCRIPT_DIR/run_cxrruptpad.sh"
else
    echo -e "\n${CYAN}Enjoy using CxrruptPad!${NC}"
fi
