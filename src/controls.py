import threading
import time
import sys
import termios
import tty
import select
from typing import Callable, Dict


class KeyboardController:
    def __init__(self):
        self.running = False
        self.key_handlers = {}
        self.listener_thread = None
        self.old_settings = None
        
    def register_key(self, key: str, handler: Callable):
        """Register a key handler"""
        self.key_handlers[key.lower()] = handler
    
    def start(self):
        """Start the keyboard listener"""
        if self.running:
            return
        
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()
    
    def stop(self):
        """Stop the keyboard listener"""
        self.running = False
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def _listen_loop(self):
        """Main listening loop using raw terminal input"""
        try:
            # Save terminal settings
            self.old_settings = termios.tcgetattr(sys.stdin)
            # Set raw mode
            tty.cbreak(sys.stdin.fileno())
            
            while self.running:
                # Check if input is available
                if select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
                    key = sys.stdin.read(1).lower()
                    
                    # Handle special keys
                    if key == ' ':
                        key = 'space'
                    elif key == '\x1b':  # ESC sequence
                        continue
                    elif key == '\r' or key == '\n':
                        continue
                    elif key == '\x03':  # Ctrl+C
                        key = 'ctrl+c'
                    
                    # Call handler if registered
                    if key in self.key_handlers:
                        try:
                            self.key_handlers[key]()
                        except Exception as e:
                            print(f"\nError handling key '{key}': {e}")
                
                time.sleep(0.01)  # Small delay to prevent high CPU usage
                
        except Exception as e:
            print(f"Keyboard listener error: {e}")
        finally:
            # Restore terminal settings
            if self.old_settings:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)


class PlayerControls:
    def __init__(self, player, ui):
        self.player = player
        self.ui = ui
        self.keyboard = KeyboardController()
        self.volume = 70
        self.setup_controls()
    
    def setup_controls(self):
        """Setup all keyboard controls"""
        self.keyboard.register_key('space', self.toggle_play_pause)
        self.keyboard.register_key('p', self.toggle_play_pause)
        self.keyboard.register_key('q', self.quit_player)
        self.keyboard.register_key('n', self.next_track)
        self.keyboard.register_key('s', self.stop_playback)
        self.keyboard.register_key('+', self.volume_up)
        self.keyboard.register_key('=', self.volume_up)
        self.keyboard.register_key('-', self.volume_down)
        self.keyboard.register_key('m', self.toggle_mute)
        self.keyboard.register_key('r', self.restart_track)
        self.keyboard.register_key('h', self.show_help)
        self.keyboard.register_key('ctrl+c', self.quit_player)
    
    def start_listening(self):
        """Start keyboard listening"""
        self.keyboard.start()
        self.show_controls_info()
    
    def stop_listening(self):
        """Stop keyboard listening"""
        self.keyboard.stop()
    
    def toggle_play_pause(self):
        """Toggle play/pause"""
        self.player.pause()
        state = self.player.get_state()
        if state == 'playing':
            self.ui.console.print("\n[green]▶️  Playing[/green]")
        elif state == 'paused':
            self.ui.console.print("\n[yellow]⏸️  Paused[/yellow]")
        else:
            self.ui.console.print(f"\n[blue]● {state.title()}[/blue]")
    
    def quit_player(self):
        """Quit the application"""
        self.ui.console.print("\n[red]👋 Goodbye![/red]")
        self.player.stop()
        self.stop_listening()
        # Set a flag that main app can check
        if hasattr(self, '_quit_callback'):
            self._quit_callback()
    
    def next_track(self):
        """Skip to next track"""
        self.ui.console.print("\n[blue]⏭️  Next track...[/blue]")
        self.player.stop()
    
    def stop_playback(self):
        """Stop current playback"""
        self.ui.console.print("\n[red]⏹️  Stopped[/red]")
        self.player.stop()
    
    def volume_up(self):
        """Increase volume"""
        self.volume = min(100, self.volume + 10)
        self.player.set_volume(self.volume)
        self.ui.console.print(f"\n[cyan]🔊 Volume: {self.volume}%[/cyan]")
    
    def volume_down(self):
        """Decrease volume"""
        self.volume = max(0, self.volume - 10)
        self.player.set_volume(self.volume)
        self.ui.console.print(f"\n[cyan]🔉 Volume: {self.volume}%[/cyan]")
    
    def toggle_mute(self):
        """Toggle mute"""
        current_vol = self.player.get_volume()
        if current_vol > 0:
            self._saved_volume = current_vol
            self.player.set_volume(0)
            self.ui.console.print("\n[red]🔇 Muted[/red]")
        else:
            restore_vol = getattr(self, '_saved_volume', self.volume)
            self.player.set_volume(restore_vol)
            self.ui.console.print(f"\n[green]🔊 Unmuted - Volume: {restore_vol}%[/green]")
    
    def restart_track(self):
        """Restart current track"""
        self.ui.console.print("\n[blue]🔄 Restarting track...[/blue]")
        # Note: This would need player support to restart from beginning
        self.ui.console.print("[dim](Restart not implemented for streaming)[/dim]")
    
    def show_help(self):
        """Show help/controls"""
        help_text = """
[bold cyan]🎵 Keyboard Controls:[/bold cyan]
[green]Space/P[/green] - Play/Pause
[red]Q[/red] - Quit
[blue]N[/blue] - Next track
[yellow]S[/yellow] - Stop
[cyan]+/=[/cyan] - Volume up
[cyan]-[/cyan] - Volume down
[magenta]M[/magenta] - Mute/Unmute
[dim]R[/dim] - Restart (not available)
[dim]H[/dim] - Show this help
"""
        self.ui.console.print(help_text)
    
    def show_controls_info(self):
        """Show initial controls information"""
        self.ui.console.print("\n[green]✅ Keyboard controls active![/green]")
        self.ui.console.print("[dim]Press 'H' for help, 'Q' to quit[/dim]")
    
    def set_quit_callback(self, callback):
        """Set callback for quit action"""
        self._quit_callback = callback
    
    def set_volume(self, volume: int):
        """Set initial volume"""
        self.volume = max(0, min(100, volume))
        self.player.set_volume(self.volume)
