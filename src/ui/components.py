import math
import random
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QLabel, QSlider, 
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtGui import (
    QColor, QLinearGradient, QPainter, QBrush, 
    QPen, QPainterPath, QFont, QRadialGradient
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve
)

from src.constants import APP_STYLE, APP_NAME, APP_VERSION

class GlowingButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
        # Set fixed size
        self.setFixedSize(120, 65)
        
        # Set properties
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent focus border
        
        # State variables
        self.hovered = False
        self.pressed = False
        self.playing = False
        self.favorite = False
        
        # Shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)
        
        # Apply initial style
        self.update_style()
        
    def update_style(self):
        # Base gradient colors based on state
        if self.playing:
            start_color = APP_STYLE["accent_gradient_start"]
            end_color = APP_STYLE["accent_gradient_end"]
        elif self.favorite:
            # Special color for favorite buttons
            start_color = APP_STYLE["primary_color"]
            end_color = APP_STYLE["secondary_color"]
        else:
            start_color = APP_STYLE["gradient_start"]
            end_color = APP_STYLE["gradient_end"]
        
        # Create gradient string based on state
        if self.pressed:
            # Darker when pressed
            gradient = f"""
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {QColor(start_color).darker(120).name()}, 
                    stop:1 {QColor(end_color).darker(120).name()}
                );
            """
        elif self.hovered:
            # Lighter when hovered
            gradient = f"""
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {QColor(start_color).lighter(120).name()}, 
                    stop:1 {QColor(end_color).lighter(120).name()}
                );
            """
        else:
            # Normal state
            gradient = f"""
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {start_color}, 
                    stop:1 {end_color}
                );
            """
        
        # Add border for favorites
        border = ""
        if self.favorite and not self.playing:
            border = f"border: 2px solid {APP_STYLE['accent_color']};"
        
        # Apply styles
        self.setStyleSheet(f"""
            QPushButton {{
                {gradient}
                {border}
                color: {APP_STYLE["text_color"]};
                border-radius: {APP_STYLE["button_radius"]};
                font-size: 14px;
                font-weight: bold;
                padding: 4px;
            }}
        """)
        
        # Update shadow for playing state
        if self.playing:
            self.shadow.setColor(QColor(APP_STYLE['glow_color']))
            self.shadow.setBlurRadius(20)
        elif self.favorite:
            self.shadow.setColor(QColor(APP_STYLE['accent_color']))
            self.shadow.setBlurRadius(15)
        else:
            self.shadow.setColor(QColor(0, 0, 0, 150))
            self.shadow.setBlurRadius(15)
    
    def enterEvent(self, event):
        self.hovered = True
        self.update_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.hovered = False
        self.update_style()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        self.pressed = True
        self.update_style()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        self.pressed = False
        self.update_style()
        super().mouseReleaseEvent(event)
    
    def set_playing(self, is_playing):
        self.playing = is_playing
        self.update_style()
        
    def set_favorite(self, is_favorite):
        self.favorite = is_favorite
        self.update_style()
        
    def setProperty(self, name, value):
        super().setProperty(name, value)
        if name == "favorite":
            self.favorite = bool(value)
            self.update_style()

class LogoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 60)
        
        # Animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update)
        self.anim_timer.start(50)  # Update every 50ms
        
        self.phase = 0
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create logo text with version
        logo_text = APP_NAME
        
        # First draw the glow effect
        glow = QColor(APP_STYLE["glow_color"])
        glow.setAlpha(80)  # More transparent
        
        # Create text path for glow
        glow_font = QFont(APP_STYLE["font_family"], 30, QFont.Weight.Bold)
        glow_path = QPainterPath()
        glow_path.addText(5, 42, glow_font, logo_text)
        
        # Draw multiple layers of glow with increasing size for better effect
        for size in [12, 8, 5]:
            blur_pen = QPen(glow, size)
            blur_pen.setStyle(Qt.PenStyle.SolidLine)
            painter.strokePath(glow_path, blur_pen)
        
        # Create text path for main text
        font = QFont(APP_STYLE["font_family"], 30, QFont.Weight.Bold)
        path = QPainterPath()
        path.addText(5, 42, font, logo_text)
        
        # Create outline
        outline_pen = QPen(QColor("#000000"), 3)
        painter.strokePath(path, outline_pen)
        
        # Create gradient for fill
        gradient = QLinearGradient(0, 0, 0, 50)
        gradient.setColorAt(0, QColor(APP_STYLE["accent_gradient_start"]))
        gradient.setColorAt(1, QColor(APP_STYLE["accent_gradient_end"]))
        
        # Use sin wave to animate gradient
        self.phase = (self.phase + 0.05) % (2 * 3.14159)
        offset = (math.sin(self.phase) + 1) / 2  # 0 to 1
        
        # Modify gradient with animation
        shine_color = QColor("#FFFFFF")
        shine_color.setAlpha(200)
        gradient.setColorAt(offset, shine_color)
        
        # Fill with gradient
        painter.fillPath(path, QBrush(gradient))
        
        # Draw version as a smaller text with similar styling but more understated
        version_font = QFont(APP_STYLE["font_family"], 12, QFont.Weight.Bold)
        version_path = QPainterPath()
        version_path.addText(210, 42, version_font, f"v{APP_VERSION}")
        
        # Draw version with outline
        painter.strokePath(version_path, QPen(QColor("#000000"), 2))
        
        # Fill version with gradient
        version_gradient = QLinearGradient(0, 30, 0, 50)
        version_gradient.setColorAt(0, QColor("#CCCCCC"))
        version_gradient.setColorAt(1, QColor("#999999"))
        painter.fillPath(version_path, QBrush(version_gradient))

class WaveformVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(150, 40)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Fixed
        )
        
        # Animation properties
        self.is_playing = False
        self.audio_level = 0  # Current audio level (0-100)
        self.samples = []  # Waveform samples
        self.max_samples = 40  # Maximum number of samples to keep
        
        # Initialize with some starter samples
        for i in range(self.max_samples):
            self.samples.append(0.05)  # Small non-zero value
            
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_waveform)
        self.timer.start(50)  # 50ms = 20fps
        
    def set_playing(self, is_playing):
        """Set whether the visualizer is in playing state"""
        self.is_playing = is_playing
        
        if not is_playing:
            # Reset samples when stopped
            self.samples = [0.05 for _ in range(self.max_samples)]
        
        self.update()
    
    def set_volume_multiplier(self, volume_multiplier):
        """Set the volume multiplier for visualization (0.0 to 1.0)"""
        # This method might be called from soundpad.py
        # It affects how the audio level is visualized
        pass
    
    def clear_waveform(self):
        """Clear the waveform visualization (reset samples)"""
        self.is_playing = False
        self.audio_level = 0
        self.samples = [0.05 for _ in range(self.max_samples)]
        self.update()
    
    def update_audio_level(self, level):
        """Update the audio level (0-100) for the waveform"""
        self.audio_level = level
        
        # Add a new sample
        normalized_level = level / 100.0
        
        # Add some randomness
        jitter = 0.1
        sample = normalized_level * (1.0 + (0.5 - random.random()) * jitter)
        
        # Add to samples and maintain max length
        self.samples.append(sample)
        
        if len(self.samples) > self.max_samples:
            self.samples = self.samples[-self.max_samples:]
        
        self.update()
    
    def update_waveform(self):
        """Update waveform animation based on current state"""
        if self.is_playing:
            # Ensure a minimum audio level for visualization
            current_level = max(10, self.audio_level)
            self.update_audio_level(current_level)
            
            # Add some random fluctuation to the audio level for the next update
            self.audio_level = max(10, min(100, self.audio_level + random.randint(-5, 5)))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor("#151520"))
        
        if not self.is_playing or not self.samples:
            # Draw idle state
            painter.setPen(QColor("#444444"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "IDLE")
            return
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        center_y = height / 2
        spacing = width / max(1, len(self.samples) - 1) if len(self.samples) > 1 else width
        
        # Create gradient for waveform
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(APP_STYLE["accent_gradient_start"]))
        gradient.setColorAt(1, QColor(APP_STYLE["accent_gradient_end"]))
        
        # Draw waveform
        path = QPainterPath()
        
        # Start at the left edge, center
        path.moveTo(0, center_y)
        
        # Draw top half of the waveform
        for i, sample in enumerate(self.samples):
            x = i * spacing
            y = center_y - (sample * center_y * 0.8)  # Scale to 80% of half-height
            path.lineTo(x, y)
        
        # Line to the right edge
        path.lineTo(width, center_y)
        
        # Draw bottom half (mirror of top half)
        for i in range(len(self.samples)-1, -1, -1):
            x = i * spacing
            sample = self.samples[i]
            y = center_y + (sample * center_y * 0.8)  # Mirror below center
            path.lineTo(x, y)
        
        # Close the path
        path.lineTo(0, center_y)
        
        # Fill the waveform
        painter.fillPath(path, QBrush(gradient))
        
        # Draw outline
        painter.setPen(QPen(QColor(APP_STYLE["primary_color"]), 1.5))
        painter.drawPath(path)
        
        painter.end() 