# CxrruptPad - Modern Audio Soundboard

<div align="center">
  <img src="https://i.imgur.com/GWY0My5.png" alt="CxrruptPad Screenshot" width="800"/>
  <p><i>A sleek, feature-rich audio soundboard application built with PyQt6 and pygame</i></p>
  <p>
    <a href="#features">Features</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#system-requirements">Requirements</a> •
    <a href="#contributing">Contributing</a>
  </p>
</div>

## 🎵 Features

- **Organized Sound Management**
  - Arrange sounds into tabbed categories
  - Effortless drag-and-drop interface
  - Favorite sounds for quick access

- **Modern, Professional UI**
  - Sleek dark theme with customizable accents
  - Responsive grid and list view modes
  - Animated transitions and glow effects

- **Advanced Audio Controls**
  - Edit sounds (trim, change volume, adjust speed)
  - Master volume slider with visual feedback
  - Stop all sounds with a single keystroke

- **Integrated Creation Tools**
  - Built-in recording functionality
  - Download sounds directly from YouTube
  - Convert various audio formats automatically

- **Productivity Features**
  - Keyboard shortcuts for rapid triggering
  - Customizable hotkeys for any sound
  - Search functionality for quick access

- **Cross-Platform Support**
  - Works on Windows and Linux
  - Automatic dependency management
  - Consistent experience across platforms

## 🚀 Installation

### Windows

1. **Automatic Installation**
   ```
   # Download and run the installer
   install.bat
   ```

2. **Manual Installation**
   ```
   # Clone the repository
   git clone https://github.com/CxrruptedSoftwares/CxrruptPad.git
   cd CxrruptPad

   # Create a virtual environment
   python -m venv venv
   venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

### Linux

1. **Automatic Installation**
   ```bash
   # Download and run the installer
   chmod +x install.sh
   ./install.sh
   ```

2. **Manual Installation**
   ```bash
   # Clone the repository
   git clone https://github.com/CxrruptedSoftwares/CxrruptPad.git
   cd CxrruptPad

   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

### Running the Application

```bash
# On Windows
run_cxrruptpad.bat

# On Linux
./run_cxrruptpad.sh
```

## 💻 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11 or Linux
- **External Dependencies**: FFmpeg (for recording and audio processing)
- **Storage**: ~100MB for the application and dependencies
- **Memory**: Minimum 2GB RAM (4GB+ recommended)

### Automatic Dependency Installation

On first launch, CxrruptPad will automatically check for and offer to install required external dependencies:

- **Windows**: Using winget or chocolatey
- **Linux**: Using your system's package manager (apt, dnf, pacman, etc.)

## 📋 Usage

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details. 
