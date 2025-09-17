"""
StudyDev Integration Utilities
Cross-module functionality for comprehensive reports and dashboards
"""

import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple
import math

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from studydev.core.config import Config
from studydev.core.database import Database

console = Console()

class IntegrationManager:
    """Manages cross-module functionality and report generation"""
    
    def __init__(self):
        self.config = Config()
        self.db = Database()
    
    def generate_productivity_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive productivity report across all modules"""
        
        start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        today = date.today().isoformat()
        
        report = {
            "period": {
                "start_date": start_date,
                "end_date": today,
                "days": days
            },
            "sessions": self._analyze_sessions(start_date),
            "projects": self._analyze_projects(start_date),
            "study": self._analyze_study_materials(start_date),
            "integration": {}
        }
        
        # Calculate cross-module metrics
        report["integration"] = self._calculate_integration_metrics(report)
        
        return report
    
    def _analyze_sessions(self, start_date: str) -> Dict[str, Any]:
        """Analyze session data for reporting"""
        
        # Get sessions in period
        sessions = self.db.execute_query("""
            SELECT session_type, subject, duration, productivity_rating, 
                   start_time, end_time, project_id, DATE(start_time) as session_date
            FROM sessions 
            WHERE start_time >= ? AND end_time IS NOT NULL
            ORDER BY start_time ASC
        """, (start_date,))
        
        # Calculate metrics
        total_sessions = len(sessions)
        
        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "total_time_hours": 0,
                "average_duration_minutes": 0,
                "average_rating": 0,
                "subject_breakdown": {},
                "project_breakdown": {},
                "daily_breakdown": {},
                "type_breakdown": {}
            }
        
        total_duration = sum(s[2] or 0 for s in sessions)
        total_duration_hours = round(total_duration / 3600, 2)
        
        avg_duration = round(total_duration / total_sessions / 60, 2)  # in minutes
        
        rated_sessions = [s for s in sessions if s[3] is not None]
        avg_rating = round(sum(s[3] for s in rated_sessions) / len(rated_sessions), 2) if rated_sessions else 0
        
        # Breakdown by subject
        subjects = {}
        for session in sessions:
            subject = session[1]
            if subject:
                if subject not in subjects:
                    subjects[subject] = {"sessions": 0, "duration": 0}
                subjects[subject]["sessions"] += 1
                subjects[subject]["duration"] += session[2] or 0
        
        for subject in subjects.values():
            subject["duration_hours"] = round(subject["duration"] / 3600, 2)
        
        # Breakdown by project
        project_ids = list(set(s[6] for s in sessions if s[6]))
        projects = {}
        
        if project_ids:
            # Get project names
            project_data = self.db.execute_query("""
                SELECT id, name FROM projects WHERE id IN ({})
            """.format(','.join('?' for _ in project_ids)), tuple(project_ids))
            
            project_names = {p[0]: p[1] for p in project_data}
            
            for session in sessions:
                project_id = session[6]
                if project_id:
                    project_name = project_names.get(project_id, f"Project {project_id}")
                    if project_name not in projects:
                        projects[project_name] = {"sessions": 0, "duration": 0}
                    projects[project_name]["sessions"] += 1
                    projects[project_name]["duration"] += session[2] or 0
            
            for project in projects.values():
                project["duration_hours"] = round(project["duration"] / 3600, 2)
        
        # Daily breakdown
        daily = {}
        for session in sessions:
            day = session[7]  # session_date
            if day not in daily:
                daily[day] = {"sessions": 0, "duration": 0}
            daily[day]["sessions"] += 1
            daily[day]["duration"] += session[2] or 0
        
        for day in daily.values():
            day["duration_hours"] = round(day["duration"] / 3600, 2)
        
        # Session type breakdown
        types = {}
        for session in sessions:
            session_type = session[0]
            if session_type not in types:
                types[session_type] = {"sessions": 0, "duration": 0}
            types[session_type]["sessions"] += 1
            types[session_type]["duration"] += session[2] or 0
        
        for type_data in types.values():
            type_data["duration_hours"] = round(type_data["duration"] / 3600, 2)
        
        return {
            "total_sessions": total_sessions,
            "total_time_hours": total_duration_hours,
            "average_duration_minutes": avg_duration,
            "average_rating": avg_rating,
            "subject_breakdown": subjects,
            "project_breakdown": projects,
            "daily_breakdown": daily,
            "type_breakdown": types
        }
    
    def _analyze_projects(self, start_date: str) -> Dict[str, Any]:
        """Analyze project data for reporting"""
        
        # Get projects modified in period
        projects = self.db.execute_query("""
            SELECT id, name, project_type, language, status, priority,
                   deadline, created_at, updated_at
            FROM projects 
            WHERE updated_at >= ? OR created_at >= ?
            ORDER BY updated_at DESC
        """, (start_date, start_date))
        
        # Project statistics
        total_projects = len(projects)
        
        if total_projects == 0:
            return {
                "total_projects": 0,
                "active_projects": 0,
                "completed_projects": 0,
                "projects_with_deadlines": 0,
                "overdue_projects": 0,
                "type_breakdown": {},
                "language_breakdown": {},
                "status_breakdown": {},
                "recent_projects": []
            }
        
        active_projects = sum(1 for p in projects if p[4] == "active")
        completed_projects = sum(1 for p in projects if p[4] == "completed")
        projects_with_deadlines = sum(1 for p in projects if p[6])
        
        today = date.today().isoformat()
        overdue_projects = sum(1 for p in projects if p[6] and p[6] < today and p[4] != "completed")
        
        # Type breakdown
        types = {}
        for project in projects:
            project_type = project[2]
            if project_type not in types:
                types[project_type] = 0
            types[project_type] += 1
        
        # Language breakdown
        languages = {}
        for project in projects:
            language = project[3]
            if language:
                if language not in languages:
                    languages[language] = 0
                languages[language] += 1
        
        # Status breakdown
        statuses = {}
        for project in projects:
            status = project[4]
            if status not in statuses:
                statuses[status] = 0
            statuses[status] += 1
        
        # Recent projects (last 5)
        recent = []
        for project in projects[:5]:
            recent.append({
                "id": project[0],
                "name": project[1],
                "type": project[2],
                "status": project[4],
                "updated_at": project[8]
            })
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "projects_with_deadlines": projects_with_deadlines,
            "overdue_projects": overdue_projects,
            "type_breakdown": types,
            "language_breakdown": languages,
            "status_breakdown": statuses,
            "recent_projects": recent
        }
    
    def _analyze_study_materials(self, start_date: str) -> Dict[str, Any]:
        """Analyze study materials data for reporting"""
        
        # Flashcard stats
        flashcards = self.db.execute_query("""
            SELECT id, subject, difficulty, review_count, correct_streak,
                   created_at, last_reviewed
            FROM flashcards
            WHERE created_at >= ? OR last_reviewed >= ?
        """, (start_date, start_date))
        
        total_flashcards = len(flashcards)
        
        if total_flashcards == 0:
            flashcard_stats = {
                "total_flashcards": 0,
                "total_reviews": 0,
                "average_streak": 0,
                "subject_breakdown": {},
                "mastery_rate": 0
            }
        else:
            total_reviews = sum(fc[3] or 0 for fc in flashcards)
            streaks = [fc[4] or 0 for fc in flashcards]
            avg_streak = round(sum(streaks) / len(streaks), 2)
            
            # Mastery rate (percentage of cards with streak >= 3)
            mastery_count = sum(1 for s in streaks if s >= 3)
            mastery_rate = round((mastery_count / total_flashcards) * 100, 2)
            
            # Subject breakdown
            subjects = {}
            for card in flashcards:
                subject = card[1]
                if subject not in subjects:
                    subjects[subject] = {"count": 0, "reviews": 0, "streaks": []}
                subjects[subject]["count"] += 1
                subjects[subject]["reviews"] += card[3] or 0
                subjects[subject]["streaks"].append(card[4] or 0)
            
            for subject in subjects.values():
                subject["avg_streak"] = round(sum(subject["streaks"]) / len(subject["streaks"]), 2)
                mastery = sum(1 for s in subject["streaks"] if s >= 3)
                subject["mastery_rate"] = round((mastery / subject["count"]) * 100, 2)
                del subject["streaks"]  # Remove raw list
            
            flashcard_stats = {
                "total_flashcards": total_flashcards,
                "total_reviews": total_reviews,
                "average_streak": avg_streak,
                "subject_breakdown": subjects,
                "mastery_rate": mastery_rate
            }
        
        # Bookmark stats
        bookmarks = self.db.execute_query("""
            SELECT id, category, is_read, rating, created_at, accessed_at
            FROM bookmarks
            WHERE created_at >= ? OR accessed_at >= ?
        """, (start_date, start_date))
        
        total_bookmarks = len(bookmarks)
        
        if total_bookmarks == 0:
            bookmark_stats = {
                "total_bookmarks": 0,
                "read_bookmarks": 0,
                "average_rating": 0,
                "category_breakdown": {}
            }
        else:
            read_bookmarks = sum(1 for b in bookmarks if b[2])
            ratings = [b[3] for b in bookmarks if b[3] is not None]
            avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
            
            # Category breakdown
            categories = {}
            for bookmark in bookmarks:
                category = bookmark[1]
                if category not in categories:
                    categories[category] = {"total": 0, "read": 0}
                categories[category]["total"] += 1
                if bookmark[2]:
                    categories[category]["read"] += 1
            
            bookmark_stats = {
                "total_bookmarks": total_bookmarks,
                "read_bookmarks": read_bookmarks,
                "average_rating": avg_rating,
                "category_breakdown": categories
            }
        
        # Course stats
        courses = self.db.execute_query("""
            SELECT id, title, platform, status, total_lessons, completed_lessons,
                   progress_percentage, created_at, updated_at
            FROM courses
            WHERE created_at >= ? OR updated_at >= ?
        """, (start_date, start_date))
        
        total_courses = len(courses)
        
        if total_courses == 0:
            course_stats = {
                "total_courses": 0,
                "in_progress_courses": 0,
                "completed_courses": 0,
                "average_progress": 0,
                "platform_breakdown": {}
            }
        else:
            in_progress = sum(1 for c in courses if c[3] == "in_progress")
            completed = sum(1 for c in courses if c[3] == "completed")
            
            progress_values = [c[6] or 0 for c in courses]
            avg_progress = round(sum(progress_values) / len(progress_values), 2)
            
            # Platform breakdown
            platforms = {}
            for course in courses:
                platform = course[2] or "Unknown"
                if platform not in platforms:
                    platforms[platform] = {"total": 0, "completed": 0, "in_progress": 0}
                platforms[platform]["total"] += 1
                if course[3] == "completed":
                    platforms[platform]["completed"] += 1
                elif course[3] == "in_progress":
                    platforms[platform]["in_progress"] += 1
            
            course_stats = {
                "total_courses": total_courses,
                "in_progress_courses": in_progress,
                "completed_courses": completed,
                "average_progress": avg_progress,
                "platform_breakdown": platforms
            }
        
        return {
            "flashcards": flashcard_stats,
            "bookmarks": bookmark_stats,
            "courses": course_stats
        }
    
    def _calculate_integration_metrics(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics that cross multiple modules"""
        
        # Subject overlap (subjects present in both sessions and flashcards)
        session_subjects = set(report["sessions"]["subject_breakdown"].keys())
        flashcard_subjects = set(report["study"]["flashcards"]["subject_breakdown"].keys())
        
        subject_overlap = session_subjects.intersection(flashcard_subjects)
        
        # Calculate time spent per subject vs. flashcard mastery
        subject_effectiveness = {}
        
        for subject in subject_overlap:
            study_time = report["sessions"]["subject_breakdown"][subject]["duration_hours"]
            mastery_rate = report["study"]["flashcards"]["subject_breakdown"][subject]["mastery_rate"]
            reviews = report["study"]["flashcards"]["subject_breakdown"][subject]["reviews"]
            
            # Calculate effectiveness (mastery per hour of study)
            if study_time > 0:
                effectiveness = round(mastery_rate / study_time, 2)
            else:
                effectiveness = 0
            
            subject_effectiveness[subject] = {
                "study_time_hours": study_time,
                "mastery_rate": mastery_rate,
                "reviews": reviews,
                "effectiveness": effectiveness
            }
        
        # Project productivity (time spent on projects vs. completion)
        project_productivity = {}
        
        for project_name, project_data in report["sessions"]["project_breakdown"].items():
            project_time = project_data["duration_hours"]
            project_sessions = project_data["sessions"]
            
            project_productivity[project_name] = {
                "time_spent_hours": project_time,
                "sessions": project_sessions
            }
        
        # Overall productivity score (weighted score across all modules)
        productivity_factors = []
        
        # Factor 1: Study time (hours per day)
        days = report["period"]["days"]
        study_hours = report["sessions"]["total_time_hours"]
        daily_hours = study_hours / days if days > 0 else 0
        
        # Score: 0-5 based on hours per day (max score at 3 hours/day)
        time_score = min(5, daily_hours * 5 / 3)
        productivity_factors.append(("Study Time", time_score))
        
        # Factor 2: Flashcard mastery
        mastery_rate = report["study"]["flashcards"]["mastery_rate"]
        mastery_score = mastery_rate / 20  # Score: 0-5 (100% mastery = 5)
        productivity_factors.append(("Flashcard Mastery", mastery_score))
        
        # Factor 3: Project completion rate
        active = report["projects"]["active_projects"]
        completed = report["projects"]["completed_projects"]
        if active + completed > 0:
            completion_rate = completed / (active + completed)
            completion_score = completion_rate * 5  # Score: 0-5
        else:
            completion_score = 0
        productivity_factors.append(("Project Completion", completion_score))
        
        # Factor 4: Average session rating
        rating = report["sessions"]["average_rating"]
        rating_score = rating  # Score: 0-5 (already on 5-point scale)
        productivity_factors.append(("Session Rating", rating_score))
        
        # Calculate weighted average (equal weights for now)
        scores = [score for _, score in productivity_factors]
        if scores:
            overall_score = round(sum(scores) / len(scores), 2)
        else:
            overall_score = 0
        
        # Productivity level based on score
        if overall_score >= 4.5:
            level = "Exceptional"
        elif overall_score >= 3.5:
            level = "Excellent"
        elif overall_score >= 2.5:
            level = "Good"
        elif overall_score >= 1.5:
            level = "Fair"
        else:
            level = "Needs Improvement"
        
        return {
            "subject_overlap": list(subject_overlap),
            "subject_effectiveness": subject_effectiveness,
            "project_productivity": project_productivity,
            "productivity_factors": {name: round(score, 2) for name, score in productivity_factors},
            "overall_productivity": {
                "score": overall_score,
                "level": level
            }
        }
    
    def get_subject_time_tracking(self, subject: str) -> Dict[str, Any]:
        """Get detailed time tracking for a specific subject"""
        
        # Get sessions for this subject
        sessions = self.db.execute_query("""
            SELECT id, start_time, end_time, duration, productivity_rating, notes
            FROM sessions
            WHERE subject = ? AND end_time IS NOT NULL
            ORDER BY start_time DESC
        """, (subject,))
        
        # Calculate statistics
        total_sessions = len(sessions)
        
        if total_sessions == 0:
            return {
                "subject": subject,
                "total_sessions": 0,
                "total_time_hours": 0,
                "average_rating": 0,
                "recent_sessions": []
            }
        
        total_duration = sum(s[3] or 0 for s in sessions)
        total_hours = round(total_duration / 3600, 2)
        
        ratings = [s[4] for s in sessions if s[4] is not None]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
        
        # Format recent sessions
        recent_sessions = []
        for session in sessions[:10]:
            session_id, start_time, end_time, duration, rating, notes = session
            
            # Format dates
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time) if end_time else None
            
            start_str = start_dt.strftime("%Y-%m-%d %H:%M")
            end_str = end_dt.strftime("%H:%M") if end_dt else "In progress"
            
            # Format duration
            duration_minutes = round((duration or 0) / 60)
            
            recent_sessions.append({
                "id": session_id,
                "date": start_dt.strftime("%Y-%m-%d"),
                "time": f"{start_str} - {end_str}",
                "duration_minutes": duration_minutes,
                "rating": rating,
                "notes": notes
            })
        
        # Get related flashcards
        flashcards = self.db.execute_query("""
            SELECT COUNT(*), AVG(correct_streak)
            FROM flashcards
            WHERE subject = ?
        """, (subject,))
        
        flashcard_count = flashcards[0][0] if flashcards else 0
        avg_streak = round(flashcards[0][1] or 0, 2) if flashcards else 0
        
        return {
            "subject": subject,
            "total_sessions": total_sessions,
            "total_time_hours": total_hours,
            "average_rating": avg_rating,
            "recent_sessions": recent_sessions,
            "flashcards": {
                "count": flashcard_count,
                "average_streak": avg_streak
            }
        }
    
    def get_project_session_stats(self, project_id: int) -> Dict[str, Any]:
        """Get session statistics for a specific project"""
        
        # Get project details
        project = self.db.execute_query("""
            SELECT name, project_type, language, status, deadline, priority
            FROM projects
            WHERE id = ?
        """, (project_id,))
        
        if not project:
            return {"success": False, "message": "Project not found"}
        
        project_name, project_type, language, status, deadline, priority = project[0]
        
        # Get sessions for this project
        sessions = self.db.execute_query("""
            SELECT id, subject, start_time, end_time, duration, productivity_rating
            FROM sessions
            WHERE project_id = ? AND end_time IS NOT NULL
            ORDER BY start_time DESC
        """, (project_id,))
        
        # Calculate statistics
        total_sessions = len(sessions)
        
        if total_sessions == 0:
            session_stats = {
                "total_sessions": 0,
                "total_time_hours": 0,
                "average_rating": 0,
                "recent_sessions": []
            }
        else:
            total_duration = sum(s[4] or 0 for s in sessions)
            total_hours = round(total_duration / 3600, 2)
            
            ratings = [s[5] for s in sessions if s[5] is not None]
            avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
            
            # Format recent sessions
            recent_sessions = []
            for session in sessions[:10]:
                session_id, subject, start_time, end_time, duration, rating = session
                
                # Format dates
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.fromisoformat(end_time) if end_time else None
                
                # Format duration
                duration_minutes = round((duration or 0) / 60)
                
                recent_sessions.append({
                    "id": session_id,
                    "subject": subject,
                    "date": start_dt.strftime("%Y-%m-%d"),
                    "duration_minutes": duration_minutes,
                    "rating": rating
                })
            
            session_stats = {
                "total_sessions": total_sessions,
                "total_time_hours": total_hours,
                "average_rating": avg_rating,
                "recent_sessions": recent_sessions
            }
        
        return {
            "success": True,
            "project": {
                "id": project_id,
                "name": project_name,
                "type": project_type,
                "language": language,
                "status": status,
                "deadline": deadline,
                "priority": priority
            },
            "sessions": session_stats
        }
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for the StudyDev dashboard"""
        
        # Get recent 7 days of data
        recent_data = self.generate_productivity_report(7)
        
        # Get today's review items
        today = date.today().isoformat()
        
        flashcards_due = self.db.execute_query("""
            SELECT COUNT(*) FROM flashcards WHERE next_review <= ?
        """, (today,))[0][0]
        
        # Get upcoming deadlines (next 7 days)
        target_date = (date.today() + timedelta(days=7)).isoformat()
        
        upcoming_deadlines = self.db.execute_query("""
            SELECT id, name, deadline
            FROM projects 
            WHERE deadline IS NOT NULL 
                AND deadline <= ? 
                AND status != 'completed'
                AND status != 'cancelled'
            ORDER BY deadline ASC
            LIMIT 5
        """, (target_date,))
        
        deadlines = []
        for project in upcoming_deadlines:
            project_id, name, deadline = project
            days_left = (datetime.fromisoformat(deadline).date() - date.today()).days
            
            deadlines.append({
                "id": project_id,
                "name": name,
                "deadline": deadline,
                "days_left": days_left
            })
        
        # Get session streaks (consecutive days with sessions)
        streak = 0
        current_date = date.today()
        
        while True:
            check_date = (current_date - timedelta(days=streak)).isoformat()
            
            sessions = self.db.execute_query("""
                SELECT COUNT(*) FROM sessions 
                WHERE DATE(start_time) = ?
            """, (check_date,))[0][0]
            
            if sessions > 0:
                streak += 1
            else:
                break
        
        # Get recent sessions
        recent_sessions = self.db.execute_query("""
            SELECT s.id, s.session_type, s.subject, s.duration, 
                   s.start_time, s.end_time, p.name as project_name
            FROM sessions s
            LEFT JOIN projects p ON s.project_id = p.id
            WHERE s.end_time IS NOT NULL
            ORDER BY s.start_time DESC
            LIMIT 5
        """)
        
        sessions = []
        for session in recent_sessions:
            session_id, session_type, subject, duration, start_time, end_time, project_name = session
            
            duration_minutes = round((duration or 0) / 60)
            date_str = datetime.fromisoformat(start_time).strftime("%Y-%m-%d")
            
            sessions.append({
                "id": session_id,
                "type": session_type,
                "subject": subject,
                "project": project_name,
                "duration_minutes": duration_minutes,
                "date": date_str
            })
        
        return {
            "flashcards_due": flashcards_due,
            "upcoming_deadlines": deadlines,
            "current_streak": streak,
            "recent_sessions": sessions,
            "recent_stats": {
                "study_hours": recent_data["sessions"]["total_time_hours"],
                "active_projects": recent_data["projects"]["active_projects"],
                "productivity_score": recent_data["integration"]["overall_productivity"]["score"],
                "productivity_level": recent_data["integration"]["overall_productivity"]["level"]
            }
        }