from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

from src.constants import APP_STYLE

def set_dark_palette(app):
    dark_palette = QPalette()
    
    # Set color roles
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(APP_STYLE["dark_color"]))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(APP_STYLE["text_color"]))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(APP_STYLE["darker_color"]))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(APP_STYLE["dark_color"]))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(APP_STYLE["text_color"]))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(APP_STYLE["text_color"]))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(APP_STYLE["dark_color"]))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(APP_STYLE["text_color"]))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor("#FF5CFF"))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(APP_STYLE["accent_color"]))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(APP_STYLE["primary_color"]))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    
    # Set disabled colors
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#666666"))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#666666"))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor("#666666"))
    
    # Apply the dark palette
    app.setPalette(dark_palette)
    
    # Additional application style
    app.setStyleSheet(f"""
        QToolTip {{ 
            color: {APP_STYLE["text_color"]}; 
            background-color: {APP_STYLE["darker_color"]}; 
            border: 1px solid {APP_STYLE["primary_color"]};
            border-radius: 4px;
            padding: 4px;
        }}
        QMenu {{
            background-color: {APP_STYLE["darker_color"]};
            border: 1px solid {APP_STYLE["primary_color"]};
            border-radius: 4px;
        }}
        QMenu::item {{
            padding: 5px 15px;
            color: {APP_STYLE["text_color"]};
        }}
        QMenu::item:selected {{
            background-color: {APP_STYLE["primary_color"]};
        }}
        QScrollBar:vertical {{
            border: none;
            background: #1a1a23;
            width: 10px;
            margin: 0px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: {APP_STYLE["secondary_color"]};
            min-height: 30px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {APP_STYLE["primary_color"]};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            border: none;
            background: #1a1a23;
            height: 10px;
            margin: 0px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background: {APP_STYLE["secondary_color"]};
            min-width: 30px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {APP_STYLE["primary_color"]};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
    """)