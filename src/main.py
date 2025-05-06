import sys
import os
import platform
import time
import pygame
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QProgressBar, QSplashScreen
)
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import Qt

from src.constants import APP_STYLE, APP_NAME, APP_VERSION, detect_system
from src.ui.styles import set_dark_palette
from src.ui.components import LogoWidget
from src.soundpad import SoundPad
from src.dependencies.dependency_checker import DependencyChecker
from src.audio.audio_utils import initialize_audio
# Import our logger
from src.utils.logger import logger

def main():
    logger.info("Starting CxrruptPad application")
    app = QApplication(sys.argv)
    set_dark_palette(app)
    app.setStyle("Fusion")
    
    try:
        # Create a fancy splash screen
        logger.debug("Creating splash screen")
        splash = QWidget()
        splash.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        splash.setFixedSize(450, 250)
        
        # Set background gradient with border radius
        splash.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {APP_STYLE['darker_color']}, 
                stop:0.3 #1d1930, 
                stop:0.7 #1d1930, 
                stop:1 {APP_STYLE['darker_color']}
            );
            border-radius: 15px;
            border: 1px solid {APP_STYLE['primary_color']};
        """)
        
        # Layout for splash content
        splash_layout = QVBoxLayout(splash)
        splash_layout.setContentsMargins(20, 20, 20, 20)
        splash_layout.setSpacing(10)
        
        # Logo
        logo_widget = LogoWidget()
        logo_widget.setFixedSize(280, 60)
        splash_layout.addWidget(logo_widget, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Status text
        status_label = QLabel(f"Checking dependencies...")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet(f"color: {APP_STYLE['text_color']}; background: transparent; font-size: 14px;")
        status_label.setFont(QFont(APP_STYLE["font_family"], 12))
        splash_layout.addWidget(status_label)
        
        # Progress bar with subtle animation
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
        splash_layout.addWidget(progress)
        
        # Version info
        version_label = QLabel(f"v{APP_VERSION} - {detect_system()}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        version_label.setStyleSheet(f"color: #AAAAAA; background: transparent; font-size: 10px;")
        splash_layout.addWidget(version_label)
        
        # Center the splash screen
        screen_geometry = app.primaryScreen().geometry()
        x = (screen_geometry.width() - splash.width()) // 2
        y = (screen_geometry.height() - splash.height()) // 2
        splash.move(x, y)
        
        # Show the splash screen
        logger.debug("Displaying splash screen")
        splash.show()
        app.processEvents()
        
        # Check dependencies
        logger.info("Checking for required dependencies")
        dependency_checker = DependencyChecker()
        status_label.setText("Checking for required dependencies...")
        app.processEvents()  # Update UI
        time.sleep(0.5)  # Small delay for visual feedback
        
        all_deps_installed = dependency_checker.check_dependencies()
        
        # Show dependency status
        missing_deps = dependency_checker.missing_deps
        if missing_deps:
            logger.warning(f"Missing dependencies: {', '.join(missing_deps)}")
            status_label.setText(f"Missing dependencies: {', '.join(missing_deps)}")
        else:
            logger.info("All dependencies found")
            status_label.setText("All dependencies found!")
        app.processEvents()
        time.sleep(1)  # Give user time to see the status
        
        # Hide splash screen
        logger.debug("Hiding splash screen")
        splash.hide()
        
        # If dependencies are missing, show dialog
        if not all_deps_installed:
            # If user chooses not to install or installation fails, still proceed
            logger.info("Showing dependency installation dialog")
            dependency_checker.show_dependency_dialog()
        
        # Initialize pygame mixer with a sample rate that works well on both Windows and Linux
        logger.info("Initializing audio system")
        initialize_audio()
        
        # Create and show main window
        logger.info("Starting main application window")
        window = SoundPad()
        window.show()
        
        # Use a clean exit
        logger.debug("Entering main application loop")
        exit_code = app.exec()
        
        # Additional cleanup
        logger.info("Application closing, performing cleanup")
        window.cleanup()
        pygame.quit()
        
        logger.info(f"Application exited with code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        # Log the exception with full traceback
        logger.critical(f"Fatal error during startup: {str(e)}", exc_info=True)
        
        # Show error message if something goes wrong during startup
        from PyQt6.QtWidgets import QMessageBox
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Application Error")
        error_dialog.setText(f"Error starting {APP_NAME}:")
        error_dialog.setDetailedText(f"{str(e)}\n\nPlease check the log file at:\n{os.path.join(logger.handlers[1].baseFilename)}")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_dialog.exec()
        sys.exit(1)

if __name__ == "__main__":
    main() 