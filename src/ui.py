from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
import time


class PlayerUI:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        
    def clear(self):
        """Clear the console"""
        self.console.clear()
    
    def show_welcome(self):
        """Show welcome message"""
        welcome_text = Text("🎵 YouTube Audio Player", style="bold blue")
        welcome_panel = Panel(
            Align.center(welcome_text),
            title="Welcome",
            border_style="blue"
        )
        self.console.print(welcome_panel)
        self.console.print()
    
    def get_url_input(self) -> str:
        """Get YouTube URL from user"""
        return self.console.input("[bold green]Enter YouTube URL:[/bold green] ")
    
    def show_loading(self, message: str = "Loading..."):
        """Show loading message"""
        self.console.print(f"[yellow]⏳ {message}[/yellow]")
    
    def show_error(self, message: str):
        """Show error message"""
        error_panel = Panel(
            f"[bold red]❌ Error:[/bold red] {message}",
            border_style="red"
        )
        self.console.print(error_panel)
    
    def show_success(self, message: str):
        """Show success message"""
        self.console.print(f"[green]✅ {message}[/green]")
    
    def show_now_playing(self, title: str, uploader: str = "Unknown"):
        """Show now playing information"""
        now_playing_text = Text()
        now_playing_text.append("▶️  Now Playing: ", style="bold green")
        now_playing_text.append(f"{title}", style="bold white")
        if uploader != "Unknown":
            now_playing_text.append(f"\n👤 By: {uploader}", style="dim")
        
        panel = Panel(
            now_playing_text,
            title="Now Playing",
            border_style="green"
        )
        self.console.print(panel)
    
    def show_progress_bar(self, current_time: int, total_time: int, position: float = 0.0):
        """Show progress bar with time"""
        if total_time <= 0:
            return
        
        # Calculate progress
        progress_percent = int((current_time / total_time) * 100) if total_time > 0 else 0
        
        # Format times
        current_str = self.format_time(current_time)
        total_str = self.format_time(total_time)
        
        # Create progress bar
        bar_length = 50
        filled_length = int(bar_length * position)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        progress_text = f"⏱️  [{bar}] {current_str} / {total_str}"
        self.console.print(progress_text)
    
    def show_controls(self):
        """Show control instructions"""
        controls_text = Text()
        controls_text.append("Controls: ", style="bold")
        controls_text.append("[Space] ", style="bold yellow")
        controls_text.append("Play/Pause | ")
        controls_text.append("[Q] ", style="bold red")
        controls_text.append("Quit | ")
        controls_text.append("[N] ", style="bold blue")
        controls_text.append("Next URL | ")
        controls_text.append("[+/-] ", style="bold cyan")
        controls_text.append("Volume")
        
        panel = Panel(
            controls_text,
            title="Controls",
            border_style="cyan"
        )
        self.console.print(panel)
    
    def show_state(self, state: str):
        """Show current player state"""
        state_colors = {
            'playing': 'green',
            'paused': 'yellow',
            'stopped': 'red',
            'buffering': 'blue',
            'loading': 'blue',
            'error': 'red'
        }
        
        color = state_colors.get(state, 'white')
        state_text = f"[{color}]● {state.upper()}[/{color}]"
        self.console.print(state_text)
    
    def show_volume(self, volume: int):
        """Show current volume"""
        volume_bar = "█" * (volume // 10) + "░" * (10 - volume // 10)
        self.console.print(f"🔊 Volume: [{volume_bar}] {volume}%")
    
    def format_time(self, ms: int) -> str:
        """Format time from milliseconds to MM:SS"""
        if ms < 0:
            return "00:00"
        
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def print_separator(self):
        """Print a separator line"""
        self.console.print("─" * 60, style="dim")
    
    def ask_continue(self) -> bool:
        """Ask user if they want to continue"""
        response = self.console.input("\n[bold cyan]Play another video? (y/n):[/bold cyan] ")
        return response.lower().startswith('y')
