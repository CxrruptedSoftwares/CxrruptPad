import platform
import subprocess
import pygame
from src.utils.logger import logger

# Try to import PyAudio if available (optional)
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
    logger.debug("PyAudio is available")
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.debug("PyAudio is not available")

def initialize_audio():
    logger.info("Initializing pygame audio system")
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        pygame.mixer.set_num_channels(64)  # Allow more simultaneous sounds
        pygame.init()
        logger.info(f"Audio initialized successfully: {pygame.mixer.get_init()}")
    except Exception as e:
        logger.error(f"Failed to initialize audio: {str(e)}")
        raise

def get_default_audio_device():
    system = platform.system()
    logger.debug(f"Getting default audio device for {system}")
    
    if system == "Windows":
        if PYAUDIO_AVAILABLE:
            try:
                p = pyaudio.PyAudio()
                info = p.get_default_input_device_info()
                device_name = info['name']
                p.terminate()
                logger.debug(f"Found default audio device via PyAudio: {device_name}")
                return device_name
            except Exception as e:
                logger.debug(f"PyAudio device detection failed: {str(e)}")
                try:
                    logger.debug("Trying FFmpeg to detect audio devices")
                    devices_cmd = subprocess.Popen(
                        ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                    )
                    _, stderr = devices_cmd.communicate()
                    
                    audio_devices = []
                    capture_audio = False
                    for line in stderr.splitlines():
                        if "DirectShow audio devices" in line:
                            capture_audio = True
                            continue
                        if capture_audio and "Alternative name" not in line:
                            if "DirectShow video devices" in line:
                                break
                            if "]  \"" in line:
                                device_name = line.split("\"")[1]
                                audio_devices.append(device_name)
                    
                    if audio_devices:
                        logger.debug(f"Found audio devices via FFmpeg: {audio_devices}")
                        return audio_devices[0]  # Return first device
                except Exception as e:
                    logger.debug(f"FFmpeg device detection failed: {str(e)}")
                
        # Default fallback for Windows
        logger.debug("Using default fallback audio device for Windows")
        return "Microphone (Realtek Audio)"
    else:
        # For Linux, we'll use default or pulse/alsa
        logger.debug("Using default audio device for Linux")
        return "default"

def stop_all_sounds():
    logger.debug("Stopping all sounds")
    pygame.mixer.stop()

def set_global_volume(volume):
    logger.debug(f"Setting global volume to {volume}%")
    pygame.mixer.music.set_volume(volume / 100)
    for channel in range(pygame.mixer.get_num_channels()):
        if pygame.mixer.Channel(channel).get_busy():
            pygame.mixer.Channel(channel).set_volume(volume / 100) 