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

class SoundPad(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - {detect_system()}")
        self.setMinimumSize(800, 600)
        
        # State variables
        self.current_tab_index = 0
        self.currently_playing = {}  # {channel: (tab_name, sound_index)}
        
        # Setup UI
        self.init_ui()
        
        # Load tabs
        self.load_tabs()
        
        # Load volume setting
        self.load_volume_setting()
        
        # Start playback checking timer
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_sound_status)
        self.check_timer.start(100)  # Check every 100ms
        
        # Add a pygame event handler for sound end events
        pygame.event.set_allowed(SOUND_END_EVENT)
    
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
        pygame.mixer.music.set_volume(value / 100)
        
        # Set volume for all channels
        for i in range(pygame.mixer.get_num_channels()):
            if pygame.mixer.Channel(i).get_busy():
                pygame.mixer.Channel(i).set_volume(value / 100)
        
        # Update the label
        self.volume_value_label.setText(f"{value}%")
        
        # Save the volume setting
        self.save_volume_setting(value)
    
    def save_volume_setting(self, volume):
        # Get settings path
        settings_path = get_app_settings_path()
        
        # Load existing settings or create new
        settings = load_json(settings_path, {"volume": volume})
        
        # Update volume
        settings["volume"] = volume
        
        # Save settings
        save_json(settings_path, settings)
    
    def load_volume_setting(self):
        # Default volume
        default_volume = 80
        
        # Get settings path
        settings_path = get_app_settings_path()
        
        # Load settings
        settings = load_json(settings_path)
        
        # Get volume value
        volume = settings.get("volume", default_volume)
        
        # Set volume slider
        self.volume_slider.setValue(volume)
    
    def load_tabs(self):
        # Clear existing tabs
        self.tab_widget.clear()
        
        # Get sounds directory
        sounds_dir = get_sounds_dir()
        
        # If sounds directory doesn't exist, create it
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir, exist_ok=True)
        
        # Get all subdirectories in the sounds directory
        tab_dirs = [d for d in os.listdir(sounds_dir) if os.path.isdir(os.path.join(sounds_dir, d))]
        
        # Add a default tab if none exist
        if not tab_dirs:
            self.add_tab("Default", prompt=False)
        else:
            # Add each tab
            for tab_name in sorted(tab_dirs):
                tab_page = TabPage(tab_name, self)
                self.tab_widget.addTab(tab_page, tab_name)
                tab_page.load_sounds()
    
    def add_tab(self, name=None, prompt=True):
        if prompt:
            # Prompt user for tab name
            tab_name, ok = QInputDialog.getText(
                self, "Add Tab", "Enter tab name:"
            )
            if not ok or not tab_name:
                return
        else:
            tab_name = name
        
        # Create safe name
        tab_name = "".join([c for c in tab_name if c.isalpha() or c.isdigit() or c.isspace()]).strip()
        if not tab_name:
            return
        
        # Check if tab with this name already exists
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == tab_name:
                QMessageBox.warning(self, "Duplicate Tab", f"A tab named '{tab_name}' already exists.")
                return
        
        # Create tab directory
        tab_dir = get_tab_dir(tab_name)
        
        # Create and add the tab
        tab_page = TabPage(tab_name, self)
        index = self.tab_widget.addTab(tab_page, tab_name)
        
        # Select the new tab
        self.tab_widget.setCurrentIndex(index)
    
    def rename_tab(self):
        # Get current tab index
        index = self.tab_widget.currentIndex()
        if index < 0:
            return
        
        # Get current tab name
        old_name = self.tab_widget.tabText(index)
        
        # Prompt for new name
        new_name, ok = QInputDialog.getText(
            self, "Rename Tab", "Enter new tab name:", text=old_name
        )
        if not ok or not new_name or new_name == old_name:
            return
        
        # Create safe name
        new_name = "".join([c for c in new_name if c.isalpha() or c.isdigit() or c.isspace()]).strip()
        if not new_name:
            return
        
        # Check if tab with this name already exists
        for i in range(self.tab_widget.count()):
            if i != index and self.tab_widget.tabText(i) == new_name:
                QMessageBox.warning(self, "Duplicate Tab", f"A tab named '{new_name}' already exists.")
                return
        
        # Get old and new directories
        old_dir = get_tab_dir(old_name)
        new_dir = os.path.join(get_sounds_dir(), new_name)
        
        try:
            # Rename the directory
            if os.path.exists(old_dir):
                os.rename(old_dir, new_dir)
            else:
                os.makedirs(new_dir, exist_ok=True)
            
            # Rename the tab in the UI
            self.tab_widget.setTabText(index, new_name)
            
            # Get the tab page and update its name
            tab_page = self.tab_widget.widget(index)
            if isinstance(tab_page, TabPage):
                tab_page.tab_name = new_name
                
                # Reload the sound list
                tab_page.load_sounds()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rename tab: {str(e)}")
    
    def delete_tab(self):
        # Get current tab index
        index = self.tab_widget.currentIndex()
        if index < 0:
            return
        
        # Get current tab name
        tab_name = self.tab_widget.tabText(index)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the tab '{tab_name}' and all its sounds?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Stop any playing sounds from this tab
        self.stop_sounds_from_tab(tab_name)
        
        # Remove the tab from the UI
        self.tab_widget.removeTab(index)
        
        # Ask if user wants to delete the directory too
        reply = QMessageBox.question(
            self, "Delete Files",
            f"Do you also want to delete all sound files from '{tab_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get tab directory
                tab_dir = get_tab_dir(tab_name)
                
                # Delete the directory and all its contents
                import shutil
                if os.path.exists(tab_dir):
                    shutil.rmtree(tab_dir)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete tab directory: {str(e)}")
        
        # If no tabs left, add a default one
        if self.tab_widget.count() == 0:
            self.add_tab("Default", prompt=False)
    
    def stop_sounds_from_tab(self, tab_name):
        # Find all channels playing sounds from this tab
        channels_to_stop = []
        for channel, (t_name, _) in self.currently_playing.items():
            if t_name == tab_name:
                channels_to_stop.append(channel)
        
        # Stop the channels
        for channel in channels_to_stop:
            if pygame.mixer.Channel(channel).get_busy():
                pygame.mixer.Channel(channel).stop()
            
            if channel in self.currently_playing:
                del self.currently_playing[channel]
    
    def toggle_sound(self, tab_name, index):
        # Get a free channel for this sound
        channel = pygame.mixer.find_channel()
        if not channel:
            QMessageBox.warning(self, "No Channels", "No free channels available! Stop some sounds first.")
            return
        
        # Find the channel number directly
        # In pygame, find_channel() returns one of the Channel objects
        # We can iterate through channels until we find one that's not busy
        # and that should be the one returned by find_channel()
        channel_num = 0  # Default to first channel if nothing else works
        num_channels = pygame.mixer.get_num_channels()
        
        # Try direct comparison first
        for i in range(num_channels):
            ch = pygame.mixer.Channel(i)
            if ch == channel:
                channel_num = i
                break
        else:
            # Fallback: Find first non-busy channel if direct comparison failed
            for i in range(num_channels):
                ch = pygame.mixer.Channel(i)
                if not ch.get_busy() and i not in self.currently_playing:
                    channel_num = i
                    break
            else:
                # If we still can't find it, use the first available channel
                for i in range(num_channels):
                    if i not in self.currently_playing:
                        channel_num = i
                        break
        
        # Check if this sound is already playing
        is_playing = False
        for ch, (t_name, idx) in list(self.currently_playing.items()):
            if t_name == tab_name and idx == index:
                # Sound is already playing, stop it
                try:
                    if 0 <= ch < pygame.mixer.get_num_channels():  # Ensure channel index is valid
                        pygame.mixer.Channel(ch).stop()
                    del self.currently_playing[ch]
                    is_playing = True
                except Exception as e:
                    print(f"Error stopping channel {ch}: {str(e)}")
                
                # Update UI state
                self.waveform.set_playing(len(self.currently_playing) > 0)
                
                # Update the button state
                tab_index = -1
                for i in range(self.tab_widget.count()):
                    if self.tab_widget.tabText(i) == tab_name:
                        tab_index = i
                        break
                
                if tab_index >= 0:
                    tab_page = self.tab_widget.widget(tab_index)
                    if isinstance(tab_page, TabPage):
                        tab_page.update_button_playing_state(index, False)
                
                return
        
        # If the sound is not already playing, play it
        
        # Get the tab page to find the sound path
        tab_index = -1
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == tab_name:
                tab_index = i
                break
        
        if tab_index < 0:
            return
        
        tab_page = self.tab_widget.widget(tab_index)
        if not isinstance(tab_page, TabPage) or index >= len(tab_page.sounds):
            return
        
        # Get sound data
        sound_data = tab_page.sounds[index]
        sound_path = sound_data['path']
        
        try:
            # Load and play the sound
            sound = pygame.mixer.Sound(sound_path)
            channel.play(sound)
            
            # Set the end event
            channel.set_endevent(SOUND_END_EVENT)
            
            # Apply current volume
            volume = self.volume_slider.value() / 100
            channel.set_volume(volume)
            
            # Save the playing sound info
            self.currently_playing[channel_num] = (tab_name, index)
            
            # Update the waveform state
            self.waveform.set_playing(True)
            
            # Update the button state
            tab_page.update_button_playing_state(index, True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to play sound: {str(e)}")
    
    def check_sound_status(self):
        # Check for sound end events
        for event in pygame.event.get():
            if event.type == SOUND_END_EVENT:
                # A sound has ended on a channel
                # Find which channel
                for channel, (tab_name, index) in list(self.currently_playing.items()):
                    if not pygame.mixer.Channel(channel).get_busy():
                        # Sound has ended, update UI
                        
                        # Update tab button state
                        tab_index = -1
                        for i in range(self.tab_widget.count()):
                            if self.tab_widget.tabText(i) == tab_name:
                                tab_index = i
                                break
                        
                        if tab_index >= 0:
                            tab_page = self.tab_widget.widget(tab_index)
                            if isinstance(tab_page, TabPage):
                                tab_page.update_button_playing_state(index, False)
                        
                        # Remove from currently playing
                        del self.currently_playing[channel]
        
        # Update waveform state if no sounds are playing
        if not self.currently_playing:
            self.waveform.set_playing(False)
    
    def stop_all_sounds(self):
        # Stop all currently playing sounds
        for channel, (tab_name, index) in list(self.currently_playing.items()):
            # Stop the sound
            pygame.mixer.Channel(channel).stop()
            
            # Update the button state
            tab_index = -1
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == tab_name:
                    tab_index = i
                    break
            
            if tab_index >= 0:
                tab_page = self.tab_widget.widget(tab_index)
                if isinstance(tab_page, TabPage):
                    tab_page.update_button_playing_state(index, False)
        
        # Clear the currently playing dict
        self.currently_playing.clear()
        
        # Update waveform state
        self.waveform.set_playing(False)
    
    def on_tab_changed(self, index):
        # Save the current tab index
        self.current_tab_index = index
    
    def keyPressEvent(self, event):
        # Handle spacebar to stop all sounds
        if event.key() == Qt.Key.Key_Space:
            self.stop_all_sounds()
            return
        
        # Handle number keys to trigger sounds
        if Qt.Key.Key_1 <= event.key() <= Qt.Key.Key_9:
            shortcut_idx = event.key() - Qt.Key.Key_1  # 0-8 for keys 1-9
            self.play_sound_by_shortcut(shortcut_idx)
            return
        
        # Handle F1-F12 keys
        if Qt.Key.Key_F1 <= event.key() <= Qt.Key.Key_F12:
            f_idx = event.key() - Qt.Key.Key_F1  # 0-11 for keys F1-F12
            self.play_sound_by_shortcut(f_idx + 9)  # 9-20 for keys F1-F12
            return
        
        # Pass to parent handler
        super().keyPressEvent(event)
    
    def play_sound_by_shortcut(self, shortcut_idx):
        # Get current tab
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return
        
        tab_page = self.tab_widget.widget(current_index)
        if not isinstance(tab_page, TabPage):
            return
        
        # Check for hotkey assignments
        tab_name = self.tab_widget.tabText(current_index)
        favorites_path = os.path.join(get_data_dir(), f"{tab_name}_favorites.json")
        
        if os.path.exists(favorites_path):
            try:
                with open(favorites_path, 'r') as f:
                    favorites_data = json.load(f)
                    
                    hotkeys = favorites_data.get('hotkeys', {})
                    hotkey_str = str(shortcut_idx)
                    
                    if hotkey_str in hotkeys:
                        sound_idx = hotkeys[hotkey_str]
                        # Play the assigned sound
                        self.toggle_sound(tab_name, sound_idx)
                        return
            except:
                pass
        
        # Fallback: Use index directly for 1-9 and F1-F12 keys
        if shortcut_idx < len(tab_page.sounds):
            self.toggle_sound(tab_name, shortcut_idx)
    
    def cleanup(self):
        # Stop the check timer
        if hasattr(self, 'check_timer'):
            self.check_timer.stop()
        
        # Stop all playing sounds
        pygame.mixer.stop()
        
        # Clean up any other resources
        for i in range(self.tab_widget.count()):
            tab_page = self.tab_widget.widget(i)
            if isinstance(tab_page, TabPage):
                tab_page.cleanup()
    
    def closeEvent(self, event):
        # Perform cleanup
        self.cleanup()
        event.accept() 