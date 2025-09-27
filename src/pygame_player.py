import pygame
import threading
import time
import subprocess
import os
import tempfile
from typing import Optional, Dict


class AudioPlayer:
    def __init__(self):
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
        pygame.mixer.init()
        self.current_media_info = None
        self.is_playing = False
        self.is_paused = False
        self.temp_file = None
        self.download_process = None
        self.start_time = 0
        self.pause_time = 0
        
    def load_stream(self, stream_url: str, media_info: Dict) -> bool:
        """Download and load audio stream for playback using yt-dlp"""
        try:
            # Create temporary file
            self.temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_path = self.temp_file.name
            self.temp_file.close()
            
            # Use the original URL from media_info if available
            original_url = media_info.get('original_url', stream_url)
            
            # Download using yt-dlp to temporary file with flexible format
            cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '0',  # Best quality available
                '-o', temp_path.replace('.mp3', '.%(ext)s'),
                '--no-warnings',
                '--ignore-errors',
                original_url if original_url.startswith('http') else stream_url
            ]
            
            print("Downloading audio...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"yt-dlp error: {result.stderr}")
                # Try alternative method
                return self._try_alternative_download(stream_url, temp_path, media_info)
            
            # Find the actual downloaded file
            actual_file = self._find_downloaded_file(temp_path)
            
            if not actual_file:
                print("Downloaded file not found, trying alternative...")
                return self._try_alternative_download(stream_url, temp_path, media_info)
            
            # Load into pygame
            pygame.mixer.music.load(actual_file)
            self.current_media_info = media_info
            self.temp_file = actual_file
            
            return True
            
        except Exception as e:
            print(f"Error loading stream: {str(e)}")
            return False
    
    def _find_downloaded_file(self, base_path):
        """Find the actual downloaded file"""
        base_without_ext = base_path.replace('.mp3', '')
        possible_extensions = ['.mp3', '.m4a', '.webm', '.opus', '.ogg']
        
        for ext in possible_extensions:
            file_path = base_without_ext + ext
            if os.path.exists(file_path):
                return file_path
        return None
    
    def _try_alternative_download(self, stream_url, temp_path, media_info):
        """Try alternative download method"""
        try:
            # Try with different options
            cmd = [
                'yt-dlp',
                '--format', 'bestaudio/best',
                '-o', temp_path.replace('.mp3', '.%(ext)s'),
                '--no-warnings',
                stream_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                actual_file = self._find_downloaded_file(temp_path)
                if actual_file and os.path.exists(actual_file):
                    pygame.mixer.music.load(actual_file)
                    self.current_media_info = media_info
                    self.temp_file = actual_file
                    return True
            
            return False
            
        except Exception as e:
            print(f"Alternative download failed: {e}")
            return False
    
    def play(self) -> bool:
        """Start playback"""
        try:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                pygame.mixer.music.play()
                self.start_time = time.time()
            
            self.is_playing = True
            return True
        except Exception as e:
            print(f"Error playing: {str(e)}")
            return False
    
    def pause(self):
        """Pause/unpause playback"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.pause_time = time.time()
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
    
    def stop(self):
        """Stop playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        
        # Clean up temporary file
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.unlink(self.temp_file)
            except:
                pass
    
    def set_volume(self, volume: int):
        """Set volume (0-100)"""
        pygame.mixer.music.set_volume(volume / 100.0)
    
    def get_volume(self) -> int:
        """Get current volume"""
        return int(pygame.mixer.music.get_volume() * 100)
    
    def get_state(self) -> str:
        """Get player state"""
        if not pygame.mixer.music.get_busy() and self.is_playing:
            return 'ended'
        elif self.is_paused:
            return 'paused'
        elif self.is_playing:
            return 'playing'
        else:
            return 'stopped'
    
    def get_position(self) -> float:
        """Get current position (0.0 - 1.0) - approximate"""
        if not self.current_media_info or not self.is_playing:
            return 0.0
        
        duration = self.current_media_info.get('duration', 0)
        if duration <= 0:
            return 0.0
        
        elapsed = time.time() - self.start_time
        return min(1.0, elapsed / duration)
    
    def get_time(self) -> int:
        """Get current time in milliseconds - approximate"""
        if not self.is_playing:
            return 0
        
        elapsed = time.time() - self.start_time
        return int(elapsed * 1000)
    
    def get_length(self) -> int:
        """Get total length in milliseconds"""
        if not self.current_media_info:
            return 0
        
        duration = self.current_media_info.get('duration', 0)
        return int(duration * 1000)
    
    def format_time(self, ms: int) -> str:
        """Format time from milliseconds to MM:SS"""
        if ms < 0:
            return "00:00"
        
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_media_info(self) -> Optional[Dict]:
        """Get current media information"""
        return self.current_media_info
    
    def is_stream_ready(self) -> bool:
        """Check if stream is ready for playback"""
        return self.current_media_info is not None
    
    def wait_for_ready(self, timeout: int = 30) -> bool:
        """Wait for stream to be ready (file to be downloaded)"""
        return self.is_stream_ready()
    
    def cleanup(self):
        """Clean up resources"""
        self.stop()
        pygame.mixer.quit()
