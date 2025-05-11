import os
import json
import time
import pygame
import subprocess
import concurrent.futures
import wave
from PyQt6.QtCore import QThread, pyqtSignal

try:
    from mutagen.mp3 import MP3
    from mutagen.oggvorbis import OggVorbis
except ImportError:
    MP3 = None
    OggVorbis = None

class LoadSoundsThread(QThread):
    loading_status_signal = pyqtSignal(str)
    loading_progress_signal = pyqtSignal(int)
    loading_finished_signal = pyqtSignal(list, bool)
    
    def __init__(self, tab_name):
        super().__init__()
        self.tab_name = tab_name
        
    def run(self):
        try:
            # Get data directory
            base_dir = os.path.join("sounds", self.tab_name)
            
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
                self.loading_status_signal.emit(f"Created new directory for tab '{self.tab_name}'")
                self.loading_finished_signal.emit([], True)
                return
            
            # Get all sound files in the directory
            sound_files = []
            for filename in os.listdir(base_dir):
                if filename.lower().endswith(('.wav', '.mp3', '.ogg')):
                    sound_files.append(filename)
            
            # If no sounds found
            if not sound_files:
                self.loading_status_signal.emit(f"No sound files found in tab '{self.tab_name}'")
                self.loading_finished_signal.emit([], True)
                return
            
            # Sort files
            sound_files.sort()
            
            # Begin loading sounds
            total_sounds = len(sound_files)
            self.loading_status_signal.emit(f"Loading {total_sounds} sounds...")
            
            # Container for loaded sounds
            sounds = []
            
            # Load sounds using thread pool for faster loading
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                # Create tasks
                future_to_file = {
                    executor.submit(self.load_single_sound, base_dir, filename): (filename, i) 
                    for i, filename in enumerate(sound_files)
                }
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_file):
                    filename, index = future_to_file[future]
                    try:
                        sound_data = future.result()
                        if sound_data:
                            sounds.append(sound_data)
                            
                            # Update progress
                            progress = int((len(sounds) / total_sounds) * 100)
                            self.loading_progress_signal.emit(progress)
                            self.loading_status_signal.emit(f"Loaded {len(sounds)}/{total_sounds} sounds...")
                    except Exception as e:
                        self.loading_status_signal.emit(f"Error loading {filename}: {str(e)}")
            
            # Final cleanup and sort by file name
            sounds.sort(key=lambda x: x['name'].lower())
            
            self.loading_status_signal.emit(f"Finished loading {len(sounds)} sounds")
            self.loading_finished_signal.emit(sounds, True)
            
        except Exception as e:
            self.loading_status_signal.emit(f"Error: {str(e)}")
            self.loading_finished_signal.emit([], False)
    
    def load_single_sound(self, base_dir, filename):
        full_path = os.path.join(base_dir, filename)
        
        # Get file creation time or modification time as fallback
        try:
            creation_time = os.path.getctime(full_path)
        except:
            creation_time = os.path.getmtime(full_path)
        
        # Get duration
        duration = ''
        try:
            if filename.lower().endswith('.wav'):
                with wave.open(full_path, 'rb') as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate)
            elif filename.lower().endswith('.mp3') and MP3:
                audio = MP3(full_path)
                duration = audio.info.length
            elif filename.lower().endswith('.ogg') and OggVorbis:
                audio = OggVorbis(full_path)
                duration = audio.info.length
        except Exception as e:
            duration = ''
        
        # Create sound data object
        sound_data = {
            'path': full_path,
            'name': os.path.splitext(filename)[0],  # Remove extension
            'creation_time': creation_time,
            'duration': duration
        }
        
        return sound_data

class YouTubeDownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, url, output_path, max_retries=3):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.max_retries = max_retries
        
    def run(self):
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            # Check if yt-dlp or youtube-dl is installed
            cmd = "yt-dlp"
            try:
                subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except:
                cmd = "youtube-dl"
                try:
                    subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                except:
                    self.error_signal.emit("Neither yt-dlp nor youtube-dl is installed!")
                    return
            
            # Set arguments for youtube downloader
            args = [
                cmd,
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",  # Best quality
                "--embed-thumbnail",  # Add thumbnail to audio file if possible
                "--add-metadata",  # Add metadata
                "--output", self.output_path + ".%(ext)s",  # Add extension automatically
                "--progress", "--newline",  # For progress parsing
                "--no-playlist",  # Avoid downloading playlists
                self.url
            ]
            
            # Start download process
            retries = 0
            self.progress_signal.emit(0)
            
            while retries < self.max_retries:
                try:
                    process = subprocess.Popen(
                        args, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=1
                    )
                    
                    # Monitor the download progress
                    current_progress = 0
                    for line in iter(process.stdout.readline, ''):
                        if "of" in line and "%" in line:
                            # Try to parse progress
                            try:
                                percent_part = line.split('%')[0].strip().split(' ')[-1]
                                percent = float(percent_part)
                                if percent > current_progress:
                                    current_progress = percent
                                    self.progress_signal.emit(int(percent))
                            except:
                                pass
                    
                    # Wait for process to complete
                    process.wait()
                    
                    if process.returncode == 0:
                        # Success
                        self.progress_signal.emit(100)
                        
                        # Find the downloaded file (might have a different extension)
                        result_file = None
                        base_dir = os.path.dirname(self.output_path)
                        base_name = os.path.basename(self.output_path)
                        
                        for filename in os.listdir(base_dir):
                            if filename.startswith(base_name) and filename.endswith('.mp3'):
                                result_file = os.path.join(base_dir, filename)
                                # Rename to ensure it doesn't have extra extensions
                                clean_path = self.output_path + '.mp3'
                                if result_file != clean_path:
                                    os.rename(result_file, clean_path)
                                    result_file = clean_path
                                break
                        
                        if not result_file:
                            self.error_signal.emit("Download completed but file not found!")
                            return
                        
                        # Emit the path to the downloaded file
                        self.finished_signal.emit(result_file)
                        return
                    else:
                        retries += 1
                        self.progress_signal.emit(0)  # Reset progress for retry
                
                except Exception as e:
                    retries += 1
                    self.progress_signal.emit(0)  # Reset progress for retry
                    time.sleep(1)  # Small delay before retrying
            
            # If we reach here, all retries failed
            self.error_signal.emit(f"Failed to download after {self.max_retries} attempts.")
            
        except Exception as e:
            self.error_signal.emit(f"Download error: {str(e)}")

class PlaylistDownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(int, str)
    retry_signal = pyqtSignal(int, str, int)
    skip_signal = pyqtSignal(int, str)
    error_signal = pyqtSignal(int, str, str)
    finished_signal = pyqtSignal(list)
    
    def __init__(self, playlist_items, tab_dir, add_prefix):
        super().__init__()
        self.playlist_items = playlist_items
        self.tab_dir = tab_dir
        self.add_prefix = add_prefix
        
    def run(self):
        results = []
        total_items = len(self.playlist_items)
        
        for i, item in enumerate(self.playlist_items):
            url = item['url']
            title = item['title']
            index = i + 1
            
            # Create safe filename from title
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c in ' -_']).strip()
            
            # Add index prefix if requested
            if self.add_prefix:
                filename = f"{index:02d} - {safe_title}"
            else:
                filename = safe_title
                
            # Output path
            output_path = os.path.join(self.tab_dir, filename)
            
            # Update status
            self.status_signal.emit(i, f"Downloading {index}/{total_items}: {title}")
            
            # Try to download
            success = False
            max_retries = 3
            retries = 0
            
            while not success and retries < max_retries:
                try:
                    # Create download command
                    cmd = "yt-dlp"
                    try:
                        subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    except:
                        cmd = "youtube-dl"
                        try:
                            subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                        except:
                            self.error_signal.emit(i, title, "Neither yt-dlp nor youtube-dl is installed!")
                            break
                    
                    args = [
                        cmd,
                        "--extract-audio",
                        "--audio-format", "mp3",
                        "--audio-quality", "0",
                        "--embed-thumbnail",
                        "--add-metadata",
                        "--output", output_path + ".%(ext)s",
                        "--progress", "--newline",
                        "--no-playlist",
                        url
                    ]
                    
                    # Start download
                    if retries > 0:
                        self.retry_signal.emit(i, title, retries)
                    
                    # Run download process
                    process = subprocess.Popen(
                        args, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=1
                    )
                    
                    # Track progress
                    for line in iter(process.stdout.readline, ''):
                        if "of" in line and "%" in line:
                            try:
                                percent_part = line.split('%')[0].strip().split(' ')[-1]
                                percent = float(percent_part)
                                self.progress_signal.emit(int(percent))
                            except:
                                pass
                    
                    # Wait for completion
                    process.wait()
                    
                    if process.returncode == 0:
                        success = True
                        self.progress_signal.emit(100)
                        
                        # Find the downloaded file
                        result_file = None
                        for filename in os.listdir(self.tab_dir):
                            if filename.startswith(os.path.basename(output_path)) and filename.endswith('.mp3'):
                                result_file = os.path.join(self.tab_dir, filename)
                                # Rename to ensure it has the correct name
                                clean_path = output_path + '.mp3'
                                if result_file != clean_path:
                                    os.rename(result_file, clean_path)
                                    result_file = clean_path
                                break
                        
                        if result_file:
                            results.append({
                                'path': result_file,
                                'name': os.path.splitext(os.path.basename(result_file))[0],
                                'creation_time': os.path.getctime(result_file)
                            })
                    else:
                        retries += 1
                
                except Exception as e:
                    retries += 1
                    time.sleep(1)
            
            # Handle failure
            if not success:
                self.skip_signal.emit(i, title)
        
        # All downloads complete
        self.finished_signal.emit(results) 