"""
StudyDev Interactive UI Utilities
Enhanced interactive features and beautiful terminal formatting
"""

import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.columns import Columns
from rich.rule import Rule

console = Console()

class InteractiveUI:
    """Enhanced interactive UI components for StudyDev"""
    
    def __init__(self):
        self.motivational_messages = {
            "start": [
                "🚀 Let's crush this session!",
                "💪 You've got this! Time to focus!",
                "🎯 Ready to level up your skills?",
                "🔥 Time to make magic happen!",
                "⚡ Let's turn knowledge into power!",
                "🌟 Your future self will thank you!",
                "🎓 Every expert was once a beginner!",
                "💡 Great things never came from comfort zones!"
            ],
            "break": [
                "☕ Well deserved break! You earned it!",
                "🌸 Take a deep breath and relax",
                "🚶 Maybe stretch a bit? Your body will thank you!",
                "💧 Don't forget to hydrate!",
                "🎵 Listen to your favorite song?",
                "🌅 Look outside - nature is beautiful!",
                "😌 Clear your mind, you're doing great!",
                "⭐ You're making excellent progress!"
            ],
            "completion": [
                "🎉 Fantastic work! Session completed!",
                "🏆 You're building great habits!",
                "💪 Another step towards mastery!",
                "🌟 Consistency is your superpower!",
                "🎯 You're on fire! Keep it up!",
                "🚀 Progress unlocked! Well done!",
                "🎓 Knowledge gained, wisdom earned!",
                "💎 You're forging your brilliant future!"
            ]
        }
    
    def show_welcome_animation(self):
        """Display an animated welcome message"""
        
        # ASCII art for StudyDev
        logo_lines = [
            "  ____  _             _       ____             ",
            " / ___|| |_ _   _  __| |_   _|  _ \\  _____   __",
            " \\___ \\| __| | | |/ _` | | | | | | |/ _ \\ \\ / /",
            "  ___) | |_| |_| | (_| | |_| | |_| |  __/\\ V / ",
            " |____/ \\__|\\__,_|\\__,_|\\__, |____/ \\___| \\_/  ",
            "                       |___/                  "
        ]
        
        # Animated reveal
        with Live(console=console, refresh_per_second=10) as live:
            for i in range(len(logo_lines) + 1):
                content = Text()
                
                # Add lines progressively
                for j, line in enumerate(logo_lines[:i]):
                    if j < i - 1:
                        content.append(line + "\n", style="bold blue")
                    elif j == i - 1:
                        # Typewriter effect for current line
                        partial_line = line[:min(len(line), (int(time.time() * 20) % (len(line) + 10)))]
                        content.append(partial_line + "\n", style="bold cyan")
                
                if i == len(logo_lines):
                    content.append("\n" + "🎯 Ultimate Student & Developer Productivity Tool", style="bold magenta")
                    content.append("\n" + "Made with ❤️  by PrinceTheProgrammer", style="dim")
                
                panel = Panel(
                    Align.center(content),
                    title="Welcome to StudyDev!",
                    border_style="green",
                    box=box.DOUBLE
                )
                
                live.update(panel)
                time.sleep(0.3)
        
        # Final pause
        time.sleep(1)
    
    def create_productivity_gauge(self, score: float, max_score: float = 5.0) -> Panel:
        """Create a beautiful productivity gauge"""
        
        # Calculate percentage
        percentage = (score / max_score) * 100
        
        # Create gauge visual
        gauge_width = 30
        filled_width = int((percentage / 100) * gauge_width)
        
        # Color based on score
        if percentage >= 80:
            color = "green"
            emoji = "🚀"
            level = "EXCEPTIONAL"
        elif percentage >= 60:
            color = "yellow"
            emoji = "🔥"
            level = "EXCELLENT"
        elif percentage >= 40:
            color = "orange"
            emoji = "💪"
            level = "GOOD"
        elif percentage >= 20:
            color = "red"
            emoji = "📈"
            level = "IMPROVING"
        else:
            color = "dim"
            emoji = "🌱"
            level = "STARTING"
        
        # Build gauge
        gauge_bar = "█" * filled_width + "░" * (gauge_width - filled_width)
        
        gauge_text = Text()
        gauge_text.append(f"{emoji} PRODUCTIVITY LEVEL: {level}\n\n", style=f"bold {color}")
        gauge_text.append(f"[{color}]{gauge_bar}[/{color}] {percentage:.1f}%\n", style="bold")
        gauge_text.append(f"Score: {score:.1f}/{max_score}", style=f"{color}")
        
        return Panel(
            Align.center(gauge_text),
            title="🎯 Productivity Meter",
            border_style=color,
            box=box.ROUNDED
        )
    
    def show_streak_celebration(self, streak_days: int):
        """Celebrate study streaks with animation"""
        
        if streak_days <= 1:
            return
        
        # Streak messages based on length
        if streak_days >= 30:
            emoji = "👑"
            message = f"LEGENDARY {streak_days}-day streak!"
            color = "gold1"
            effect = "CHAMPION"
        elif streak_days >= 14:
            emoji = "🔥"
            message = f"BLAZING {streak_days}-day streak!"
            color = "red"
            effect = "FIRE"
        elif streak_days >= 7:
            emoji = "⭐"
            message = f"AMAZING {streak_days}-day streak!"
            color = "yellow"
            effect = "STAR"
        else:
            emoji = "💪"
            message = f"SOLID {streak_days}-day streak!"
            color = "green"
            effect = "POWER"
        
        # Animated celebration
        with Live(console=console, refresh_per_second=8) as live:
            for frame in range(20):
                content = Text()
                
                # Pulsing effect
                if frame % 4 < 2:
                    content.append(f"\n{emoji} {effect} STREAK! {emoji}\n", style=f"bold {color} blink")
                else:
                    content.append(f"\n{emoji} {effect} STREAK! {emoji}\n", style=f"bold {color}")
                
                content.append(f"{message}\n", style=f"bold {color}")
                content.append("Keep the momentum going! 🚀", style="cyan")
                
                panel = Panel(
                    Align.center(content),
                    title="🎉 STREAK ACHIEVEMENT",
                    border_style=color,
                    box=box.DOUBLE
                )
                
                live.update(panel)
                time.sleep(0.1)
    
    def create_progress_visualization(self, data: Dict[str, Any]) -> Layout:
        """Create a comprehensive progress visualization"""
        
        layout = Layout()
        
        # Split into sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Header with title
        header_text = Text("📊 StudyDev Progress Dashboard", style="bold blue", justify="center")
        layout["header"].update(Panel(header_text, box=box.ROUNDED))
        
        # Main area split into left and right
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Left side: Stats
        stats_table = Table(title="📈 Current Stats", box=box.SIMPLE)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="bold green")
        
        stats_table.add_row("🎯 Sessions Today", str(data.get("sessions_today", 0)))
        stats_table.add_row("⏰ Hours Studied", f"{data.get('hours_studied', 0):.1f}h")
        stats_table.add_row("🔥 Current Streak", f"{data.get('streak', 0)} days")
        stats_table.add_row("🎴 Cards Due", str(data.get("flashcards_due", 0)))
        
        layout["left"].update(stats_table)
        
        # Right side: Recent activity
        activity_table = Table(title="🕐 Recent Activity", box=box.SIMPLE)
        activity_table.add_column("Activity", style="blue")
        activity_table.add_column("Time", style="dim")
        
        for activity in data.get("recent_activity", [])[:5]:
            activity_table.add_row(activity["action"], activity["time"])
        
        layout["right"].update(activity_table)
        
        # Footer with motivational message
        motivation = random.choice(self.motivational_messages["start"])
        footer_text = Text(motivation, style="italic green", justify="center")
        layout["footer"].update(Panel(footer_text, box=box.ROUNDED))
        
        return layout
    
    def show_completion_celebration(self, session_type: str, duration_minutes: int, 
                                  productivity_rating: int = None):
        """Show an animated completion celebration"""
        
        # Select appropriate messages and colors
        if session_type == "study":
            emoji = "🎓"
            color = "green"
            title = "STUDY SESSION COMPLETE!"
        elif session_type == "break":
            emoji = "☕"
            color = "blue"  
            title = "BREAK TIME FINISHED!"
        else:
            emoji = "🚀"
            color = "magenta"
            title = "SESSION COMPLETE!"
        
        messages = self.motivational_messages["completion"]
        celebration_msg = random.choice(messages)
        
        # Animated celebration
        with Live(console=console, refresh_per_second=6) as live:
            for frame in range(15):
                content = Text()
                
                # Pulsing title
                if frame % 3 == 0:
                    content.append(f"\n{emoji} {title} {emoji}\n", style=f"bold {color} blink")
                else:
                    content.append(f"\n{emoji} {title} {emoji}\n", style=f"bold {color}")
                
                content.append(f"Duration: {duration_minutes} minutes\n", style="cyan")
                
                if productivity_rating:
                    stars = "⭐" * productivity_rating
                    content.append(f"Rating: {stars} ({productivity_rating}/5)\n", style="yellow")
                
                content.append(f"\n{celebration_msg}", style="italic green")
                
                panel = Panel(
                    Align.center(content),
                    title="🎉 CONGRATULATIONS",
                    border_style=color,
                    box=box.DOUBLE
                )
                
                live.update(panel)
                time.sleep(0.15)
    
    def create_interactive_menu(self, title: str, options: List[Dict[str, str]], 
                              style: str = "blue") -> str:
        """Create an interactive menu with navigation"""
        
        console.print(f"\n{title}", style=f"bold {style}")
        console.print(Rule(style=style))
        
        # Display options
        for i, option in enumerate(options, 1):
            icon = option.get("icon", "•")
            desc = option.get("description", "")
            console.print(f"  {i}. {icon} {option['label']}")
            if desc:
                console.print(f"     [dim]{desc}[/dim]")
        
        console.print(Rule(style=style))
        
        while True:
            try:
                choice = Prompt.ask(
                    "Select option",
                    choices=[str(i) for i in range(1, len(options) + 1)],
                    default="1"
                )
                return options[int(choice) - 1]["value"]
            except (ValueError, IndexError):
                console.print("❌ [red]Invalid choice, please try again[/red]")
    
    def show_loading_animation(self, message: str, duration: float = 2.0):
        """Show a beautiful loading animation"""
        
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        with Live(console=console, refresh_per_second=10) as live:
            start_time = time.time()
            
            while time.time() - start_time < duration:
                spinner_idx = int((time.time() - start_time) * 10) % len(spinners)
                spinner = spinners[spinner_idx]
                
                content = Text()
                content.append(f"{spinner} ", style="cyan bold")
                content.append(message, style="blue")
                
                panel = Panel(
                    Align.center(content),
                    title="Processing...",
                    border_style="cyan"
                )
                
                live.update(panel)
                time.sleep(0.1)
    
    def create_help_display(self, commands: Dict[str, Dict[str, str]]) -> None:
        """Create a beautiful help display with command categories"""
        
        console.print("\n🎯 [bold blue]StudyDev Command Reference[/bold blue]")
        console.print(Rule(style="blue"))
        
        for category, cmd_list in commands.items():
            # Category header
            console.print(f"\n📁 [bold green]{category}[/bold green]")
            
            # Commands table
            table = Table(box=box.SIMPLE, show_header=False)
            table.add_column("Command", style="cyan", min_width=25)
            table.add_column("Description", style="white")
            
            for command, description in cmd_list.items():
                table.add_row(f"studydev {command}", description)
            
            console.print(table)
        
        console.print(Rule(style="blue"))
        console.print("💡 [italic]Tip: Use --help after any command for detailed options[/italic]")
    
    def show_achievement_unlock(self, achievement: Dict[str, Any]):
        """Show an achievement unlock animation"""
        
        title = achievement.get("title", "Achievement Unlocked!")
        description = achievement.get("description", "Great job!")
        icon = achievement.get("icon", "🏆")
        color = achievement.get("color", "gold1")
        
        # Achievement unlock animation
        with Live(console=console, refresh_per_second=8) as live:
            for frame in range(25):
                content = Text()
                
                # Glowing effect
                if frame < 10:
                    intensity = frame / 10
                    glow_char = "✨" if frame % 2 == 0 else "⭐"
                elif frame < 20:
                    intensity = 1.0
                    glow_char = "🌟"
                else:
                    intensity = (25 - frame) / 5
                    glow_char = "✨"
                
                # Build content
                glow_line = glow_char * int(intensity * 8)
                content.append(f"{glow_line}\n", style=color)
                content.append(f"{icon} ACHIEVEMENT UNLOCKED! {icon}\n", style=f"bold {color}")
                content.append(f"{title}\n", style=f"bold white")
                content.append(f"{glow_line}\n", style=color)
                content.append(f"{description}", style="italic cyan")
                
                panel = Panel(
                    Align.center(content),
                    title="🎉 SUCCESS",
                    border_style=color,
                    box=box.DOUBLE
                )
                
                live.update(panel)
                time.sleep(0.1)
        
        # Hold final frame
        time.sleep(1)
    
    def create_status_summary(self, data: Dict[str, Any]) -> Panel:
        """Create a comprehensive status summary panel"""
        
        # Main stats
        stats_columns = []
        
        # Study stats
        study_text = Text()
        study_text.append("📚 STUDY\n", style="bold blue")
        study_text.append(f"Sessions: {data.get('total_sessions', 0)}\n", style="blue")
        study_text.append(f"Hours: {data.get('total_hours', 0):.1f}h\n", style="blue")
        study_text.append(f"Streak: {data.get('streak', 0)} days", style="blue")
        
        # Project stats
        project_text = Text()
        project_text.append("📝 PROJECTS\n", style="bold green")
        project_text.append(f"Active: {data.get('active_projects', 0)}\n", style="green")
        project_text.append(f"Completed: {data.get('completed_projects', 0)}\n", style="green")
        project_text.append(f"Due Soon: {data.get('due_soon', 0)}", style="green")
        
        # Study materials
        materials_text = Text()
        materials_text.append("🎴 MATERIALS\n", style="bold magenta")
        materials_text.append(f"Flashcards: {data.get('total_flashcards', 0)}\n", style="magenta")
        materials_text.append(f"Due: {data.get('flashcards_due', 0)}\n", style="magenta")
        materials_text.append(f"Bookmarks: {data.get('total_bookmarks', 0)}", style="magenta")
        
        # Productivity score
        score = data.get('productivity_score', 0)
        productivity_text = Text()
        productivity_text.append("🎯 PRODUCTIVITY\n", style="bold yellow")
        productivity_text.append(f"Score: {score:.1f}/5\n", style="yellow")
        productivity_text.append(f"Level: {data.get('productivity_level', 'Starting')}", style="yellow")
        
        stats_columns = [
            Panel(study_text, title="Study", box=box.ROUNDED),
            Panel(project_text, title="Projects", box=box.ROUNDED),
            Panel(materials_text, title="Materials", box=box.ROUNDED),
            Panel(productivity_text, title="Performance", box=box.ROUNDED)
        ]
        
        return Panel(
            Columns(stats_columns, equal=True),
            title="🎯 StudyDev Status Overview",
            border_style="blue",
            box=box.DOUBLE
        )