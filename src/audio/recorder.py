import os
import platform
import threading
import time
import subprocess
import wave
import tempfile
import random
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QSizePolicy,
    QSlider, QMessageBox, QFileDialog, QLineEdit, QInputDialog
)
from PyQt6.QtGui import QIcon, QColor, QFont
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread

from src.constants import APP_STYLE
from src.ui.components import WaveformVisualizer
from src.audio.audio_utils import get_default_audio_device
from src.utils.logger import logger

class RecordingThread(QThread):
    status_signal = pyqtSignal(str)
    time_signal = pyqtSignal(int)
    level_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, audio_device, system, max_seconds=60):
        super().__init__()
        self.audio_device = audio_device
        self.system = system
        self.max_seconds = max_seconds
        self.temp_file = None
        self.process = None
        self.stop_flag = False
        self.record_seconds = 0

    def run(self):
        try:
            # Create temporary file for recording
            temp_dir = tempfile.gettempdir()
            temp_name = f"recording_{int(time.time())}_{random.randint(1000, 9999)}.wav"
            self.temp_file = os.path.join(temp_dir, temp_name)
            
            logger.info(f"Starting audio recording to {self.temp_file}")
            self.status_signal.emit("Starting recording...")
            
            # Set up recording command based on platform
            if self.system == "Windows":
                # On Windows, use FFmpeg with DirectShow
                cmd = [
                    "ffmpeg",
                    "-f", "dshow",
                    "-audio_buffer_size", "50",
                    "-i", f"audio={self.audio_device}",
                    "-y",  # Overwrite output file
                    "-acodec", "pcm_s16le",
                    "-ar", "44100",
                    "-ac", "2",
                    self.temp_file
                ]
            else:
                # On Linux, use ALSA/Pulse
                if "default" in self.audio_device.lower():
                    # Use default ALSA device
                    cmd = [
                        "ffmpeg",
                        "-f", "alsa",
                        "-i", "default",
                        "-y",
                        "-acodec", "pcm_s16le",
                        "-ar", "44100",
                        "-ac", "2",
                        self.temp_file
                    ]
                else:
                    # Use pulse audio
                    cmd = [
                        "ffmpeg",
                        "-f", "pulse",
                        "-i", "default",
                        "-y",
                        "-acodec", "pcm_s16le",
                        "-ar", "44100",
                        "-ac", "2",
                        self.temp_file
                    ]
            
            # Start FFmpeg recording process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.status_signal.emit("Recording started")
            
            # Monitor recording and update time/level
            self.record_seconds = 0
            start_time = time.time()
            
            while not self.stop_flag and self.record_seconds < self.max_seconds:
                # Sleep to allow time to process
                time.sleep(0.1)
                
                # Update recording duration
                self.record_seconds = int(time.time() - start_time)
                self.time_signal.emit(self.record_seconds)
                
                # Generate a pseudo-random audio level for visual feedback
                # In a real app, we'd analyze the audio buffer, but this is simpler
                base_level = 30
                variation = random.randint(0, 40)
                # Higher variations more likely when recording longer
                probability = min(80, self.record_seconds * 2)
                spike = random.randint(0, 100) < probability
                
                if spike:
                    level = base_level + variation
                else:
                    level = base_level + (variation // 2)
                
                self.level_signal.emit(level)
                
                # Check if process is still running
                if self.process.poll() is not None:
                    if self.process.returncode != 0:
                        stderr = self.process.stderr.read()
                        self.error_signal.emit(f"Recording failed: {stderr}")
                        return
                    break
            
            # If we reached max time, stop recording
            if self.record_seconds >= self.max_seconds:
                self.status_signal.emit("Maximum recording time reached")
                self.stop_recording()
            
            # Signal completion
            if os.path.exists(self.temp_file):
                self.finished_signal.emit(self.temp_file)
            else:
                self.error_signal.emit("Recording file not found")
        
        except Exception as e:
            logger.error(f"Recording error: {str(e)}", exc_info=True)
            self.error_signal.emit(f"Recording error: {str(e)}")
    
    def stop_recording(self):
        self.stop_flag = True
        if self.process and self.process.poll() is None:
            logger.debug("Stopping recording process")
            # Try to gracefully stop FFmpeg
            if platform.system() == "Windows":
                # Windows needs to use taskkill
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.process.pid)])
            else:
                # Send SIGTERM on Unix
                self.process.terminate()
                self.process.wait(timeout=2)
                
                # Force kill if still running
                if self.process.poll() is None:
                    self.process.kill()
            logger.debug("Recording process stopped")

