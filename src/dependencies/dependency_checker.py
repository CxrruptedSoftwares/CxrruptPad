import platform
import subprocess
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QCheckBox, 
    QPushButton, QProgressBar, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMetaObject, Q_ARG

from src.constants import APP_STYLE

class DependencyInstallThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, dependencies, system):
        super().__init__()
        self.dependencies = dependencies
        self.system = system

    def run(self):
        success = True
        
        if self.system == "Windows":
            success = self._install_windows(self.dependencies)
        else:
            success = self._install_linux(self.dependencies)
            
        self.finished_signal.emit(success)

    def _install_windows(self, dependencies):
        success = True
        
        # Check for winget or chocolatey
        has_winget = self._is_installed("winget")
        has_choco = self._is_installed("choco")
        
        if not has_winget and not has_choco:
            # Try to use pip for yt-dlp at least
            if "yt-dlp" in dependencies:
                try:
                    self.progress_signal.emit("Installing yt-dlp via pip...")
                    
                    pip_result = subprocess.run(
                        ['pip3', 'install', '--user', 'yt-dlp'],
                        capture_output=True,
                        text=True
                    )
                    
                    if pip_result.returncode != 0:
                        success = False
                        self.progress_signal.emit("Failed to install yt-dlp via pip.")
                except Exception as e:
                    success = False
                    self.progress_signal.emit(f"Error installing yt-dlp: {str(e)}")
            return success
        
        for dep in dependencies:
            if dep == "yt-dlp":
                try:
                    self.progress_signal.emit("Installing yt-dlp via pip...")
                    
                    pip_result = subprocess.run(
                        ['pip3', 'install', '--user', 'yt-dlp'],
                        capture_output=True,
                        text=True
                    )
                    
                    if pip_result.returncode != 0:
                        success = False
                        self.progress_signal.emit("Failed to install yt-dlp via pip.")
                except Exception as e:
                    success = False
                    self.progress_signal.emit(f"Error installing yt-dlp: {str(e)}")
            else:
                try:
                    if has_winget:
                        self.progress_signal.emit(f"Installing {dep} using winget...")
                        result = subprocess.run(
                            ['winget', 'install', '--id', dep if dep != "ffmpeg" else "Gyan.FFmpeg", '--accept-source-agreements', '-e'],
                            capture_output=True,
                            text=True
                        )
                    elif has_choco:
                        self.progress_signal.emit(f"Installing {dep} using chocolatey...")
                        result = subprocess.run(
                            ['choco', 'install', dep, '-y'],
                            capture_output=True,
                            text=True
                        )
                    
                    if result.returncode != 0:
                        success = False
                        self.progress_signal.emit(f"Failed to install {dep}.")
                except Exception as e:
                    success = False
                    self.progress_signal.emit(f"Error installing {dep}: {str(e)}")
        
        return success

    def _install_linux(self, dependencies):
        success = True
        
        # Determine package manager
        package_manager = None
        install_cmd = []
        
        # Package name mapping for different package managers
        package_map = {
            "apt": {"ffmpeg": "ffmpeg", "sox": "sox", "yt-dlp": "python3-yt-dlp"},
            "dnf": {"ffmpeg": "ffmpeg", "sox": "sox", "yt-dlp": "python3-yt-dlp"},
            "pacman": {"ffmpeg": "ffmpeg", "sox": "sox", "yt-dlp": "yt-dlp"},
            "zypper": {"ffmpeg": "ffmpeg", "sox": "sox", "yt-dlp": "python3-yt-dlp"},
            "apk": {"ffmpeg": "ffmpeg", "sox": "sox", "yt-dlp": "yt-dlp"}
        }
        
        # Check for different package managers
        if self._is_installed("apt"):
            package_manager = "apt"
            install_cmd = ["sudo", "apt", "install", "-y"]
        elif self._is_installed("apt-get"):
            package_manager = "apt"
            install_cmd = ["sudo", "apt-get", "install", "-y"]
        elif self._is_installed("dnf"):
            package_manager = "dnf"
            install_cmd = ["sudo", "dnf", "install", "-y"]
        elif self._is_installed("yum"):
            package_manager = "dnf"
            install_cmd = ["sudo", "yum", "install", "-y"]
        elif self._is_installed("pacman"):
            package_manager = "pacman"
            install_cmd = ["sudo", "pacman", "-S", "--noconfirm"]
        elif self._is_installed("zypper"):
            package_manager = "zypper"
            install_cmd = ["sudo", "zypper", "install", "-y"]
        elif self._is_installed("apk"):
            package_manager = "apk"
            install_cmd = ["sudo", "apk", "add"]
        
        if not package_manager:
            # If we can't determine the package manager, try to use pip for yt-dlp at least
            if "yt-dlp" in dependencies:
                try:
                    self.progress_signal.emit("Installing yt-dlp via pip...")
                    
                    pip_result = subprocess.run(
                        ['pip3', 'install', '--user', 'yt-dlp'],
                        capture_output=True,
                        text=True
                    )
                    
                    if pip_result.returncode != 0:
                        success = False
                        self.progress_signal.emit("Failed to install yt-dlp via pip.")
                except Exception as e:
                    success = False
                    self.progress_signal.emit(f"Error installing yt-dlp: {str(e)}")
            return success
        
        for dep in dependencies:
            if dep == "yt-dlp" and package_manager not in ["apt", "dnf", "pacman", "zypper", "apk"]:
                try:
                    self.progress_signal.emit("Installing yt-dlp via pip...")
                    
                    pip_result = subprocess.run(
                        ['pip3', 'install', '--user', 'yt-dlp'],
                        capture_output=True,
                        text=True
                    )
                    
                    if pip_result.returncode != 0:
                        success = False
                        self.progress_signal.emit("Failed to install yt-dlp via pip.")
                except Exception as e:
                    success = False
                    self.progress_signal.emit(f"Error installing yt-dlp: {str(e)}")
            else:
                # Get package name for current package manager
                if package_manager in package_map and dep in package_map[package_manager]:
                    pkg = package_map[package_manager][dep]
                else:
                    pkg = dep  # Use dependency name as package name
                
                # Update status
                self.progress_signal.emit(f"Installing {dep}...")
                
                try:
                    # Install package
                    result = subprocess.run(
                        install_cmd + [pkg],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        success = False
                        self.progress_signal.emit(f"Failed to install {dep}.")
                except Exception as e:
                    success = False
                    self.progress_signal.emit(f"Error installing {dep}: {str(e)}")
        
        return success

    def _is_installed(self, command):
        try:
            # Hide console window on Windows
            startupinfo = None
            if self.system == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.run(
                [command, '--version'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                startupinfo=startupinfo
            )
            return True
        except FileNotFoundError:
            return False

class DependencyChecker:
    def __init__(self, parent=None):
        self.parent = parent
        self.system = platform.system()
        self.missing_deps = []
        
    def check_dependencies(self):
        self.missing_deps = []
        
        # Check for FFmpeg
        if not self._is_installed('ffmpeg'):
            self.missing_deps.append('ffmpeg')
        
        # Check for yt-dlp or youtube-dl
        if not (self._is_installed('yt-dlp') or self._is_installed('youtube-dl')):
            self.missing_deps.append('yt-dlp')
        
        # Check if SoX is installed (optional but useful)
        if not self._is_installed('sox'):
            self.missing_deps.append('sox')
        
        # Return True if all dependencies are installed
        return len(self.missing_deps) == 0
    
    def _is_installed(self, command):
        try:
            # Hide console window on Windows
            startupinfo = None
            if self.system == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.run(
                [command, '--version'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                startupinfo=startupinfo
            )
            return True
        except FileNotFoundError:
            return False
    
    def show_dependency_dialog(self):
        if not self.missing_deps:
            return True
        
        # Create a dialog to display missing dependencies
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Missing Dependencies")
        dialog.setMinimumWidth(450)
        
        # Apply app style
        dialog.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {APP_STYLE['darker_color']}, 
                    stop:0.3 #1d1930, 
                    stop:0.7 #1d1930, 
                    stop:1 {APP_STYLE['darker_color']}
                );
                border-radius: 10px;
            }}
            QLabel {{
                color: {APP_STYLE['text_color']};
                background: transparent;
            }}
            QCheckBox {{
                color: {APP_STYLE['text_color']};
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: {APP_STYLE['primary_color']};
                border: 2px solid {APP_STYLE['primary_color']};
                border-radius: 3px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: #252535;
                border: 2px solid #444455;
                border-radius: 3px;
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Add header
        header = QLabel("Missing Dependencies Detected")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont(APP_STYLE["font_family"], 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {APP_STYLE['accent_color']}; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Add description
        desc = QLabel(
            "The following dependencies are required but not installed. "
            "Would you like to install them now?"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Add checkboxes for each missing dependency
        checkboxes = {}
        for dep in self.missing_deps:
            cb = QCheckBox(dep)
            cb.setChecked(True)
            layout.addWidget(cb)
            checkboxes[dep] = cb
        
        # Add installation description
        install_desc = QLabel("")
        if self.system == "Windows":
            install_desc.setText(
                "On Windows, installation requires administrator privileges.\n"
                "FFmpeg and yt-dlp will be installed via winget if available."
            )
        else:
            install_desc.setText(
                "On Linux, installation requires sudo privileges.\n"
                "Packages will be installed using your system's package manager."
            )
        install_desc.setWordWrap(True)
        layout.addWidget(install_desc)
        
        # Add status label
        status_label = QLabel("Ready to install")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)
        
        # Add progress bar
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminate progress
        progress.setTextVisible(False)
        progress.setFixedHeight(6)
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #252535;
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {APP_STYLE['accent_gradient_start']}, 
                                          stop:1 {APP_STYLE['accent_gradient_end']});
                border-radius: 3px;
            }}
        """)
        progress.hide()  # Hide initially
        layout.addWidget(progress)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        skip_button = QPushButton("Skip")
        skip_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #333333;
                color: {APP_STYLE['text_color']};
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #444444;
            }}
            QPushButton:pressed {{
                background-color: #222222;
            }}
        """)
        
        install_button = QPushButton("Install Selected")
        install_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 {APP_STYLE['primary_color']}, 
                                           stop:1 {APP_STYLE['secondary_color']});
                color: {APP_STYLE['text_color']};
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {APP_STYLE['secondary_color']}, 
                                          stop:1 {APP_STYLE['primary_color']});
            }}
            QPushButton:pressed {{
                background: {APP_STYLE['secondary_color']};
            }}
            QPushButton:disabled {{
                background: #666666;
                color: #AAAAAA;
            }}
        """)
        
        button_layout.addWidget(skip_button)
        button_layout.addWidget(install_button)
        layout.addLayout(button_layout)
        
        install_result = [False]  # Use list to mutate from inner function
        
        # Install function
        def install_dependencies():
            # Disable buttons and show progress
            install_button.setEnabled(False)
            skip_button.setEnabled(False)
            progress.show()
            
            # Get selected dependencies
            selected_deps = [dep for dep, cb in checkboxes.items() if cb.isChecked()]
            
            if not selected_deps:
                dialog.accept()
                return
                
            # Create installation thread
            install_thread = DependencyInstallThread(selected_deps, self.system)
            
            # Connect signals
            def update_status(message):
                status_label.setText(message)
            
            def on_install_finished(success):
                progress.hide()
                if success:
                    status_label.setText("Installation completed successfully!")
                else:
                    status_label.setText("Some installations failed. Check console for details.")
                
                install_result[0] = success
                # Enable skip button to close dialog
                skip_button.setText("Close")
                skip_button.setEnabled(True)
            
            install_thread.progress_signal.connect(update_status)
            install_thread.finished_signal.connect(on_install_finished)
            
            # Start thread
            install_thread.start()
        
        # Connect buttons
        install_button.clicked.connect(install_dependencies)
        skip_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec()
        
        return install_result[0] 