from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.columns import Columns
from rich.box import ROUNDED, HEAVY, DOUBLE, MINIMAL
import time


class PlayerUI:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.current_title = ""
        self.current_uploader = ""
        
    def clear(self):
        """Clear the console"""
        self.console.clear()
    
    def show_welcome(self):
        """Show welcome message with programmer-style design"""
        # Create ASCII-style header
        header_text = Text()
        header_text.append("╔══════════════════════════════════════════════════════════════════╗\n", style="bold bright_cyan")
        header_text.append("║", style="bold bright_cyan")
        header_text.append("                    🎵 YT-AUDIO PLAYER v2.0                      ", style="bold bright_white")
        header_text.append("║\n", style="bold bright_cyan")
        header_text.append("║", style="bold bright_cyan")
        header_text.append("                 Stream YouTube Audio Like A Pro                 ", style="bright_magenta")
        header_text.append("║\n", style="bold bright_cyan")
        header_text.append("╚══════════════════════════════════════════════════════════════════╝", style="bold bright_cyan")
        
        centered_header = Align.center(header_text)
        self.console.print(centered_header)
        self.console.print()
    
    def show_player_interface(self, title: str = "", uploader: str = "", 
                             current_time: int = 0, total_time: int = 0, 
                             position: float = 0.0, volume: int = 100, state: str = "stopped"):
        """Show the main player interface with beautiful design"""
        
        # Create main player panel
        player_table = Table.grid(padding=(0, 2))
        player_table.add_column(style="bright_white", width=90)
        player_table.add_column(style="bright_cyan", justify="right", width=20)
        
        # Song info section
        if title:
            # Title with music note
            title_text = Text()
            title_text.append("♪ ", style="bright_yellow bold")
            title_text.append(title[:55] + "..." if len(title) > 55 else title, style="bold bright_white")
            
            # Volume section with actual volume bar
            volume_bar = "█" * (volume // 10) + "░" * (10 - volume // 10)
            volume_text = Text()
            volume_text.append("🔊 ", style="bright_green")
            volume_text.append(f"[{volume_bar}] {volume}%", style="bright_cyan")
            
            
            player_table.add_row(title_text, Align.right(volume_text))
            
            # Artist info
            if uploader and uploader != "Unknown":
                artist_text = Text()
                artist_text.append("👤 ", style="bright_blue")
                artist_text.append(f"by {uploader}", style="dim bright_white")
                player_table.add_row(artist_text, "")
            
            # Status indicator
            status_text = Text()
            if state == "playing":
                status_text.append("▶️ ", style="bright_green bold")
                status_text.append("NOW PLAYING", style="bold bright_green")
            elif state == "paused":
                status_text.append("⏸️ ", style="bright_yellow bold")
                status_text.append("PAUSED", style="bold bright_yellow")
            elif state == "loading":
                status_text.append("⏳ ", style="bright_blue bold")
                status_text.append("LOADING...", style="bold bright_blue")
            else:
                status_text.append("⏹️ ", style="dim")
                status_text.append("READY", style="dim bright_white")
            
            player_table.add_row("", "")  # Spacing
            player_table.add_row(status_text, "")
        
        # Create the main panel
        main_panel = Panel(
            player_table,
            title="[bold bright_cyan]♫ AUDIO STREAM ♫[/bold bright_cyan]",
            border_style="bright_cyan",
            box=ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print(main_panel)
    
    def show_progress_bar(self, current_time: int, total_time: int, position: float = 0.0):
        """Show beautiful progress bar"""
        if total_time <= 0:
            # Show placeholder when no audio
            placeholder_panel = Panel(
                Align.center(Text("⌛ Waiting for audio stream...", style="dim bright_yellow")),
                title="[dim bright_white]PROGRESS[/dim bright_white]",
                border_style="dim bright_white",
                box=ROUNDED,
                padding=(0, 2)
            )
            self.console.print(placeholder_panel)
            return
        
        # Create progress visualization
        current_str = self.format_time(current_time)
        total_str = self.format_time(total_time)
        percentage = int(position * 100)
        
        # Create custom progress bar
        progress_width = 50
        filled = int(progress_width * position)
        empty = progress_width - filled
        
        progress_text = Text()
        progress_text.append(current_str, style="bright_green bold")
        progress_text.append(" [", style="bright_white")
        progress_text.append("█" * filled, style="bright_cyan")
        progress_text.append("░" * empty, style="dim")
        progress_text.append(f"] {percentage}% ", style="bright_white")
        progress_text.append(total_str, style="bright_green bold")
        
        # Add wave animation for playing state
        wave_text = Text("🎵 ~ ~ ~ ~ ~ 🎶 ~ ~ ~ ~ ~ 🎵", style="dim bright_magenta")
        
        progress_content = Align.center(progress_text)
        wave_content = Align.center(wave_text)
        
        # Combine progress and wave
        combined = Text()
        combined.append(str(progress_content) + "\n")
        combined.append(str(wave_content))
        
        progress_panel = Panel(
            progress_content,
            title=f"[bold bright_magenta]⏱️  PROGRESS - {percentage}%[/bold bright_magenta]",
            border_style="bright_magenta",
            box=ROUNDED,
            padding=(0, 2)
        )
        
        self.console.print(progress_panel)
        
        # Add wave animation below
        wave_panel = Panel(
            wave_content,
            border_style="dim bright_magenta",
            box=MINIMAL,
            padding=(0, 1)
        )
        self.console.print(wave_panel)
    
    def show_controls_info(self):
        """Show control information in a beautiful way"""
        controls_table = Table.grid(padding=(0, 4))
        controls_table.add_column(style="bright_yellow")
        controls_table.add_column(style="bright_white")
        controls_table.add_column(style="bright_yellow")
        controls_table.add_column(style="bright_white")
        
        controls_table.add_row("💻", "TERMINAL CONTROLS", "🎮", "PROGRAMMER MODE")
        controls_table.add_row("'p'", "Play/Pause", "'n'", "Next Track")
        controls_table.add_row("'q'", "Quit Player", "Ctrl+C", "Force Exit")
        
        controls_panel = Panel(
            controls_table,
            title="[bold bright_yellow]⌨️  KEYBOARD SHORTCUTS[/bold bright_yellow]",
            border_style="bright_yellow",
            box=ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print(controls_panel)
    
    def show_now_playing(self, title: str, uploader: str = "Unknown"):
        """Show now playing information"""
        self.current_title = title
        self.current_uploader = uploader
        
        # Clear and show the complete interface
        self.clear()
        self.show_welcome()
        self.show_player_interface(title, uploader, volume=getattr(self, 'current_volume', 70))
        self.show_progress_bar(0, 0, 0.0)
        self.show_controls_info()
    
    def update_progress(self, current_time: int, total_time: int, position: float = 0.0, volume: int = 70, state: str = "playing"):
        """Update the complete interface with progress"""
        self.clear()
        self.show_welcome()
        self.show_player_interface(self.current_title, self.current_uploader, current_time, total_time, position, volume, state)
        self.show_progress_bar(current_time, total_time, position)
        self.show_controls_info()
    
    def show_loading_animation(self, message: str = "Loading audio stream..."):
        """Show animated loading screen"""
        loading_text = Text()
        loading_text.append("⠋ ", style="bright_cyan bold")
        loading_text.append(message, style="bright_white")
        
        loading_panel = Panel(
            Align.center(loading_text),
            title="[bold bright_blue]🚀 INITIALIZING[/bold bright_blue]",
            border_style="bright_blue",
            box=ROUNDED,
            padding=(1, 4)
        )
        
        self.console.print(loading_panel)
    
    def get_url_input(self) -> str:
        """Get YouTube URL from user with style"""
        self.console.print()
        url_panel = Panel(
            "Enter YouTube URL to stream audio:",
            title="[bold bright_green]🔗 INPUT REQUIRED[/bold bright_green]",
            border_style="bright_green",
            box=ROUNDED
        )
        self.console.print(url_panel)
        
        return self.console.input("[bold bright_green]➤ URL:[/bold bright_green] ")
    
    def show_loading(self, message: str = "Loading..."):
        """Show loading message"""
        self.console.print(f"[bright_blue]⚡ {message}[/bright_blue]")
    
    def show_error(self, message: str):
        """Show error message with style"""
        error_panel = Panel(
            f"[bold red]💥 ERROR:[/bold red] {message}",
            title="[bold red]⚠️  SYSTEM ERROR[/bold red]",
            border_style="red",
            box=HEAVY,
            padding=(1, 2)
        )
        self.console.print(error_panel)
    
    def show_success(self, message: str):
        """Show success message"""
        success_panel = Panel(
            f"[bold green]✨ {message}[/bold green]",
            title="[bold green]🎉 SUCCESS[/bold green]",
            border_style="bright_green",
            box=ROUNDED
        )
        self.console.print(success_panel)
    
    def show_state(self, state: str):
        """Show current player state"""
        state_emojis = {
            'playing': '▶️',
            'paused': '⏸️',
            'stopped': '⏹️',
            'buffering': '⏳',
            'loading': '🔄',
            'error': '❌'
        }
        
        state_colors = {
            'playing': 'bright_green',
            'paused': 'bright_yellow',
            'stopped': 'bright_red',
            'buffering': 'bright_blue',
            'loading': 'bright_blue',
            'error': 'red'
        }
        
        emoji = state_emojis.get(state, '●')
        color = state_colors.get(state, 'white')
        
        state_text = f"[{color}]{emoji} {state.upper()}[/{color}]"
        self.console.print(f"\n{state_text}")
    
    def format_time(self, ms: int) -> str:
        """Format time from milliseconds to MM:SS"""
        if ms < 0:
            return "00:00"
        
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def print_separator(self):
        """Print a beautiful separator line"""
        separator = "═" * 80
        self.console.print(f"[dim bright_cyan]{separator}[/dim bright_cyan]")
    
    def ask_continue(self) -> bool:
        """Ask user if they want to continue with style"""
        continue_panel = Panel(
            "Ready for another audio stream?",
            title="[bold bright_magenta]🔄 CONTINUE?[/bold bright_magenta]",
            border_style="bright_magenta",
            box=ROUNDED
        )
        self.console.print(continue_panel)
        
        response = self.console.input("[bold bright_magenta]➤ Play another? (y/n):[/bold bright_magenta] ")
        return response.lower().startswith('y')
    
    def show_goodbye(self):
        """Show goodbye message"""
        goodbye_text = Text()
        goodbye_text.append("╔══════════════════════════════════════════════════════════════════╗\n", style="bold bright_cyan")
        goodbye_text.append("║", style="bold bright_cyan")
        goodbye_text.append("              Thanks for using YT-Audio Player! 🎵              ", style="bold bright_white")
        goodbye_text.append("║\n", style="bold bright_cyan")
        goodbye_text.append("║", style="bold bright_cyan")
        goodbye_text.append("                    Keep coding and jamming! 💻                  ", style="bright_magenta")
        goodbye_text.append("║\n", style="bold bright_cyan")
        goodbye_text.append("╚══════════════════════════════════════════════════════════════════╝", style="bold bright_cyan")
        
        self.console.print(goodbye_text)
