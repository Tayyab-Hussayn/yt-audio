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
        self.keyboard_listener = None
        
    def setup_keyboard_listener(self):
        """Setup non-blocking keyboard listener"""
        try:
            from pynput import keyboard
            
            def on_press(key):
                try:
                    if key == keyboard.Key.space:
                        self.player.pause()
                        state = self.player.get_state()
                        self.ui.console.print(f"\n[yellow]● {state.upper()}[/yellow]")
                    elif key.char == 'q':
                        self.ui.console.print("\n[red]Quitting...[/red]")
                        self.running = False
                        self.player.stop()
                    elif key.char == 'n':
                        self.ui.console.print("\n[blue]Stopping current track...[/blue]")
                        self.player.stop()
                    elif key.char == '+' or key.char == '=':
                        self.current_volume = min(100, self.current_volume + 10)
                        self.player.set_volume(self.current_volume)
                        self.ui.console.print(f"\n[cyan]🔊 Volume: {self.current_volume}%[/cyan]")
                    elif key.char == '-':
                        self.current_volume = max(0, self.current_volume - 10)
                        self.player.set_volume(self.current_volume)
                        self.ui.console.print(f"\n[cyan]🔊 Volume: {self.current_volume}%[/cyan]")
                except AttributeError:
                    # Special keys (like space) don't have char attribute
                    pass
                except Exception as e:
                    # Ignore keyboard errors to prevent crashes
                    pass
            
            # Start the keyboard listener
            self.keyboard_listener = keyboard.Listener(on_press=on_press)
            self.keyboard_listener.start()
            return True
            
        except ImportError:
            self.ui.console.print("[yellow]Warning: pynput not available, keyboard controls disabled[/yellow]")
            return False
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.ui.console.print("\n[yellow]Shutting down...[/yellow]")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if hasattr(self, 'keyboard_listener') and self.keyboard_listener:
            self.keyboard_listener.stop()
        self.player.cleanup()
    
    def monitor_playback(self):
        """Monitor playback progress in background thread"""
        last_update = 0
        while self.running:
            state = self.player.get_state()
            
            if state == 'playing':
                current_time = self.player.get_time()
                total_time = self.player.get_length()
                
                # Update every 2 seconds to avoid spam
                if time.time() - last_update > 2:
                    if total_time > 0:
                        position = current_time / total_time
                        progress_bar = "█" * int(position * 30) + "░" * (30 - int(position * 30))
                        time_str = f"{self.ui.format_time(current_time)} / {self.ui.format_time(total_time)}"
                        
                        # Clear line and show progress
                        print(f"\r[{progress_bar}] {time_str} - {state}", end="", flush=True)
                        last_update = time.time()
                        
            elif state == 'ended':
                print(f"\n[green]✅ Playback finished![/green]")
                self.running = False
                break
            elif state == 'error':
                print(f"\n[red]❌ Playback error[/red]")
                break
                
            time.sleep(1)
    
    def handle_keyboard_input(self):
        """Display control instructions (keyboard listener handles actual input)"""
        if hasattr(self, 'keyboard_listener') and self.keyboard_listener:
            self.ui.console.print("\n[dim]Keyboard controls active: [Space]=Play/Pause [Q]=Quit [N]=Next [+/-]=Volume[/dim]")
        else:
            # Fallback to old method if pynput isn't available
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
            self.ui.show_controls()
            self.ui.show_volume(self.current_volume)
            self.ui.print_separator()
            
            # Setup keyboard controls
            controls_available = self.setup_controls()
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_playback, daemon=True)
            monitor_thread.start()
            
            # Start keyboard controls
            input_thread = threading.Thread(target=self.handle_keyboard_input, daemon=True)
            input_thread.start()
            
            if controls_available:
                self.ui.console.print("[green]✅ Press any key to control playback![/green]")
            
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
            self.ui.console.print("[green]Thanks for using YouTube Audio Player![/green]")


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
