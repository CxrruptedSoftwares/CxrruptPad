# CxrruptPad - Modern Audio Soundboard

A sleek, feature-rich audio soundboard application built with PyQt6 and pygame. Perfect for streamers, content creators, or anyone who needs quick access to sound effects.

![CxrruptPad Screenshot](https://i.imgur.com/YourScreenshotHere.png)

## Features

- 🎵 Organize sounds into tabbed categories
- 🌈 Modern, stylish UI with glow effects
- 🎚️ Edit sounds (trim, change volume, adjust speed)
- 🎛️ Built-in recording functionality
- ⬇️ Download sounds directly from YouTube
- ⭐ Favorite sounds for quick access
- ⌨️ Keyboard shortcuts for rapid triggering
- 🌗 Cross-platform support (Windows and Linux)
- 🔄 Automatic dependency management

## Installation

### Option 1: Clone the Repository and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/CxrruptSoundpad.git
cd CxrruptSoundpad

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Install from PyPI (if available)

```bash
pip install cxrruptpad
```

### Running the Application

```bash
python main.py
```

## System Requirements

- Python 3.8 or higher
- Windows 10/11 or Linux
- FFmpeg (for recording and audio processing)
- Additional dependencies listed in requirements.txt

## Automatic Dependency Installation

On first launch, CxrruptPad will check if you have all the required external dependencies (like FFmpeg) installed on your system. If any are missing, it will offer to install them automatically:

- On Windows: Using winget or chocolatey
- On Linux: Using your system's package manager (apt, dnf, pacman, etc.)

## Usage

### Managing Tabs and Sounds

- Use the "Add Tab" button to create categories
- Click "Add Sound" to import audio files to the current tab
- Record new sounds or download from YouTube directly in the app
- Right-click sounds for additional options (edit, favorite, assign hotkeys)

### Playing Sounds

- Click any sound button to play it
- Press the space bar to stop all sounds
- Use number keys 1-9 to trigger the first 9 sounds in a tab
- Create custom hotkey assignments for your most used sounds

### Customization

- Toggle between grid and list view modes
- Adjust volume with the slider at the bottom of the window
- Right-click sounds to add favorites or assign custom hotkeys

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 