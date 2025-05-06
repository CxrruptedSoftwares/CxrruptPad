import os
import sys
import json
import pygame
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QPushButton, QLabel, QMessageBox, QInputDialog,
    QMenu, QSlider, QDialog, QFileDialog
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QTimer, QSize

from src.constants import APP_STYLE, APP_NAME, APP_VERSION, SOUND_END_EVENT, detect_system
from src.ui.components import LogoWidget, WaveformVisualizer
from src.audio.recorder import RecorderDialog
from src.utils.file_utils import (
    get_sounds_dir, get_tab_dir, get_data_dir,
    save_json, load_json, get_app_settings_path
)
from src.tabpage import TabPage
from src.utils.logger import logger

class SoundPad(QWidget):
    def __init__(self):
        super().__init__()
        
        logger.info("Initializing SoundPad main application")
        
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - {detect_system()}")
        self.setMinimumSize(800, 600)
        
        # State variables
        self.current_tab_index = 0
        self.currently_playing = {}  # {channel: (tab_name, sound_index)}
        
        # Setup UI
        logger.debug("Setting up user interface")
        self.init_ui()
        
        # Load tabs
        logger.info("Loading saved tabs")
        self.load_tabs()
        
        # Load volume setting
        logger.debug("Loading volume settings")
        self.load_volume_setting()
        
        # Start playback checking timer
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_sound_status)
        self.check_timer.start(100)  # Check every 100ms
        
        # Add a pygame event handler for sound end events
        pygame.event.set_allowed(SOUND_END_EVENT)
        logger.debug("SoundPad initialization complete")
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Header layout with logo
        header_layout = QHBoxLayout()
        
        # Logo
        self.logo = LogoWidget()
        header_layout.addWidget(self.logo)
        
        # Add spacer to push buttons to the right
        header_layout.addStretch()
        
        # Add tab control buttons
        tab_controls = QHBoxLayout()
        tab_controls.setSpacing(5)
        
        # Add Tab button
        self.add_tab_btn = QPushButton("+ Add Tab")
        self.add_tab_btn.clicked.connect(lambda: self.add_tab())
        self.add_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background: {APP_STYLE['primary_color']};
                color: {APP_STYLE['text_color']};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {APP_STYLE['secondary_color']};
            }}
        """)
        tab_controls.addWidget(self.add_tab_btn)
        
        # Rename Tab button
        self.rename_tab_btn = QPushButton("Rename Tab")
        self.rename_tab_btn.clicked.connect(self.rename_tab)
        self.rename_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background: #555555;
                color: {APP_STYLE['text_color']};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                background: #666666;
            }}
        """)
        tab_controls.addWidget(self.rename_tab_btn)
        
        # Delete Tab button
        self.delete_tab_btn = QPushButton("Delete Tab")
        self.delete_tab_btn.clicked.connect(self.delete_tab)
        self.delete_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background: #A62626;
                color: {APP_STYLE['text_color']};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                background: #C62626;
            }}
        """)
        tab_controls.addWidget(self.delete_tab_btn)
        
        header_layout.addLayout(tab_controls)
        main_layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {APP_STYLE['primary_color']};
                background: {APP_STYLE['darker_color']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background: {APP_STYLE['dark_color']};
                color: {APP_STYLE['text_color']};
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 {APP_STYLE['primary_color']}, 
                                           stop:1 {APP_STYLE['secondary_color']});
                color: {APP_STYLE['text_color']};
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background: {APP_STYLE['primary_color']};
            }}
        """)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        # Footer layout
        footer_layout = QHBoxLayout()
        
        # Waveform visualizer
        self.waveform = WaveformVisualizer()
        self.waveform.setFixedHeight(40)
        footer_layout.addWidget(self.waveform, 3)
        
        # Create volume slider
        volume_layout = self.create_volume_slider()
        footer_layout.addLayout(volume_layout, 1)
        
        main_layout.addLayout(footer_layout)
        
        # Set window style
        self.setStyleSheet(f"""
            QWidget {{
                background: {APP_STYLE['dark_color']};
                color: {APP_STYLE['text_color']};
            }}
        """)
    
    def create_volume_slider(self):
        # Create a fancy volume control container
        volume_layout = QVBoxLayout()
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(2)
        
        # Add a label for the volume
        volume_label = QLabel("Volume")
        volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        volume_layout.addWidget(volume_label)
        
        # Create volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)  # Default to full volume
        self.volume_slider.setFixedWidth(150)
        self.volume_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #999999;
                height: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #1A1A1D, 
                                          stop:1 {APP_STYLE['primary_color']});
                border-radius: 5px;
            }}
            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 {APP_STYLE['accent_gradient_start']}, 
                                          stop:1 {APP_STYLE['accent_gradient_end']});
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -4px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 {APP_STYLE['accent_color']}, 
                                          stop:1 {APP_STYLE['primary_color']});
            }}
        """)
        
        # Connect volume slider to change volume
        self.volume_slider.valueChanged.connect(self.set_volume)
        
        volume_layout.addWidget(self.volume_slider)
        
        # Add current volume value label
        self.volume_value_label = QLabel("100%")
        self.volume_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        volume_layout.addWidget(self.volume_value_label)
        
        return volume_layout
    
    def set_volume(self, value):
        # Set volume for pygame mixer (0.0 to 1.0)
        volume = value / 100.0
        pygame.mixer.music.set_volume(volume)
        for i in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(i).set_volume(volume)
        
        # Update waveform visualizer volume
        self.waveform.set_volume_multiplier(volume)
        
        # Save the volume setting
        self.save_volume_setting(value)
        logger.debug(f"Volume set to {value}%")
    
    def save_volume_setting(self, volume):
        # Get settings path
        settings_path = get_app_settings_path()
        
        # Load existing settings or create new ones
        if os.path.exists(settings_path):
            settings = load_json(settings_path)
        else:
            settings = {}
        
        # Update volume setting
        settings['volume'] = volume
        save_json(settings_path, settings)
        logger.debug(f"Volume setting saved: {volume}%")
    
    def load_volume_setting(self):
        # Default volume
        volume = 100
        
        # Get settings path
        settings_path = get_app_settings_path()
        
        # Load settings if they exist
        if os.path.exists(settings_path):
            settings = load_json(settings_path)
            if 'volume' in settings:
                volume = settings['volume']
                logger.debug(f"Loaded volume setting: {volume}%")
        
        # Set the volume slider and apply the volume
        self.volume_slider.setValue(volume)
    
    def load_tabs(self):
        # Clear existing tabs
        logger.debug("Clearing existing tabs")
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)
        
        # Get the tabs directory
        tabs_dir = get_tab_dir()
        
        # Ensure the tabs directory exists
        if not os.path.exists(tabs_dir):
            os.makedirs(tabs_dir)
            logger.info(f"Created tabs directory: {tabs_dir}")
        
        # Get all subdirectories in the tabs directory (each is a tab)
        tab_dirs = [d for d in os.listdir(tabs_dir) if os.path.isdir(os.path.join(tabs_dir, d))]
        
        # If no tabs exist, create a default one
        if not tab_dirs:
            logger.info("No tabs found, creating default tab")
            self.add_tab("Default", prompt=False)
        else:
            # Load each tab
            for tab_name in sorted(tab_dirs):
                logger.debug(f"Loading tab: {tab_name}")
                tab_page = TabPage(tab_name, self)
                self.tab_widget.addTab(tab_page, tab_name)
            
            # Set the current tab to the saved index or 0
            settings_path = get_app_settings_path()
            if os.path.exists(settings_path):
                settings = load_json(settings_path)
                if 'current_tab' in settings and settings['current_tab'] < len(tab_dirs):
                    self.tab_widget.setCurrentIndex(settings['current_tab'])
                    logger.debug(f"Set current tab to saved index: {settings['current_tab']}")
    
    def add_tab(self, name=None, prompt=True):
        if prompt:
            # Prompt for tab name
            name, ok = QInputDialog.getText(self, 
                                          "New Tab", 
                                          "Enter a name for the new tab:")
            if not ok or not name:
                return
        
        # Ensure name is valid for a directory
        name = name.replace('/', '_').replace('\\', '_').strip()
        if not name:
            name = "New Tab"
        
        # Create tab directory
        tab_dir = os.path.join(get_tab_dir(), name)
        if os.path.exists(tab_dir):
            # Tab already exists
            QMessageBox.warning(self, "Tab Exists", 
                              f"A tab named '{name}' already exists.")
            logger.warning(f"Attempted to create tab that already exists: {name}")
            return
        
        # Create the directory
        os.makedirs(tab_dir)
        
        # Create the tab page
        tab_page = TabPage(name, self)
        
        # Add the tab to the tab widget
        index = self.tab_widget.addTab(tab_page, name)
        self.tab_widget.setCurrentIndex(index)
        
        logger.info(f"Created new tab: {name}")
    
    def rename_tab(self):
        # Get current tab index
        index = self.tab_widget.currentIndex()
        if index == -1:
            return
        
        # Get current tab name
        old_name = self.tab_widget.tabText(index)
        
        # Prompt for new name
        new_name, ok = QInputDialog.getText(
            self, "Rename Tab", 
            "Enter a new name for this tab:", 
            text=old_name
        )
        
        if not ok or not new_name or new_name == old_name:
            return
        
        # Ensure name is valid for a directory
        new_name = new_name.replace('/', '_').replace('\\', '_').strip()
        if not new_name:
            return
        
        # Check if a tab with this name already exists
        tab_dir = os.path.join(get_tab_dir(), new_name)
        if os.path.exists(tab_dir):
            QMessageBox.warning(self, "Tab Exists", 
                              f"A tab named '{new_name}' already exists.")
            logger.warning(f"Attempted to rename tab to existing name: {new_name}")
            return
        
        # Rename the directory
        old_dir = os.path.join(get_tab_dir(), old_name)
        try:
            os.rename(old_dir, tab_dir)
            
            # Update the tab widget
            self.tab_widget.setTabText(index, new_name)
            
            # Update the tab page
            tab_page = self.tab_widget.currentWidget()
            if tab_page:
                tab_page.tab_name = new_name
                
            logger.info(f"Renamed tab from '{old_name}' to '{new_name}'")
        except Exception as e:
            QMessageBox.critical(self, "Rename Failed", 
                               f"Failed to rename tab: {str(e)}")
            logger.error(f"Failed to rename tab from '{old_name}' to '{new_name}': {str(e)}")
    
    def delete_tab(self):
        # Get current tab index
        index = self.tab_widget.currentIndex()
        if index == -1:
            return
        
        # Get tab name
        tab_name = self.tab_widget.tabText(index)
        
        # Confirm deletion
        result = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete the tab '{tab_name}' and all its sounds?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result != QMessageBox.StandardButton.Yes:
            return
        
        # Stop any sounds from this tab
        self.stop_sounds_from_tab(tab_name)
        
        # Remove the tab
        self.tab_widget.removeTab(index)
        
        # Delete the tab directory
        tab_dir = os.path.join(get_tab_dir(), tab_name)
        try:
            import shutil
            shutil.rmtree(tab_dir)
            logger.info(f"Deleted tab: {tab_name}")
        except Exception as e:
            QMessageBox.critical(self, "Delete Failed", 
                               f"Failed to delete tab directory: {str(e)}")
            logger.error(f"Failed to delete tab directory for '{tab_name}': {str(e)}")
            return
        
        # If no tabs left, create a default one
        if self.tab_widget.count() == 0:
            self.add_tab("Default", prompt=False)
            logger.info("Created new default tab after deleting the last tab")
    
    def stop_sounds_from_tab(self, tab_name):
        # Find all channels playing sounds from this tab
        channels_to_stop = []
        for channel, (playing_tab, _) in self.currently_playing.items():
            if playing_tab == tab_name:
                channels_to_stop.append(channel)
        
        # Stop the sounds
        for channel in channels_to_stop:
            if channel in self.currently_playing:
                channel.stop()
                del self.currently_playing[channel]
                
        logger.debug(f"Stopped {len(channels_to_stop)} sounds from tab: {tab_name}")
    
    def toggle_sound(self, tab_name, index):
        # Get a free channel for this sound
        try:
            # Check if this sound is already playing
            for channel, (playing_tab, playing_index) in list(self.currently_playing.items()):
                if playing_tab == tab_name and playing_index == index:
                    # Stop the sound
                    channel.stop()
                    del self.currently_playing[channel]
                    logger.debug(f"Stopped sound {index} in tab '{tab_name}'")
                    return
            
            # Sound is not playing, so play it
            # Get the TabPage for this tab
            tab_page = None
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == tab_name:
                    tab_page = self.tab_widget.widget(i)
                    break
            
            if not tab_page:
                logger.error(f"Could not find tab page for '{tab_name}'")
                return
            
            # Get the sound data
            sound_data = tab_page.get_sound_data(index)
            if not sound_data:
                logger.warning(f"No sound data found for index {index} in tab '{tab_name}'")
                return
            
            sound_path = sound_data.get('path', '')
            if not sound_path or not os.path.exists(sound_path):
                logger.error(f"Sound file not found: {sound_path}")
                return
            
            # Get a free channel
            channel = pygame.mixer.find_channel()
            if not channel:
                # No free channels, stop the oldest sound
                oldest_channel = None
                oldest_time = float('inf')
                for ch, _ in self.currently_playing.items():
                    if ch.get_sound() and ch.get_busy():
                        sound_pos = ch.get_pos() / 1000.0  # Convert to seconds
                        sound_length = ch.get_sound().get_length()
                        time_left = sound_length - sound_pos
                        if time_left < oldest_time:
                            oldest_time = time_left
                            oldest_channel = ch
                
                if oldest_channel:
                    oldest_channel.stop()
                    del self.currently_playing[oldest_channel]
                    channel = oldest_channel
                    logger.debug("Stopped oldest sound to free up a channel")
                else:
                    logger.warning("No channels available to play sound")
                    return
            
            # Load and play the sound
            try:
                sound = pygame.mixer.Sound(sound_path)
                
                # Get the volume
                volume = self.volume_slider.value() / 100.0
                
                # Set the volume for this channel
                channel.set_volume(volume)
                
                # Play the sound
                channel.play(sound)
                
                # Store the playing sound
                self.currently_playing[channel] = (tab_name, index)
                
                logger.debug(f"Playing sound {index} from tab '{tab_name}': {os.path.basename(sound_path)}")
                
                # Set the channel's endevent
                channel.set_endevent(SOUND_END_EVENT)
                
                # Update the tab page button to show it's playing
                tab_page.set_button_playing_state(index, True)
                
            except Exception as e:
                logger.error(f"Error playing sound {index} from tab '{tab_name}': {str(e)}")
                QMessageBox.critical(self, "Playback Error", 
                                   f"Failed to play sound: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error in toggle_sound: {str(e)}", exc_info=True)
    
    def check_sound_status(self):
        # Check for sound end events
        for event in pygame.event.get(SOUND_END_EVENT):
            # Find the channel that ended
            for channel, (tab_name, index) in list(self.currently_playing.items()):
                if not channel.get_busy():
                    # Sound has ended
                    del self.currently_playing[channel]
                    
                    # Update the tab page button to show it's not playing
                    for i in range(self.tab_widget.count()):
                        if self.tab_widget.tabText(i) == tab_name:
                            tab_page = self.tab_widget.widget(i)
                            tab_page.set_button_playing_state(index, False)
                            logger.debug(f"Sound {index} in tab '{tab_name}' finished playing")
                            break
        
        # Update waveform visualizer
        if pygame.mixer.get_busy():
            self.waveform.update_waveform()
        else:
            self.waveform.clear_waveform()
    
    def stop_all_sounds(self):
        logger.debug("Stopping all sounds")
        # Stop all currently playing sounds
        for channel, (tab_name, index) in list(self.currently_playing.items()):
            if channel.get_busy():
                channel.stop()
                
                # Update the tab page button to show it's not playing
                for i in range(self.tab_widget.count()):
                    if self.tab_widget.tabText(i) == tab_name:
                        tab_page = self.tab_widget.widget(i)
                        tab_page.set_button_playing_state(index, False)
                        break
        
        # Clear the currently playing dictionary
        self.currently_playing.clear()
        
        # Clear the waveform
        self.waveform.clear_waveform()
    
    def on_tab_changed(self, index):
        # Save the current tab index
        self.current_tab_index = index
        settings_path = get_app_settings_path()
        settings = load_json(settings_path) if os.path.exists(settings_path) else {}
        settings['current_tab'] = index
        save_json(settings_path, settings)
        logger.debug(f"Changed to tab index {index}")
    
    def keyPressEvent(self, event):
        # Handle spacebar to stop all sounds
        if event.key() == Qt.Key.Key_Space:
            self.stop_all_sounds()
        
        # Handle number keys 1-9 to trigger sounds
        elif Qt.Key.Key_1 <= event.key() <= Qt.Key.Key_9:
            shortcut_idx = event.key() - Qt.Key.Key_1  # Convert to 0-based index
            self.play_sound_by_shortcut(shortcut_idx)
        
        # Let parent class handle other keys
        else:
            super().keyPressEvent(event)
    
    def play_sound_by_shortcut(self, shortcut_idx):
        # Get current tab
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            return
        
        # Play the sound at the given shortcut index
        current_tab.play_sound_by_index(shortcut_idx)
        logger.debug(f"Triggered sound via keyboard shortcut: {shortcut_idx + 1}")
    
    def cleanup(self):
        logger.info("Performing application cleanup")
        # Stop the check timer
        if hasattr(self, 'check_timer'):
            self.check_timer.stop()
        
        # Stop all sounds
        self.stop_all_sounds()
        
        # Save the current tab index
        settings_path = get_app_settings_path()
        settings = load_json(settings_path) if os.path.exists(settings_path) else {}
        settings['current_tab'] = self.tab_widget.currentIndex()
        save_json(settings_path, settings)
        
        logger.debug("Cleanup completed")
    
    def closeEvent(self, event):
        # Perform cleanup
        self.cleanup()
        logger.info("Application closing")
        event.accept() 