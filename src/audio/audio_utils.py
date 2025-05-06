import platform
import subprocess
import pygame

# Try to import PyAudio if available (optional)
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

def initialize_audio():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
    pygame.mixer.set_num_channels(64)  # Allow more simultaneous sounds
    pygame.init()

def get_default_audio_device():
    system = platform.system()
    
    if system == "Windows":
        if PYAUDIO_AVAILABLE:
            try:
                p = pyaudio.PyAudio()
                info = p.get_default_input_device_info()
                device_name = info['name']
                p.terminate()
                return device_name
            except Exception:
                try:
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
                        return audio_devices[0]  # Return first device
                except:
                    pass
                
        # Default fallback for Windows
        return "Microphone (Realtek Audio)"
    else:
        # For Linux, we'll use default or pulse/alsa
        return "default"

def stop_all_sounds():
    pygame.mixer.stop()

def set_global_volume(volume):
    pygame.mixer.music.set_volume(volume / 100)
    for channel in range(pygame.mixer.get_num_channels()):
        if pygame.mixer.Channel(channel).get_busy():
            pygame.mixer.Channel(channel).set_volume(volume / 100) 