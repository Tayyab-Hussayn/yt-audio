import vlc
import time
import threading
from typing import Optional, Dict


class AudioPlayer:
    def __init__(self):
        self.instance = vlc.Instance('--intf', 'dummy', '--extraintf', 'http')
        self.player = self.instance.media_player_new()
        self.current_media_info = None
        self.is_playing = False
        self.position = 0
        self.length = 0
    
    def load_stream(self, stream_url: str, media_info: Dict) -> bool:
        """Load audio stream for playback"""
        try:
            # If we have the original URL, try to use it directly with VLC
            original_url = media_info.get('original_url', stream_url)
            
            # VLC can sometimes handle YouTube URLs directly
            if original_url.startswith('http') and 'youtube.com' in original_url:
                media = self.instance.media_new(original_url)
            else:
                media = self.instance.media_new(stream_url)
                
            self.player.set_media(media)
            self.current_media_info = media_info
            
            print(f"VLC loaded stream: {media_info.get('title', 'Unknown')}")
            return True
            
        except Exception as e:
            print(f"Error loading stream with VLC: {str(e)}")
            return False
    
    def play(self) -> bool:
        """Start playback"""
        try:
            result = self.player.play()
            if result == 0:  # VLC returns 0 on success
                self.is_playing = True
                return True
            return False
        except Exception as e:
            print(f"Error playing: {str(e)}")
            return False
    
    def pause(self):
        """Pause playback"""
        self.player.pause()
        self.is_playing = not self.is_playing
    
    def stop(self):
        """Stop playback"""
        self.player.stop()
        self.is_playing = False
    
    def set_volume(self, volume: int):
        """Set volume (0-100)"""
        self.player.audio_set_volume(max(0, min(100, volume)))
    
    def get_volume(self) -> int:
        """Get current volume"""
        return self.player.audio_get_volume()
    
    def get_state(self) -> str:
        """Get player state"""
        state = self.player.get_state()
        state_map = {
            vlc.State.NothingSpecial: 'idle',
            vlc.State.Opening: 'opening',
            vlc.State.Buffering: 'buffering',
            vlc.State.Playing: 'playing',
            vlc.State.Paused: 'paused',
            vlc.State.Stopped: 'stopped',
            vlc.State.Ended: 'ended',
            vlc.State.Error: 'error'
        }
        return state_map.get(state, 'unknown')
    
    def get_position(self) -> float:
        """Get current position (0.0 - 1.0)"""
        return self.player.get_position()
    
    def get_time(self) -> int:
        """Get current time in milliseconds"""
        return self.player.get_time()
    
    def get_length(self) -> int:
        """Get total length in milliseconds"""
        return self.player.get_length()
    
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
        state = self.get_state()
        return state not in ['idle', 'opening', 'error']
    
    def wait_for_ready(self, timeout: int = 10) -> bool:
        """Wait for stream to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_stream_ready():
                return True
            time.sleep(0.1)
        return False
    
    def cleanup(self):
        """Clean up resources"""
        self.stop()
        self.player.release()
        self.instance.release()
