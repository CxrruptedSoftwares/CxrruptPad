#!/bin/bash

# CxrruptPad Installation Script for Linux
# ========================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}=======================================${NC}"
echo -e "${PURPLE}     CxrruptPad Installation Script    ${NC}"
echo -e "${PURPLE}=======================================${NC}"

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
        
        if [ -z "$PYTHON_CMD" ]; then
            echo -e "${RED}✗ No suitable Python version found. Please install Python 3.8 or higher.${NC}"
            exit 1
        fi
    fi
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check for pip
echo -e "\n${BLUE}Checking for pip...${NC}"
if ! $PYTHON_CMD -m pip --version &>/dev/null; then
    echo -e "${YELLOW}⚠ pip not found, attempting to install...${NC}"
    
    # Detect package manager
    if command -v apt-get &>/dev/null; then
        echo -e "${BLUE}Using apt package manager${NC}"
        sudo apt-get update
        sudo apt-get install -y python3-pip
    elif command -v dnf &>/dev/null; then
        echo -e "${BLUE}Using dnf package manager${NC}"
        sudo dnf install -y python3-pip
    elif command -v pacman &>/dev/null; then
        echo -e "${BLUE}Using pacman package manager${NC}"
        sudo pacman -S --noconfirm python-pip
    elif command -v zypper &>/dev/null; then
        echo -e "${BLUE}Using zypper package manager${NC}"
        sudo zypper install -y python3-pip
    elif command -v apk &>/dev/null; then
        echo -e "${BLUE}Using apk package manager${NC}"
        sudo apk add py3-pip
    else
        echo -e "${RED}✗ Could not determine package manager. Please install pip manually.${NC}"
        exit 1
    fi
    
    if ! $PYTHON_CMD -m pip --version &>/dev/null; then
        echo -e "${RED}✗ Failed to install pip. Please install pip manually.${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ pip installed successfully${NC}"
    fi
else
    echo -e "${GREEN}✓ pip is installed${NC}"
fi

# Detect FFmpeg
echo -e "\n${BLUE}Checking for FFmpeg...${NC}"
if ! command -v ffmpeg &>/dev/null; then
    echo -e "${YELLOW}⚠ FFmpeg not found, attempting to install...${NC}"
    
    # Detect package manager
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y ffmpeg
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm ffmpeg
    elif command -v zypper &>/dev/null; then
        sudo zypper install -y ffmpeg
    elif command -v apk &>/dev/null; then
        sudo apk add ffmpeg
    else
        echo -e "${YELLOW}⚠ Could not determine package manager. Please install FFmpeg manually.${NC}"
    fi
    
    if ! command -v ffmpeg &>/dev/null; then
        echo -e "${YELLOW}⚠ Failed to install FFmpeg. The application will still work but some features may be limited.${NC}"
    else
        echo -e "${GREEN}✓ FFmpeg installed successfully${NC}"
    fi
else
    echo -e "${GREEN}✓ FFmpeg is installed${NC}"
fi

# Create virtual environment
echo -e "\n${BLUE}Setting up virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists. Using existing environment.${NC}"
else
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠ Failed to create virtual environment with venv. Trying virtualenv...${NC}"
        
        # Try to install virtualenv if not available
        if ! $PYTHON_CMD -m pip show virtualenv &>/dev/null; then
            echo -e "${BLUE}Installing virtualenv...${NC}"
            $PYTHON_CMD -m pip install --user virtualenv
        fi
        
        $PYTHON_CMD -m virtualenv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}✗ Failed to create virtual environment. Continuing without it.${NC}"
            VENV_FAILED=true
        fi
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
pip install -r requirements.txt
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
    echo -e "${GREEN}✓ Desktop shortcut created at $DESKTOP_FILE${NC}"
    # Create a simple icon if it doesn't exist
    if [ ! -f "$SCRIPT_DIR/icon.png" ]; then
        echo -e "${YELLOW}⚠ No icon found. You might want to add an icon at $SCRIPT_DIR/icon.png${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Failed to create desktop shortcut${NC}"
fi

# Create executable script
echo -e "\n${BLUE}Creating executable script...${NC}"
cat > "$SCRIPT_DIR/run_cxrruptpad.sh" << EOF
#!/bin/bash
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
echo -e "\nEnjoy using CxrruptPad!\n" 