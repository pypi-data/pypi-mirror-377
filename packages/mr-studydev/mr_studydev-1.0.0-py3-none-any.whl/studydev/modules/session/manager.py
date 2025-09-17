"""
StudyDev Session Manager - Core Logic
Handles Pomodoro timer, session tracking, and productivity analytics
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, BarColumn
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table

from studydev.core.config import Config
from studydev.core.database import Database
from studydev.utils.interactive import InteractiveUI

console = Console()

class SessionManager:
    """Manages study sessions with Pomodoro timer functionality"""
    
    def __init__(self):
        self.config = Config()
        self.db = Database()
        self.interactive_ui = InteractiveUI()
        self.current_session = None
        self.timer_thread = None
        self.is_running = False
        self.is_paused = False
        self.remaining_time = 0
        
    def start_session(self, session_type: str = "study", duration: int = 25, 
                     subject: str = None, project: str = None) -> Dict[str, Any]:
        """Start a new session with timer"""
        
        if self.is_running:
            console.print("❌ [red]A session is already running! Stop it first.[/red]")
            return {"success": False, "message": "Session already running"}
        
        # Get project ID if project name provided
        project_id = None
        if project:
            project_id = self._get_project_id(project)
            if not project_id:
                console.print(f"⚠️  [yellow]Project '{project}' not found. Session will be created without project link.[/yellow]")
        
        # Create session record
        session_data = {
            "session_type": session_type,
            "project_id": project_id,
            "subject": subject,
            "start_time": datetime.now().isoformat(),
            "duration": duration * 60,  # Convert to seconds
            "status": "active"
        }
        
        # Insert into database
        session_id = self._create_session_record(session_data)
        session_data["id"] = session_id
        
        self.current_session = session_data
        self.remaining_time = duration * 60
        self.is_running = True
        self.is_paused = False
        
        # Start the timer
        self._start_timer_display(duration, session_type, subject)
        
        return {"success": True, "session_id": session_id, "message": "Session started successfully"}
    
    def _start_timer_display(self, duration_minutes: int, session_type: str, subject: str):
        """Display interactive timer with progress"""
        
        total_seconds = duration_minutes * 60
        start_time = time.time()
        
        # Create a beautiful timer display
        def create_timer_display(elapsed: int, remaining: int):
            # Calculate progress
            progress_percent = (elapsed / total_seconds) * 100
            
            # Create main panel content
            timer_text = Text()
            timer_text.append("🍅 " if session_type == "study" else "☕ ", style="bold")
            timer_text.append(f"{session_type.title()} Session", style="bold blue")
            
            if subject:
                timer_text.append(f"\n📚 {subject}", style="dim")
            
            # Format time remaining
            minutes, seconds = divmod(remaining, 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            timer_text.append(f"\n\n⏰ {time_str}", style="bold green" if remaining > 60 else "bold red")
            
            # Add progress bar
            bar_width = 30
            filled = int((progress_percent / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            timer_text.append(f"\n{bar} {progress_percent:.1f}%", style="blue")
            
            # Add motivational messages based on time remaining
            if remaining > total_seconds * 0.75:
                timer_text.append("\n💪 Stay focused! You've got this!", style="bold cyan")
            elif remaining > total_seconds * 0.5:
                timer_text.append("\n🔥 Great progress! Keep going!", style="bold yellow")
            elif remaining > total_seconds * 0.25:
                timer_text.append("\n🎯 Almost there! Push through!", style="bold orange")
            else:
                timer_text.append("\n🏁 Final stretch! You're amazing!", style="bold red")
            
            return Panel(
                timer_text,
                title=f"StudyDev Timer - {session_type.title()}",
                border_style="green" if remaining > 60 else "red",
                expand=False
            )
        
        # Timer loop with live display
        try:
            with Live(create_timer_display(0, total_seconds), refresh_per_second=1, console=console) as live:
                while self.remaining_time > 0 and self.is_running:
                    if not self.is_paused:
                        elapsed = int(time.time() - start_time)
                        self.remaining_time = max(0, total_seconds - elapsed)
                        live.update(create_timer_display(elapsed, self.remaining_time))
                    
                    time.sleep(1)
                
                # Timer completed
                if self.remaining_time <= 0:
                    self._session_completed(duration_minutes, session_type)
                    
        except KeyboardInterrupt:
            self.pause_session()
            console.print("\n⏸️  [yellow]Session paused. Use 'studydev session resume' to continue or 'studydev session stop' to end.[/yellow]")
    
    def _session_completed(self, duration_minutes: int, session_type: str):
        """Handle session completion with beautiful celebration"""
        if not self.current_session:
            return
        
        # Update session record
        end_time = datetime.now().isoformat()
        actual_duration = (datetime.fromisoformat(end_time) - 
                         datetime.fromisoformat(self.current_session["start_time"])).total_seconds()
        
        # Get productivity rating with interactive prompt
        from rich.prompt import IntPrompt
        rating = IntPrompt.ask(
            "\n🎆 [bold]How productive was this session?[/bold] (1-5)",
            choices=["1", "2", "3", "4", "5"],
            default=4
        )
        
        self.db.execute_update(
            "UPDATE sessions SET end_time = ?, duration = ?, productivity_rating = ? WHERE id = ?",
            (end_time, int(actual_duration), rating, self.current_session["id"])
        )
        
        # Show beautiful completion celebration
        self.interactive_ui.show_completion_celebration(
            session_type, 
            int(actual_duration // 60),
            rating
        )
        
        # Play completion sound (if enabled)
        self._play_completion_sound()
        
        # Check for achievements and streaks
        self._check_achievements()
        
        # Reset state
        self.is_running = False
        self.current_session = None
    
    def pause_session(self):
        """Pause the current session"""
        if not self.is_running:
            console.print("❌ [red]No active session to pause.[/red]")
            return False
        
        self.is_paused = True
        console.print("⏸️  [yellow]Session paused.[/yellow]")
        return True
    
    def resume_session(self):
        """Resume a paused session"""
        if not self.is_running or not self.is_paused:
            console.print("❌ [red]No paused session to resume.[/red]")
            return False
        
        self.is_paused = False
        console.print("▶️  [green]Session resumed.[/green]")
        return True
    
    def stop_session(self, rating: int = None):
        """Stop the current session"""
        if not self.is_running:
            console.print("❌ [red]No active session to stop.[/red]")
            return False
        
        # Update session record
        if self.current_session:
            end_time = datetime.now().isoformat()
            actual_duration = (datetime.fromisoformat(end_time) - 
                             datetime.fromisoformat(self.current_session["start_time"])).total_seconds()
            
            self.db.execute_update(
                "UPDATE sessions SET end_time = ?, duration = ?, productivity_rating = ? WHERE id = ?",
                (end_time, int(actual_duration), rating or 3, self.current_session["id"])
            )
        
        # Reset state
        self.is_running = False
        self.is_paused = False
        self.current_session = None
        
        console.print("🛑 [yellow]Session stopped.[/yellow]")
        return True
    
    def get_session_stats(self, period: str = "today") -> Dict[str, Any]:
        """Get session statistics for specified period"""
        
        # Calculate date range
        now = datetime.now()
        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:  # all
            start_date = datetime(2000, 1, 1)
        
        # Query database
        sessions = self.db.execute_query("""
            SELECT session_type, subject, duration, productivity_rating, start_time
            FROM sessions 
            WHERE start_time >= ? AND end_time IS NOT NULL
            ORDER BY start_time DESC
        """, (start_date.isoformat(),))
        
        # Calculate statistics
        stats = {
            "total_sessions": len(sessions),
            "total_time_seconds": sum(s[2] or 0 for s in sessions),
            "total_time_hours": round(sum(s[2] or 0 for s in sessions) / 3600, 2),
            "average_rating": round(sum(s[3] or 0 for s in sessions) / len(sessions), 2) if sessions else 0,
            "subjects": {},
            "session_types": {},
            "daily_breakdown": {}
        }
        
        # Break down by subject and type
        for session in sessions:
            session_type, subject, duration, rating, start_time = session
            duration = duration or 0
            
            # Subject breakdown
            if subject:
                if subject not in stats["subjects"]:
                    stats["subjects"][subject] = {"sessions": 0, "time": 0, "rating": []}
                stats["subjects"][subject]["sessions"] += 1
                stats["subjects"][subject]["time"] += duration
                if rating:
                    stats["subjects"][subject]["rating"].append(rating)
            
            # Session type breakdown
            if session_type not in stats["session_types"]:
                stats["session_types"][session_type] = {"sessions": 0, "time": 0}
            stats["session_types"][session_type]["sessions"] += 1
            stats["session_types"][session_type]["time"] += duration
            
            # Daily breakdown
            day = datetime.fromisoformat(start_time).date().isoformat()
            if day not in stats["daily_breakdown"]:
                stats["daily_breakdown"][day] = {"sessions": 0, "time": 0}
            stats["daily_breakdown"][day]["sessions"] += 1
            stats["daily_breakdown"][day]["time"] += duration
        
        # Calculate average ratings for subjects
        for subject_data in stats["subjects"].values():
            if subject_data["rating"]:
                subject_data["avg_rating"] = round(sum(subject_data["rating"]) / len(subject_data["rating"]), 2)
            else:
                subject_data["avg_rating"] = 0
            del subject_data["rating"]  # Remove raw ratings list
        
        return stats
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent session history"""
        
        sessions = self.db.execute_query("""
            SELECT s.id, s.session_type, s.subject, s.start_time, s.end_time, 
                   s.duration, s.productivity_rating, p.name as project_name
            FROM sessions s
            LEFT JOIN projects p ON s.project_id = p.id
            ORDER BY s.start_time DESC
            LIMIT ?
        """, (limit,))
        
        history = []
        for session in sessions:
            session_id, session_type, subject, start_time, end_time, duration, rating, project = session
            
            # Format session data
            session_data = {
                "id": session_id,
                "type": session_type,
                "subject": subject,
                "project": project,
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": round((duration or 0) / 60) if duration else 0,
                "rating": rating,
                "status": "completed" if end_time else "incomplete"
            }
            
            history.append(session_data)
        
        return history
    
    def _get_project_id(self, project_name: str) -> Optional[int]:
        """Get project ID by name"""
        result = self.db.execute_query(
            "SELECT id FROM projects WHERE name = ?", (project_name,)
        )
        return result[0][0] if result else None
    
    def _create_session_record(self, session_data: Dict[str, Any]) -> int:
        """Create a new session record in database"""
        
        result = self.db.execute_update("""
            INSERT INTO sessions (session_type, project_id, subject, start_time, duration)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_data["session_type"],
            session_data.get("project_id"),
            session_data.get("subject"),
            session_data["start_time"],
            session_data.get("duration")
        ))
        
        # Get the ID of the inserted record
        session_id = self.db.execute_query("SELECT last_insert_rowid()")[0][0]
        return session_id
    
    def _check_achievements(self):
        """Check and display achievement unlocks"""
        # Calculate current streak
        now = datetime.now()
        today = now.date()
        
        # Get recent sessions to calculate streak
        recent_sessions = self.db.execute_query("""
            SELECT DISTINCT DATE(start_time) as session_date 
            FROM sessions 
            WHERE end_time IS NOT NULL 
            ORDER BY session_date DESC
            LIMIT 30
        """)
        
        # Calculate consecutive days
        streak_days = 0
        check_date = today
        
        session_dates = [datetime.fromisoformat(s[0] + "T00:00:00").date() for s in recent_sessions]
        
        while check_date in session_dates:
            streak_days += 1
            check_date = check_date - timedelta(days=1)
        
        # Check for streak milestones
        if streak_days == 3:
            self.interactive_ui.show_achievement_unlock({
                "title": "Three Day Streak!",
                "description": "You've studied for 3 consecutive days. Great start!",
                "icon": "🔥",
                "color": "orange"
            })
        elif streak_days == 7:
            self.interactive_ui.show_achievement_unlock({
                "title": "One Week Warrior!", 
                "description": "Seven days straight! You're building amazing habits!",
                "icon": "⭐",
                "color": "yellow"
            })
        elif streak_days == 30:
            self.interactive_ui.show_achievement_unlock({
                "title": "Monthly Master!",
                "description": "30 days of consistent study! You're unstoppable!",
                "icon": "👑",
                "color": "gold1"
            })
        
        # Check session milestones
        total_sessions = self.db.execute_query(
            "SELECT COUNT(*) FROM sessions WHERE end_time IS NOT NULL"
        )[0][0]
        
        if total_sessions == 10:
            self.interactive_ui.show_achievement_unlock({
                "title": "Session Starter!",
                "description": "You've completed 10 study sessions!",
                "icon": "📚",
                "color": "blue"
            })
        elif total_sessions == 50:
            self.interactive_ui.show_achievement_unlock({
                "title": "Study Champion!",
                "description": "50 sessions completed! You're a productivity machine!",
                "icon": "🏆",
                "color": "gold1"
            })
        elif total_sessions == 100:
            self.interactive_ui.show_achievement_unlock({
                "title": "Century Club!",
                "description": "100 study sessions! You've truly mastered consistency!",
                "icon": "💎",
                "color": "magenta"
            })
    
    def _play_completion_sound(self):
        """Play completion sound if enabled"""
        if self.config.get("session.notification_sound", True):
            # Simple beep sound for completion
            try:
                import os
                os.system("echo -e '\a'")  # Terminal bell
            except:
                pass  # Ignore if sound fails
