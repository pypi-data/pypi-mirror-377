"""
StudyDev Session Management Commands
Handles Pomodoro timer, task tracking, and time logging
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from studydev.modules.session.manager import SessionManager

console = Console()

# Create the session sub-application
session_app = typer.Typer(
    help="📚 Study & Dev Session Manager - Pomodoro timer and productivity tracking",
    rich_markup_mode="rich"
)

@session_app.command("start")
def start_session(
    session_type: str = typer.Option("study", help="Type of session (study/break/project)"),
    duration: int = typer.Option(25, help="Duration in minutes"),
    subject: str = typer.Option(None, help="Subject or topic for this session"),
    project: str = typer.Option(None, help="Associated project name")
):
    """🚀 Start a new study/work session with Pomodoro timer"""
    manager = SessionManager()
    
    console.print(f"\n🎯 Starting {session_type} session for {duration} minutes")
    if subject:
        console.print(f"📚 Subject: {subject}")
    if project:
        console.print(f"📝 Project: {project}")
    
    console.print("\n⏰ [cyan]Press Ctrl+C to pause the timer[/cyan]")
    console.print("[dim]Timer will start in 3 seconds...[/dim]")
    
    import time
    time.sleep(3)
    
    # Start the actual session
    result = manager.start_session(
        session_type=session_type,
        duration=duration,
        subject=subject,
        project=project
    )
    
    if not result["success"]:
        console.print(f"❌ [red]Failed to start session: {result['message']}[/red]")

@session_app.command("break")
def take_break(
    duration: int = typer.Option(5, help="Break duration in minutes")
):
    """☕ Take a break with timer"""
    manager = SessionManager()
    
    console.print(f"\n☕ Starting {duration}-minute break")
    console.print("\n⏰ [cyan]Press Ctrl+C to pause the break timer[/cyan]")
    console.print("[dim]Break timer will start in 3 seconds...[/dim]")
    
    import time
    time.sleep(3)
    
    # Start break session
    result = manager.start_session(
        session_type="break",
        duration=duration,
        subject="Break Time"
    )
    
    if not result["success"]:
        console.print(f"❌ [red]Failed to start break: {result['message']}[/red]")

@session_app.command("pause")
def pause_session():
    """⏸️  Pause the current session"""
    manager = SessionManager()
    manager.pause_session()

@session_app.command("resume")
def resume_session():
    """▶️  Resume a paused session"""
    manager = SessionManager()
    manager.resume_session()

@session_app.command("stop")
def stop_session(
    rating: int = typer.Option(None, help="Rate your productivity (1-5)", min=1, max=5)
):
    """🛑 Stop the current session"""
    manager = SessionManager()
    
    if rating is None:
        # Ask for rating interactively
        try:
            rating_input = typer.prompt("Rate your productivity (1-5)", type=int)
            if 1 <= rating_input <= 5:
                rating = rating_input
            else:
                console.print("[yellow]Invalid rating, using default (3)[/yellow]")
                rating = 3
        except:
            console.print("[yellow]Using default rating (3)[/yellow]")
            rating = 3
    
    manager.stop_session(rating)

@session_app.command("stats")
def show_stats(
    period: str = typer.Option("today", help="Time period (today/week/month/all)")
):
    """📈 Show session statistics and productivity metrics"""
    manager = SessionManager()
    stats = manager.get_session_stats(period)
    
    # Create main stats panel
    stats_text = Text()
    stats_text.append(f"📈 Session Statistics - {period.title()}\n\n", style="bold blue")
    stats_text.append(f"🎯 Total Sessions: {stats['total_sessions']}\n", style="green")
    stats_text.append(f"⏱️  Total Time: {stats['total_time_hours']} hours\n", style="green")
    
    if stats['average_rating'] > 0:
        stars = "⭐" * int(stats['average_rating'])
        stats_text.append(f"🎆 Average Rating: {stats['average_rating']}/5 {stars}\n", style="yellow")
    
    stats_panel = Panel(stats_text, title="Overview", border_style="blue")
    console.print(stats_panel)
    
    # Subject breakdown table
    if stats['subjects']:
        console.print("\n📚 [bold]Subject Breakdown[/bold]")
        subject_table = Table()
        subject_table.add_column("Subject", style="cyan")
        subject_table.add_column("Sessions", justify="right")
        subject_table.add_column("Time (hours)", justify="right")
        subject_table.add_column("Avg Rating", justify="right")
        
        for subject, data in stats['subjects'].items():
            hours = round(data['time'] / 3600, 1)
            rating = f"{data['avg_rating']}/5" if data['avg_rating'] > 0 else "N/A"
            subject_table.add_row(
                subject, 
                str(data['sessions']), 
                str(hours), 
                rating
            )
        
        console.print(subject_table)
    
    # Session types breakdown
    if stats['session_types']:
        console.print("\n🔄 [bold]Session Types[/bold]")
        type_table = Table()
        type_table.add_column("Type", style="magenta")
        type_table.add_column("Sessions", justify="right")
        type_table.add_column("Time (hours)", justify="right")
        
        for session_type, data in stats['session_types'].items():
            hours = round(data['time'] / 3600, 1)
            type_table.add_row(
                session_type.title(), 
                str(data['sessions']), 
                str(hours)
            )
        
        console.print(type_table)

@session_app.command("history")
def show_history(
    limit: int = typer.Option(10, help="Number of recent sessions to show")
):
    """📚 Show recent session history"""
    manager = SessionManager()
    history = manager.get_session_history(limit)
    
    if not history:
        console.print("\n📚 [yellow]No session history found. Start your first session![/yellow]")
        return
    
    console.print(f"\n📚 [bold]Recent Session History (last {limit})[/bold]")
    
    # Create history table
    history_table = Table()
    history_table.add_column("Date/Time", style="cyan")
    history_table.add_column("Type", style="magenta")
    history_table.add_column("Subject", style="green")
    history_table.add_column("Project", style="blue")
    history_table.add_column("Duration", justify="right")
    history_table.add_column("Rating", justify="center")
    history_table.add_column("Status", justify="center")
    
    for session in history:
        # Format datetime
        from datetime import datetime
        dt = datetime.fromisoformat(session['start_time'])
        date_str = dt.strftime("%m-%d %H:%M")
        
        # Format rating
        rating = "⭐" * session['rating'] if session['rating'] else "N/A"
        
        # Status icon
        status_icon = "✅" if session['status'] == "completed" else "⏸️"
        
        history_table.add_row(
            date_str,
            session['type'].title(),
            session['subject'] or "N/A",
            session['project'] or "N/A",
            f"{session['duration_minutes']}m",
            rating,
            status_icon
        )
    
    console.print(history_table)