class PlaybackThread(QThread):
    finished_signal = pyqtSignal()
    level_signal = pyqtSignal(int)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.stop_flag = False

    def run(self):
        try:
            # Start playback using FFmpeg
            cmd = [
                "ffplay",
                "-nodisp",  # No display window
                "-autoexit",  # Exit when done
                "-i", self.file_path
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Simulate audio levels during playback
            # Get duration of the audio file
            duration = 0
            try:
                with wave.open(self.file_path, 'rb') as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate)
            except:
                # Fallback to a default duration
                duration = 10
            
            start_time = time.time()
            
            while not self.stop_flag:
                # Sleep to allow time to process
                time.sleep(0.05)
                
                # Generate random audio level for visualization
                level = random.randint(20, 80)
                self.level_signal.emit(level)
                
                # Check if playback completed
                if process.poll() is not None or (time.time() - start_time) >= duration:
                    break
            
            # Ensure process is terminated
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=1)
            
            self.finished_signal.emit()
            
        except Exception as e:
            print(f"Playback error: {str(e)}")
            self.finished_signal.emit()
    
    def stop_playback(self):
        self.stop_flag = True

class RecorderDialog(QDialog):
    def __init__(self, parent, tab_dir):
        super().__init__(parent)
        self.parent = parent
        self.tab_dir = tab_dir
        self.recording_file = None
        self.recording_thread = None
        self.playback_thread = None
        self.is_recording = False
        self.is_playing = False
        self.recorded_seconds = 0
        self.temp_file = None
        
        logger.debug(f"Opening RecorderDialog for tab directory: {tab_dir}")
        
        # Set window properties
        self.setWindowTitle("Record Sound")
        self.setMinimumSize(500, 350)
        self.setModal(True)
        
        # Apply app style
        self.setStyleSheet(f"""
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
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 {APP_STYLE['primary_color']}, 
                                          stop:1 {APP_STYLE['secondary_color']});
                color: {APP_STYLE['text_color']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 {APP_STYLE['secondary_color']}, 
                                          stop:1 {APP_STYLE['primary_color']});
            }}
            QPushButton:pressed {{
                background: {APP_STYLE['secondary_color']};
            }}
            QPushButton:disabled {{
                background: #444444;
                color: #888888;
            }}
            QLineEdit {{
                background-color: #252535;
                color: {APP_STYLE['text_color']};
                border: 1px solid #444455;
                border-radius: 4px;
                padding: 6px;
            }}
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Status label
        self.status_label = QLabel("Ready to record")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont(APP_STYLE["font_family"], 12, QFont.Weight.Bold))
        layout.addWidget(self.status_label)
        
        # Time display
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont(APP_STYLE["font_family"], 24, QFont.Weight.Bold))
        self.time_label.setStyleSheet(f"color: {APP_STYLE['accent_color']};")
        layout.addWidget(self.time_label)
        
        # Waveform visualizer
        self.waveform = WaveformVisualizer(self)
        self.waveform.setMinimumHeight(80)
        layout.addWidget(self.waveform)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Record button
        self.record_button = QPushButton("Record")
        self.record_button.setMinimumHeight(50)
        self.record_button.setIcon(QIcon.fromTheme("media-record"))
        self.record_button.clicked.connect(self.toggle_recording)
        controls_layout.addWidget(self.record_button)
        
        # Play button
        self.play_button = QPushButton("Play")
        self.play_button.setMinimumHeight(50)
        self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.play_button.clicked.connect(self.play_recording)
        self.play_button.setEnabled(False)
        controls_layout.addWidget(self.play_button)
        
        layout.addLayout(controls_layout)
        
        # Sound name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Sound Name:"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter sound name")
        name_layout.addWidget(self.name_input)
        
        layout.addLayout(name_layout)
        
        # Save button
        save_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Sound")
        self.save_button.setMinimumHeight(50)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_recording)
        save_layout.addWidget(self.save_button)
        
        layout.addLayout(save_layout)
        
        # Timer for updating the UI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        # Timer for waveform updates when not recording/playing
        self.waveform_timer = QTimer(self)
        self.waveform_timer.timeout.connect(self.update_waveform)
        self.waveform_timer.start(100)
        
        # Get default audio device
        self.audio_device = get_default_audio_device()
        self.system = platform.system()
    
    def update_timer(self):
        minutes = self.recorded_seconds // 60
        seconds = self.recorded_seconds % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def update_waveform(self):
        if not self.is_recording and not self.is_playing:
            # When idle, keep waveform in idle state
            self.waveform.set_playing(False)
    
    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        # Don't start if we're playing
        if self.is_playing:
            return
        
        # Reset state
        self.is_recording = True
        self.recorded_seconds = 0
        self.update_timer()
        self.timer.start(1000)  # Update timer every second
        
        # Update UI
        self.record_button.setText("Stop")
        self.play_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.status_label.setText("Recording...")
        self.waveform.set_playing(True)
        
        # Start recording thread
        self.recording_thread = RecordingThread(
            self.audio_device,
            self.system,
            max_seconds=60  # 1 minute max
        )
        
        # Connect signals
        self.recording_thread.status_signal.connect(self.status_label.setText)
        self.recording_thread.time_signal.connect(self.update_recording_time)
        self.recording_thread.level_signal.connect(self.waveform.update_audio_level)
        self.recording_thread.finished_signal.connect(self.on_recording_finished)
        self.recording_thread.error_signal.connect(self.on_recording_error)
        
        # Start thread
        self.recording_thread.start()
    
    def update_recording_time(self, seconds):
        self.recorded_seconds = seconds
        self.update_timer()
    
    def on_recording_finished(self, file_path):
        self.recording_file = file_path
        self.is_recording = False
        self.timer.stop()
        
        # Update UI
        self.record_button.setText("Record")
        self.play_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.status_label.setText("Recording completed!")
        self.waveform.set_playing(False)
        
        # Suggest a default name
        if not self.name_input.text():
            self.name_input.setText(f"Recording_{time.strftime('%Y%m%d_%H%M%S')}")
    
    def on_recording_error(self, error_message):
        self.is_recording = False
        self.timer.stop()
        
        # Update UI
        self.record_button.setText("Record")
        self.status_label.setText(f"Error: {error_message}")
        self.waveform.set_playing(False)
        
        # Show error message
        QMessageBox.critical(self, "Recording Error", error_message)
    
    def stop_recording(self):
        if self.recording_thread and self.is_recording:
            self.status_label.setText("Stopping recording...")
            self.recording_thread.stop_recording()
    
    def play_recording(self):
        if not self.recording_file or not os.path.exists(self.recording_file):
            QMessageBox.warning(self, "Playback Error", "No recording available to play.")
            return
        
        if self.is_recording:
            return
        
        if self.is_playing:
            # Stop current playback
            self.playback_thread.stop_playback()
            self.is_playing = False
            self.play_button.setText("Play")
            self.waveform.set_playing(False)
            return
        
        # Start playback
        self.is_playing = True
        self.play_button.setText("Stop")
        self.status_label.setText("Playing recording...")
        self.waveform.set_playing(True)
        
        # Start playback thread
        self.playback_thread = PlaybackThread(self.recording_file)
        
        # Connect signals
        self.playback_thread.level_signal.connect(self.waveform.update_audio_level)
        self.playback_thread.finished_signal.connect(self.on_playback_finished)
        
        # Start thread
        self.playback_thread.start()
    
    def on_playback_finished(self):
        self.is_playing = False
        self.play_button.setText("Play")
        self.status_label.setText("Ready")
        self.waveform.set_playing(False)
    
    def save_recording(self):
        if not self.recording_file or not os.path.exists(self.recording_file):
            QMessageBox.warning(self, "Save Error", "No recording available to save.")
            return
        
        # Get name from input
        sound_name = self.name_input.text().strip()
        if not sound_name:
            QMessageBox.warning(self, "Save Error", "Please enter a name for the sound.")
            return
        
        # Create safe filename
        safe_name = "".join([c for c in sound_name if c.isalpha() or c.isdigit() or c in ' -_']).strip()
        if not safe_name:
            safe_name = f"Recording_{time.strftime('%Y%m%d_%H%M%S')}"
        
        # Create output path
        if not os.path.exists(self.tab_dir):
            os.makedirs(self.tab_dir, exist_ok=True)
        
        output_path = os.path.join(self.tab_dir, f"{safe_name}.wav")
        
        # Check if file already exists
        if os.path.exists(output_path):
            reply = QMessageBox.question(
                self, "File Exists",
                f"A sound named '{safe_name}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        try:
            # Copy the file
            with open(self.recording_file, 'rb') as src_file:
                with open(output_path, 'wb') as dst_file:
                    dst_file.write(src_file.read())
            
            QMessageBox.information(self, "Success", f"Sound '{safe_name}' saved successfully!")
            self.accept()  # Close dialog with success
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save recording: {str(e)}")
    
    def closeEvent(self, event):
        # Clean up resources
        if self.is_recording:
            self.recording_thread.stop_recording()
        
        if self.is_playing and self.playback_thread:
            self.playback_thread.stop_playback()
        
        # Stop timers
        self.timer.stop()
        self.waveform_timer.stop()
        
        # Accept close event
        event.accept() 