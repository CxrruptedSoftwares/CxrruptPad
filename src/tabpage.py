import os
import pygame
import concurrent.futures
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
    QPushButton, QLabel, QMessageBox, QMenu, QDialog,
    QFileDialog, QInputDialog, QGridLayout
)
from PyQt6.QtGui import QAction, QIcon, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSignal

from src.constants import APP_STYLE
from src.ui.components import GlowingButton, WaveformVisualizer
from src.audio.threads import LoadSoundsThread, YouTubeDownloadThread, PlaylistDownloadThread
from src.audio.recorder import RecorderDialog
from src.utils.file_utils import (
    get_tab_dir, get_tab_favorites_path, save_json, load_json,
    create_safe_filename, delete_file_safely, move_file_safely
)

class TabPage(QWidget):
    def __init__(self, tab_name, parent=None):
        super().__init__(parent)
        self.tab_name = tab_name
        self.parent = parent
        self.sounds = []
        self.buttons = []
        self.sound_buttons_layout = None
        self.favorites = {}
        self.hotkeys = {}
        
        # Initialize UI
        self.init_ui()
        
        # Load favorites and hotkeys
        self.load_favorites()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Control buttons layout
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Add Sound button
        self.add_sound_btn = QPushButton("Add Sound")
        self.add_sound_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 {APP_STYLE['primary_color']}, 
                                          stop:1 {APP_STYLE['secondary_color']});
                color: {APP_STYLE['text_color']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 {APP_STYLE['secondary_color']}, 
                                          stop:1 {APP_STYLE['primary_color']});
            }}
        """)
        self.add_sound_btn.clicked.connect(self.show_add_sound_menu)
        controls_layout.addWidget(self.add_sound_btn)
        
        # Record Sound button
        self.record_sound_btn = QPushButton("Record Sound")
        self.record_sound_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 {APP_STYLE['accent_gradient_start']}, 
                                          stop:1 {APP_STYLE['accent_gradient_end']});
                color: {APP_STYLE['text_color']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 {APP_STYLE['accent_gradient_end']}, 
                                          stop:1 {APP_STYLE['accent_gradient_start']});
            }}
        """)
        self.record_sound_btn.clicked.connect(self.show_recorder)
        controls_layout.addWidget(self.record_sound_btn)
        
        # YouTube Download button
        self.youtube_btn = QPushButton("YouTube Download")
        self.youtube_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FF0000;
                color: {APP_STYLE['text_color']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #CC0000;
            }}
        """)
        self.youtube_btn.clicked.connect(self.show_youtube_dialog)
        controls_layout.addWidget(self.youtube_btn)
        
        # Stop All button
        self.stop_all_btn = QPushButton("Stop All")
        self.stop_all_btn.setStyleSheet(f"""
            QPushButton {{
                background: #A62626;
                color: {APP_STYLE['text_color']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #C62626;
            }}
        """)
        self.stop_all_btn.clicked.connect(self.stop_all_sounds)
        controls_layout.addWidget(self.stop_all_btn)
        
        # Add spacer to push reload to the right
        controls_layout.addStretch(1)
        
        # Reload button
        self.reload_btn = QPushButton("Reload")
        self.reload_btn.setStyleSheet(f"""
            QPushButton {{
                background: #444444;
                color: {APP_STYLE['text_color']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: #555555;
            }}
        """)
        self.reload_btn.clicked.connect(self.load_sounds)
        controls_layout.addWidget(self.reload_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {APP_STYLE['text_color']}; background: transparent;")
        main_layout.addWidget(self.status_label)
        
        # Scroll area for sound buttons
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: 1px solid {APP_STYLE['primary_color']};
                border-radius: 8px;
            }}
        """)
        
        # Create container for sound buttons
        self.sound_buttons_container = QWidget()
        self.sound_buttons_container.setStyleSheet("background: transparent;")
        
        # Grid layout for sound buttons
        self.sound_buttons_layout = QGridLayout(self.sound_buttons_container)
        self.sound_buttons_layout.setContentsMargins(10, 10, 10, 10)
        self.sound_buttons_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.sound_buttons_container)
        main_layout.addWidget(self.scroll_area)
    
    def load_sounds(self):
        # Clear existing sound buttons
        self.clear_sound_buttons()
        
        # Update status
        self.status_label.setText("Loading sounds...")
        
        # Start thread to load sounds
        self.load_thread = LoadSoundsThread(self.tab_name)
        self.load_thread.loading_status_signal.connect(self.status_label.setText)
        self.load_thread.loading_finished_signal.connect(self.on_sounds_loaded)
        self.load_thread.start()
    
    def clear_sound_buttons(self):
        # Remove all buttons from layout
        if self.sound_buttons_layout:
            while self.sound_buttons_layout.count():
                item = self.sound_buttons_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
        
        # Clear buttons list
        self.buttons.clear()
    
    def on_sounds_loaded(self, sounds, success):
        # Set sounds list
        self.sounds = sounds
        
        if not success:
            self.status_label.setText("Error loading sounds")
            return
        
        # Create sound buttons
        self.create_sound_buttons()
        
        # Update status
        self.status_label.setText(f"Loaded {len(self.sounds)} sounds")
    
    def create_sound_buttons(self):
        # Clear existing buttons
        self.clear_sound_buttons()
        
        # Calculate columns based on container width (approximately)
        columns = max(3, self.scroll_area.width() // 150)
        
        # Create buttons for each sound
        for i, sound in enumerate(self.sounds):
            button = GlowingButton(sound['name'])
            button.clicked.connect(lambda checked, idx=i: self.toggle_sound(idx))
            
            # Set up context menu
            button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            button.customContextMenuRequested.connect(lambda pos, idx=i: self.show_sound_context_menu(pos, idx))
            
            # Add button to grid layout
            row = i // columns
            col = i % columns
            self.sound_buttons_layout.addWidget(button, row, col)
            
            # Add to buttons list
            self.buttons.append(button)
            
            # Check if sound is a favorite and style accordingly
            if str(i) in self.favorites:
                button.setProperty("favorite", True)
                # Ensure the button shadow is visible
                button.shadow.setColor(QColor(APP_STYLE['accent_color']))
            
            # Look for hotkey assignment
            for key, value in self.hotkeys.items():
                if value == str(i):
                    try:
                        key_num = int(key)
                        if 0 <= key_num <= 8:  # 1-9 keys
                            hotkey = f"{key_num + 1}"
                            button.setText(f"{sound['name']} [{hotkey}]")
                        elif 9 <= key_num <= 20:  # F1-F12 keys
                            hotkey = f"F{key_num - 8}"
                            button.setText(f"{sound['name']} [{hotkey}]")
                    except:
                        pass
        
        # Update the layout
        self.sound_buttons_container.updateGeometry()
    
    def toggle_sound(self, index):
        # Call the parent's toggle sound method
        if self.parent and hasattr(self.parent, 'toggle_sound'):
            self.parent.toggle_sound(self.tab_name, index)
    
    def update_button_playing_state(self, index, is_playing):
        # Update button state
        if 0 <= index < len(self.buttons):
            self.buttons[index].set_playing(is_playing)
    
    def stop_all_sounds(self):
        # Tell parent to stop all sounds
        if self.parent and hasattr(self.parent, 'stop_all_sounds'):
            self.parent.stop_all_sounds()
    
    def show_add_sound_menu(self):
        # Create context menu
        menu = QMenu(self)
        
        # Add actions
        add_file_action = QAction("Add Sound File", self)
        add_file_action.triggered.connect(self.add_sound_file)
        menu.addAction(add_file_action)
        
        add_folder_action = QAction("Add Sound Folder", self)
        add_folder_action.triggered.connect(self.add_sound_folder)
        menu.addAction(add_folder_action)
        
        # Show the menu
        menu.exec(self.add_sound_btn.mapToGlobal(self.add_sound_btn.rect().bottomLeft()))
    
    def add_sound_file(self):
        # Show file open dialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Sound Files",
            "",
            "Sound Files (*.mp3 *.wav *.ogg);;All Files (*.*)"
        )
        
        if not file_paths:
            return
        
        # Get tab directory
        tab_dir = get_tab_dir(self.tab_name)
        
        # Copy files to tab directory
        for src_path in file_paths:
            try:
                # Get file name
                file_name = os.path.basename(src_path)
                
                # Create destination path
                dst_path = os.path.join(tab_dir, file_name)
                
                # Check if file already exists
                if os.path.exists(dst_path):
                    # Ask to overwrite
                    reply = QMessageBox.question(
                        self,
                        "File Exists",
                        f"A file named '{file_name}' already exists. Overwrite?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply != QMessageBox.StandardButton.Yes:
                        continue
                
                # Copy file
                with open(src_path, 'rb') as src_file:
                    with open(dst_path, 'wb') as dst_file:
                        dst_file.write(src_file.read())
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy file: {str(e)}")
        
        # Reload sounds
        self.load_sounds()
    
    def add_sound_folder(self):
        # Show folder select dialog
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder Containing Sound Files"
        )
        
        if not folder_path:
            return
        
        # Get tab directory
        tab_dir = get_tab_dir(self.tab_name)
        
        # Find all sound files in the folder
        sound_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                    sound_files.append(os.path.join(root, file))
        
        if not sound_files:
            QMessageBox.information(self, "No Sound Files", "No sound files found in the selected folder.")
            return
        
        # Ask if user wants to add sound files
        reply = QMessageBox.question(
            self,
            "Add Sound Files",
            f"Found {len(sound_files)} sound files. Add them to the tab?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Copy files to tab directory
        success_count = 0
        
        for src_path in sound_files:
            try:
                # Get file name
                file_name = os.path.basename(src_path)
                
                # Create destination path
                dst_path = os.path.join(tab_dir, file_name)
                
                # Copy file (overwrite if exists)
                with open(src_path, 'rb') as src_file:
                    with open(dst_path, 'wb') as dst_file:
                        dst_file.write(src_file.read())
                
                success_count += 1
                
            except Exception as e:
                pass  # Skip failed files
        
        # Show result
        QMessageBox.information(
            self,
            "Import Complete",
            f"Successfully imported {success_count} out of {len(sound_files)} sounds."
        )
        
        # Reload sounds
        self.load_sounds()
    
    def show_recorder(self):
        # Get tab directory
        tab_dir = get_tab_dir(self.tab_name)
        
        # Create and show recorder dialog
        dialog = RecorderDialog(self, tab_dir)
        result = dialog.exec()
        
        # Reload sounds if changes were made
        if result == QDialog.DialogCode.Accepted:
            self.load_sounds()
    
    def show_youtube_dialog(self):
        # Prompt for YouTube URL
        url, ok = QInputDialog.getText(
            self,
            "YouTube Download",
            "Enter YouTube video URL:"
        )
        
        if not ok or not url:
            return
        
        # Prompt for sound name
        sound_name, ok = QInputDialog.getText(
            self,
            "Sound Name",
            "Enter a name for the sound:",
            text=f"YouTube_{url.split('=')[-1] if '=' in url else 'Sound'}"
        )
        
        if not ok or not sound_name:
            return
        
        # Create safe filename
        safe_name = create_safe_filename(sound_name)
        if not safe_name:
            safe_name = "YouTube_Sound"
        
        # Get tab directory
        tab_dir = get_tab_dir(self.tab_name)
        
        # Create output path
        output_path = os.path.join(tab_dir, safe_name)
        
        # Create progress dialog
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("Downloading from YouTube")
        progress_dialog.setMinimumWidth(400)
        
        # Apply app style
        progress_dialog.setStyleSheet(f"""
            QDialog {{
                background: {APP_STYLE['darker_color']};
            }}
            QLabel {{
                color: {APP_STYLE['text_color']};
            }}
            QProgressBar {{
                border: 1px solid {APP_STYLE['primary_color']};
                border-radius: 5px;
                background: #252535;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {APP_STYLE['primary_color']}, 
                                          stop:1 {APP_STYLE['secondary_color']});
                border-radius: 4px;
            }}
        """)
        
        # Create layout
        layout = QVBoxLayout(progress_dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Add status label
        status_label = QLabel(f"Downloading '{safe_name}' from YouTube...")
        layout.addWidget(status_label)
        
        # Add progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        layout.addWidget(progress_bar)
        
        # Create download thread
        download_thread = YouTubeDownloadThread(url, output_path)
        
        # Connect signals
        download_thread.progress_signal.connect(progress_bar.setValue)
        
        def on_download_finished(file_path):
            progress_dialog.accept()
            
            QMessageBox.information(
                self,
                "Download Complete",
                f"Successfully downloaded '{os.path.basename(file_path)}'."
            )
            
            # Reload sounds
            self.load_sounds()
        
        def on_download_error(error_message):
            progress_dialog.reject()
            
            QMessageBox.critical(
                self,
                "Download Error",
                f"Failed to download: {error_message}"
            )
        
        download_thread.finished_signal.connect(on_download_finished)
        download_thread.error_signal.connect(on_download_error)
        
        # Start thread
        download_thread.start()
        
        # Show dialog (non-modal)
        progress_dialog.setModal(True)
        progress_dialog.exec()
    
    def show_sound_context_menu(self, pos, index):
        # Get the button that was right-clicked
        button = self.sender()
        
        # Create context menu
        menu = QMenu(self)
        
        # Play action
        play_action = QAction("Play", self)
        play_action.triggered.connect(lambda: self.toggle_sound(index))
        menu.addAction(play_action)
        
        # Rename action
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.rename_sound(index))
        menu.addAction(rename_action)
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_sound(index))
        menu.addAction(delete_action)
        
        # Add separator
        menu.addSeparator()
        
        # Toggle favorite action
        is_favorite = str(index) in self.favorites
        favorite_text = "Remove from Favorites" if is_favorite else "Add to Favorites"
        favorite_action = QAction(favorite_text, self)
        favorite_action.triggered.connect(lambda: self.toggle_favorite(index))
        menu.addAction(favorite_action)
        
        # Hotkey submenu
        hotkey_menu = QMenu("Assign Hotkey", self)
        
        # Numeric keys (1-9)
        for i in range(1, 10):
            key_text = f"{i}"
            key_action = QAction(key_text, self)
            key_action.triggered.connect(lambda checked, key=i-1: self.assign_hotkey(index, key))
            hotkey_menu.addAction(key_action)
        
        # Function keys (F1-F12)
        hotkey_menu.addSeparator()
        for i in range(1, 13):
            key_text = f"F{i}"
            key_action = QAction(key_text, self)
            key_action.triggered.connect(lambda checked, key=i+8: self.assign_hotkey(index, key))
            hotkey_menu.addAction(key_action)
        
        # Clear hotkey option
        if any(str(value) == str(index) for value in self.hotkeys.values()):
            hotkey_menu.addSeparator()
            clear_action = QAction("Clear Hotkey", self)
            clear_action.triggered.connect(lambda: self.clear_hotkey(index))
            hotkey_menu.addAction(clear_action)
        
        menu.addMenu(hotkey_menu)
        
        # Show the menu at the right-clicked position
        menu.exec(button.mapToGlobal(pos))
    
    def rename_sound(self, index):
        if index < 0 or index >= len(self.sounds):
            return
        
        # Get current sound data
        sound_data = self.sounds[index]
        current_name = sound_data['name']
        
        # Prompt for new name
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Sound",
            "Enter new name:",
            text=current_name
        )
        
        if not ok or not new_name or new_name == current_name:
            return
        
        # Get current file path
        current_path = sound_data['path']
        
        # Create new file path
        file_ext = os.path.splitext(current_path)[1]
        new_path = os.path.join(os.path.dirname(current_path), new_name + file_ext)
        
        try:
            # Rename the file
            os.rename(current_path, new_path)
            
            # Reload sounds
            self.load_sounds()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rename sound: {str(e)}")
    
    def delete_sound(self, index):
        if index < 0 or index >= len(self.sounds):
            return
        
        # Get sound data
        sound_data = self.sounds[index]
        sound_name = sound_data['name']
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{sound_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Get file path
        file_path = sound_data['path']
        
        # Delete file
        if delete_file_safely(file_path):
            # Remove from favorites and hotkeys
            self.remove_from_favorites(index)
            self.clear_hotkey(index)
            
            # Reload sounds
            self.load_sounds()
        else:
            QMessageBox.critical(self, "Error", f"Failed to delete '{sound_name}'.")
    
    def load_favorites(self):
        # Get favorites file path
        favorites_path = get_tab_favorites_path(self.tab_name)
        
        # Load favorites data
        favorites_data = load_json(favorites_path)
        
        # Set favorites and hotkeys
        self.favorites = favorites_data.get('favorites', {})
        self.hotkeys = favorites_data.get('hotkeys', {})
    
    def save_favorites(self):
        # Get favorites file path
        favorites_path = get_tab_favorites_path(self.tab_name)
        
        # Create favorites data
        favorites_data = {
            'favorites': self.favorites,
            'hotkeys': self.hotkeys
        }
        
        # Save favorites data
        save_json(favorites_path, favorites_data)
    
    def toggle_favorite(self, index):
        # Convert index to string for JSON compatibility
        index_str = str(index)
        
        if index_str in self.favorites:
            # Remove from favorites
            del self.favorites[index_str]
            
            # Update button styling
            if 0 <= index < len(self.buttons):
                self.buttons[index].set_favorite(False)
        else:
            # Add to favorites
            self.favorites[index_str] = True
            
            # Update button styling
            if 0 <= index < len(self.buttons):
                self.buttons[index].set_favorite(True)
        
        # Save favorites
        self.save_favorites()
    
    def remove_from_favorites(self, index):
        # Convert index to string for JSON compatibility
        index_str = str(index)
        
        if index_str in self.favorites:
            # Remove from favorites
            del self.favorites[index_str]
            
            # Update button styling
            if 0 <= index < len(self.buttons):
                self.buttons[index].set_favorite(False)
            
            # Save favorites
            self.save_favorites()
    
    def assign_hotkey(self, sound_index, hotkey_index):
        # Convert indices to strings for JSON compatibility
        sound_index_str = str(sound_index)
        hotkey_index_str = str(hotkey_index)
        
        # Check if any other sound is using this hotkey
        for key, value in list(self.hotkeys.items()):
            if value == hotkey_index_str:
                # Remove existing assignment
                del self.hotkeys[key]
        
        # Assign hotkey
        self.hotkeys[hotkey_index_str] = sound_index_str
        
        # Save favorites
        self.save_favorites()
        
        # Reload buttons to update the text
        self.create_sound_buttons()
    
    def clear_hotkey(self, sound_index):
        # Convert index to string for JSON compatibility
        sound_index_str = str(sound_index)
        
        # Find and remove hotkey assignment
        for key, value in list(self.hotkeys.items()):
            if value == sound_index_str:
                del self.hotkeys[key]
        
        # Save favorites
        self.save_favorites()
        
        # Reload buttons to update the text
        self.create_sound_buttons()
    
    def cleanup(self):
        # Stop any loading thread
        if hasattr(self, 'load_thread') and self.load_thread.isRunning():
            self.load_thread.terminate()
            self.load_thread.wait() 