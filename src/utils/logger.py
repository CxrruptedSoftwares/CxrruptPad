import os
import sys
import logging
import datetime
import platform
import traceback
from pathlib import Path

def get_log_directory():
    """Get the appropriate directory for storing log files based on the platform."""
    system = platform.system()
    
    if system == "Windows":
        log_dir = os.path.join(os.getenv('APPDATA'), 'CxrruptPad', 'logs')
    elif system == "Linux":
        log_dir = os.path.join(os.path.expanduser('~'), '.config', 'CxrruptPad', 'logs')
    else:
        # Fallback for other platforms
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    
    # Create the directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    return log_dir

def setup_logger():
    """Set up and configure the application logger."""
    # Create a custom logger
    logger = logging.getLogger('CxrruptPad')
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create log directory
    log_dir = get_log_directory()
    
    # Create the latest.log file
    latest_log_path = os.path.join(log_dir, 'latest.log')
    
    # If latest.log exists, archive it with timestamp
    if os.path.exists(latest_log_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_log_path = os.path.join(log_dir, f'log_{timestamp}.log')
        try:
            os.rename(latest_log_path, archived_log_path)
        except Exception:
            # If renaming fails, just proceed with a new file
            pass
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    # File handler
    file_handler = logging.FileHandler(latest_log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_format)
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Log system information
    logger.info(f"=== CxrruptPad Session Started ===")
    logger.info(f"System: {platform.system()} {platform.version()}")
    logger.info(f"Python Version: {platform.python_version()}")
    logger.info(f"Log Directory: {log_dir}")
    
    return logger

# Exception handler to log uncaught exceptions
def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions to the log file."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupt (Ctrl+C)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger = logging.getLogger('CxrruptPad')
    logger.critical("Uncaught Exception:", exc_info=(exc_type, exc_value, exc_traceback))

# Global logger instance
logger = setup_logger()
sys.excepthook = log_uncaught_exceptions 