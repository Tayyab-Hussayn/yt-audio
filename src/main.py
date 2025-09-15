#!/usr/bin/env python3

import click
import time
import threading
import signal
import sys

try:
    # Try relative imports first (when run as module)
    from .extractor import YouTubeExtractor
    from .ui import PlayerUI
    try:
        from .player import AudioPlayer
    except ImportError:
        print("VLC not available, using pygame backend...")
        from .pygame_player import AudioPlayer
except ImportError:
    # Fall back to absolute imports (when run directly)
    from extractor import YouTubeExtractor
    from ui import PlayerUI
    try:
        from player import AudioPlayer
    except ImportError:
        print("VLC not available, using pygame backend...")
        from pygame_player import AudioPlayer


class YouTubeAudioCLI:
    def __init__(self):
        self.extractor = YouTubeExtractor()
        self.player = AudioPlayer()
        self.ui = PlayerUI()
        self.running = True
        self.current_volume = 70
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.ui.console.print("\n[yellow]Shutting down...[/yellow]")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        self.player.cleanup()
    
    def monitor_playback(self):
        """Monitor playback progress in background thread"""
        while self.running:
            if self.player.get_state() == 'playing':
                current_time = self.player.get_time()
                total_time = self.player.get_length()
                position = self.player.get_position()
                
                if total_time > 0:
                    # Update the UI with progress
                    self.ui.update_progress(current_time, total_time, position)
                
                # Check if playback ended
                if self.player.get_state() == 'ended':
                    self.ui.console.print("\n[green]✅ Playback finished![/green]")
                    break
                    
            time.sleep(2)  # Update every 2 seconds to avoid too frequent refreshes
    
    def handle_text_input(self):
        """Handle basic text input controls"""
        try:
            while self.running and self.player.get_state() not in ['stopped', 'ended']:
                self.ui.console.print("\n[dim]Press 'p' to pause/play, 'q' to quit, 'n' for next:[/dim]")
                user_input = input().lower().strip()
                
                if user_input == 'p':
                    self.player.pause()
                    state = self.player.get_state()
                    self.ui.show_state(state)
                elif user_input == 'q':
                    self.running = False
                    break
                elif user_input == 'n':
                    self.player.stop()
                    break
        except KeyboardInterrupt:
            self.running = False
    
    def play_url(self, url: str) -> bool:
        """Play a single YouTube URL"""
        try:
            # Extract audio information
            self.ui.show_loading("Extracting audio stream...")
            audio_info = self.extractor.extract_audio_info(url)
            
            if not audio_info:
                self.ui.show_error("Failed to extract audio stream")
                return False
            
            # Load stream
            self.ui.show_loading("Loading stream...")
            if not self.player.load_stream(audio_info['stream_url'], audio_info):
                self.ui.show_error("Failed to load audio stream")
                return False
            
            # Set initial volume
            self.player.set_volume(self.current_volume)
            
            # Start playback
            self.ui.show_loading("Starting playback...")
            if not self.player.play():
                self.ui.show_error("Failed to start playback")
                return False
            
            # Wait for stream to be ready
            if not self.player.wait_for_ready():
                self.ui.show_error("Stream failed to load properly")
                return False
            
            # Show now playing info
            self.ui.clear()
            self.ui.show_now_playing(audio_info['title'], audio_info.get('uploader', 'Unknown'))
            self.ui.print_separator()
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_playback, daemon=True)
            monitor_thread.start()
            
            # Start input thread for basic text controls
            input_thread = threading.Thread(target=self.handle_text_input, daemon=True)
            input_thread.start()
            
            # Wait for playback to finish or user to quit
            while self.running and self.player.get_state() not in ['stopped', 'ended', 'error']:
                time.sleep(0.5)
            
            return True
            
        except Exception as e:
            self.ui.show_error(f"Unexpected error: {str(e)}")
            return False
    
    def run(self):
        """Main application loop"""
        # Set up signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            self.ui.clear()
            self.ui.show_welcome()
            
            while self.running:
                try:
                    # Get URL from user
                    url = self.ui.get_url_input()
                    
                    if not url:
                        continue
                    
                    if url.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    # Validate URL
                    if not self.extractor.is_valid_youtube_url(url):
                        self.ui.show_error("Invalid YouTube URL. Please try again.")
                        continue
                    
                    # Play the URL
                    success = self.play_url(url)
                    
                    if success:
                        self.ui.print_separator()
                        if not self.ui.ask_continue():
                            break
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.ui.show_error(f"Unexpected error: {str(e)}")
        
        finally:
            self.cleanup()
            self.ui.show_goodbye()


@click.command()
@click.option('--url', '-u', help='YouTube URL to play directly')
@click.option('--volume', '-v', default=70, help='Initial volume (0-100)')
def main(url, volume):
    """YouTube Audio CLI Player - Stream YouTube videos as audio"""
    
    app = YouTubeAudioCLI()
    app.current_volume = max(0, min(100, volume))
    
    if url:
        # Direct URL mode
        if not app.extractor.is_valid_youtube_url(url):
            app.ui.show_error("Invalid YouTube URL")
            return
        
        app.ui.clear()
        app.ui.show_welcome()
        app.play_url(url)
    else:
        # Interactive mode
        app.run()


if __name__ == "__main__":
    main()
