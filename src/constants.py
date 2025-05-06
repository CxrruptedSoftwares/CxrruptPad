import platform

# Global styling constants
APP_STYLE = {
    "primary_color": "#B300FF",
    "secondary_color": "#8900CF",
    "dark_color": "#1A1A1D",
    "darker_color": "#121214",
    "accent_color": "#FF5CFF",
    "glow_color": "#FF00FF",
    "text_color": "#FFFFFF",
    "button_radius": "8px",
    "button_height": "65px", 
    "button_width": "120px",
    "font_family": "Segoe UI",
    "gradient_start": "#B300FF",
    "gradient_end": "#5D00A3",
    "accent_gradient_start": "#FF5CFF",
    "accent_gradient_end": "#D437D4"
}

# App version
APP_VERSION = "1.0.0"

# App name
APP_NAME = "CxrruptPad"

# Sound end event for pygame
SOUND_END_EVENT = 25  # pygame.USEREVENT + 1

# Function to get system information
def detect_system():
    system = platform.system()
    if system == "Windows":
        return f"Windows {platform.release()}"
    elif system == "Linux":
        try:
            # Try to get distribution info
            import distro
            return f"Linux ({distro.name()} {distro.version()})"
        except ImportError:
            # Fallback if distro module is not available
            return f"Linux {platform.release()}"
    elif system == "Darwin":
        return f"macOS {platform.mac_ver()[0]}"
    else:
        return system 