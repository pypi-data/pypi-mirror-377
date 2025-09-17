"""
StudyDev Study Materials Manager - Core Logic
Handles bookmarks, flashcards, course tracking, and study resources
"""

import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
import random
import math

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm

from studydev.core.config import Config
from studydev.core.database import Database

console = Console()

class StudyMaterialsManager:
    """Manages study materials, bookmarks, flashcards, and courses"""
    
    def __init__(self):
        self.config = Config()
        self.db = Database()
    
    # ================================
    # BOOKMARK MANAGEMENT
    # ================================
    
    def add_bookmark(self, url: str, title: str, category: str = "General", 
                    description: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """Add a new bookmark"""
        
        # Check if URL already exists
        existing = self.db.execute_query(
            "SELECT id FROM bookmarks WHERE url = ?", (url,)
        )
        
        if existing:
            return {"success": False, "message": "Bookmark with this URL already exists"}
        
        # Insert bookmark
        tags_json = json.dumps(tags or [])
        
        self.db.execute_update("""
            INSERT INTO bookmarks (title, url, description, category, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, url, description, category, tags_json, datetime.now().isoformat()))
        
        bookmark_id = self.db.execute_query("SELECT last_insert_rowid()")[0][0]
        
        return {
            "success": True,
            "bookmark_id": bookmark_id,
            "message": f"Bookmark '{title}' added successfully"
        }
    
    def list_bookmarks(self, category: str = None, tags: List[str] = None, 
                      search: str = None, is_read: bool = None) -> List[Dict[str, Any]]:
        """List bookmarks with filtering options"""
        
        query = """
            SELECT id, title, url, description, category, tags, is_read, 
                   rating, created_at, accessed_at
            FROM bookmarks
            WHERE 1=1
        """
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if is_read is not None:
            query += " AND is_read = ?"
            params.append(is_read)
        
        if search:
            query += " AND (title LIKE ? OR description LIKE ? OR url LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        query += " ORDER BY created_at DESC"
        
        bookmarks = self.db.execute_query(query, tuple(params))
        
        bookmark_list = []
        for bookmark in bookmarks:
            bookmark_data = {
                "id": bookmark[0],
                "title": bookmark[1],
                "url": bookmark[2],
                "description": bookmark[3],
                "category": bookmark[4],
                "tags": json.loads(bookmark[5] or "[]"),
                "is_read": bool(bookmark[6]),
                "rating": bookmark[7],
                "created_at": bookmark[8],
                "accessed_at": bookmark[9]
            }
            
            # Filter by tags if specified
            if tags:
                bookmark_tags = bookmark_data["tags"]
                if not any(tag in bookmark_tags for tag in tags):
                    continue
            
            bookmark_list.append(bookmark_data)
        
        return bookmark_list
    
    def update_bookmark(self, bookmark_id: int, **updates) -> bool:
        """Update bookmark fields"""
        
        valid_fields = {"title", "description", "category", "is_read", "rating"}
        
        update_fields = []
        params = []
        
        for field, value in updates.items():
            if field in valid_fields:
                update_fields.append(f"{field} = ?")
                params.append(value)
            elif field == "tags":
                update_fields.append("tags = ?")
                params.append(json.dumps(value))
        
        if not update_fields:
            return False
        
        params.append(bookmark_id)
        query = f"UPDATE bookmarks SET {', '.join(update_fields)} WHERE id = ?"
        
        rows_affected = self.db.execute_update(query, tuple(params))
        return rows_affected > 0
    
    def access_bookmark(self, bookmark_id: int) -> bool:
        """Mark bookmark as accessed and update timestamp"""
        
        rows_affected = self.db.execute_update("""
            UPDATE bookmarks 
            SET accessed_at = ?, is_read = 1 
            WHERE id = ?
        """, (datetime.now().isoformat(), bookmark_id))
        
        return rows_affected > 0
    
    def delete_bookmark(self, bookmark_id: int) -> bool:
        """Delete a bookmark"""
        
        rows_affected = self.db.execute_update(
            "DELETE FROM bookmarks WHERE id = ?", (bookmark_id,)
        )
        
        return rows_affected > 0
    
    def get_bookmark_categories(self) -> List[str]:
        """Get all bookmark categories"""
        
        categories = self.db.execute_query("""
            SELECT DISTINCT category FROM bookmarks 
            ORDER BY category
        """)
        
        return [cat[0] for cat in categories]
    
    # ================================
    # FLASHCARD MANAGEMENT  
    # ================================
    
    def add_flashcard(self, question: str, answer: str, subject: str,
                     difficulty: int = 3, tags: List[str] = None) -> Dict[str, Any]:
        """Add a new flashcard"""
        
        tags_json = json.dumps(tags or [])
        
        # Calculate initial review date (tomorrow)
        next_review = (datetime.now() + timedelta(days=1)).date().isoformat()
        
        self.db.execute_update("""
            INSERT INTO flashcards (
                question, answer, subject, difficulty, next_review, 
                tags, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            question, answer, subject, difficulty, next_review,
            tags_json, datetime.now().isoformat()
        ))
        
        flashcard_id = self.db.execute_query("SELECT last_insert_rowid()")[0][0]
        
        return {
            "success": True,
            "flashcard_id": flashcard_id,
            "message": f"Flashcard added to {subject}"
        }
    
    def get_flashcards_for_review(self, subject: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get flashcards due for review"""
        
        today = date.today().isoformat()
        
        query = """
            SELECT id, question, answer, subject, difficulty, 
                   last_reviewed, next_review, review_count, correct_streak, tags
            FROM flashcards
            WHERE next_review <= ?
        """
        params = [today]
        
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        
        query += " ORDER BY next_review ASC LIMIT ?"
        params.append(limit)
        
        flashcards = self.db.execute_query(query, tuple(params))
        
        flashcard_list = []
        for card in flashcards:
            flashcard_data = {
                "id": card[0],
                "question": card[1],
                "answer": card[2],
                "subject": card[3],
                "difficulty": card[4],
                "last_reviewed": card[5],
                "next_review": card[6],
                "review_count": card[7],
                "correct_streak": card[8],
                "tags": json.loads(card[9] or "[]")
            }
            flashcard_list.append(flashcard_data)
        
        return flashcard_list
    
    def review_flashcard(self, flashcard_id: int, correct: bool) -> Dict[str, Any]:
        """Review a flashcard and update spaced repetition schedule"""
        
        # Get current flashcard data
        card = self.db.execute_query("""
            SELECT difficulty, review_count, correct_streak, last_reviewed
            FROM flashcards WHERE id = ?
        """, (flashcard_id,))
        
        if not card:
            return {"success": False, "message": "Flashcard not found"}
        
        difficulty, review_count, correct_streak, last_reviewed = card[0]
        
        # Update review statistics
        new_review_count = (review_count or 0) + 1
        
        if correct:
            new_correct_streak = (correct_streak or 0) + 1
        else:
            new_correct_streak = 0
        
        # Calculate next review interval using spaced repetition
        next_interval = self._calculate_next_interval(
            difficulty, new_correct_streak, correct
        )
        
        next_review_date = (date.today() + timedelta(days=next_interval)).isoformat()
        current_time = datetime.now().isoformat()
        
        # Update flashcard
        self.db.execute_update("""
            UPDATE flashcards 
            SET last_reviewed = ?, next_review = ?, review_count = ?, correct_streak = ?
            WHERE id = ?
        """, (current_time, next_review_date, new_review_count, new_correct_streak, flashcard_id))
        
        return {
            "success": True,
            "next_review_days": next_interval,
            "correct_streak": new_correct_streak,
            "message": "Flashcard reviewed successfully"
        }
    
    def _calculate_next_interval(self, difficulty: int, correct_streak: int, correct: bool) -> int:
        """Calculate next review interval using spaced repetition algorithm"""
        
        if not correct:
            return 1  # Review again tomorrow if incorrect
        
        if correct_streak == 1:
            return 1  # First correct answer - review tomorrow
        elif correct_streak == 2:
            return 3  # Second correct - review in 3 days
        else:
            # Use exponential backoff with difficulty adjustment
            base_interval = 7  # One week base
            multiplier = 1.5 + (correct_streak * 0.1)
            difficulty_factor = (6 - difficulty) / 5  # Easier cards get longer intervals
            
            interval = int(base_interval * multiplier * difficulty_factor)
            return min(interval, 365)  # Maximum 1 year interval
    
    def get_flashcard_subjects(self) -> List[str]:
        """Get all flashcard subjects"""
        
        subjects = self.db.execute_query("""
            SELECT DISTINCT subject FROM flashcards 
            ORDER BY subject
        """)
        
        return [subj[0] for subj in subjects]
    
    def get_flashcard_stats(self, subject: str = None) -> Dict[str, Any]:
        """Get flashcard statistics"""
        
        query = "SELECT COUNT(*) FROM flashcards"
        params = []
        
        if subject:
            query += " WHERE subject = ?"
            params.append(subject)
        
        total_cards = self.db.execute_query(query, tuple(params))[0][0]
        
        # Cards due for review
        today = date.today().isoformat()
        due_query = "SELECT COUNT(*) FROM flashcards WHERE next_review <= ?"
        due_params = [today]
        
        if subject:
            due_query += " AND subject = ?"
            due_params.append(subject)
        
        due_cards = self.db.execute_query(due_query, tuple(due_params))[0][0]
        
        # Average correct streak
        streak_query = "SELECT AVG(correct_streak) FROM flashcards"
        streak_params = []
        
        if subject:
            streak_query += " WHERE subject = ?"
            streak_params.append(subject)
        
        avg_streak = self.db.execute_query(streak_query, tuple(streak_params))[0][0] or 0
        
        return {
            "total_cards": total_cards,
            "due_for_review": due_cards,
            "average_streak": round(avg_streak, 1),
            "mastery_rate": round((avg_streak / 5) * 100, 1) if avg_streak > 0 else 0
        }
    
    # ================================
    # COURSE MANAGEMENT
    # ================================
    
    def add_course(self, title: str, platform: str = None, instructor: str = None,
                  url: str = None, total_lessons: int = None, 
                  target_completion_date: str = None) -> Dict[str, Any]:
        """Add a new course"""
        
        self.db.execute_update("""
            INSERT INTO courses (
                title, platform, instructor, url, total_lessons, 
                target_completion_date, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, platform, instructor, url, total_lessons,
            target_completion_date, datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        course_id = self.db.execute_query("SELECT last_insert_rowid()")[0][0]
        
        return {
            "success": True,
            "course_id": course_id,
            "message": f"Course '{title}' added successfully"
        }
    
    def update_course_progress(self, course_id: int, completed_lessons: int) -> Dict[str, Any]:
        """Update course progress"""
        
        # Get course details
        course = self.db.execute_query("""
            SELECT total_lessons FROM courses WHERE id = ?
        """, (course_id,))
        
        if not course:
            return {"success": False, "message": "Course not found"}
        
        total_lessons = course[0][0]
        
        # Calculate progress percentage
        if total_lessons and total_lessons > 0:
            progress = min(100.0, (completed_lessons / total_lessons) * 100)
        else:
            progress = 0.0
        
        # Determine status
        if progress >= 100:
            status = "completed"
        elif progress > 0:
            status = "in_progress"
        else:
            status = "enrolled"
        
        # Update course
        self.db.execute_update("""
            UPDATE courses 
            SET completed_lessons = ?, progress_percentage = ?, status = ?, updated_at = ?
            WHERE id = ?
        """, (completed_lessons, progress, status, datetime.now().isoformat(), course_id))
        
        return {
            "success": True,
            "progress": progress,
            "status": status,
            "message": f"Progress updated: {progress:.1f}%"
        }
    
    def list_courses(self, status: str = None) -> List[Dict[str, Any]]:
        """List courses with optional status filter"""
        
        query = """
            SELECT id, title, platform, instructor, url, total_lessons,
                   completed_lessons, progress_percentage, status,
                   start_date, target_completion_date, created_at
            FROM courses
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY updated_at DESC"
        
        courses = self.db.execute_query(query, tuple(params))
        
        course_list = []
        for course in courses:
            course_data = {
                "id": course[0],
                "title": course[1],
                "platform": course[2],
                "instructor": course[3],
                "url": course[4],
                "total_lessons": course[5],
                "completed_lessons": course[6] or 0,
                "progress_percentage": course[7] or 0.0,
                "status": course[8],
                "start_date": course[9],
                "target_completion_date": course[10],
                "created_at": course[11]
            }
            course_list.append(course_data)
        
        return course_list
    
    def get_course_stats(self) -> Dict[str, Any]:
        """Get course statistics"""
        
        # Total courses
        total_courses = self.db.execute_query("SELECT COUNT(*) FROM courses")[0][0]
        
        # Completed courses
        completed = self.db.execute_query("""
            SELECT COUNT(*) FROM courses WHERE status = 'completed'
        """)[0][0]
        
        # In progress courses
        in_progress = self.db.execute_query("""
            SELECT COUNT(*) FROM courses WHERE status = 'in_progress'
        """)[0][0]
        
        # Average progress
        avg_progress = self.db.execute_query("""
            SELECT AVG(progress_percentage) FROM courses
        """)[0][0] or 0
        
        return {
            "total_courses": total_courses,
            "completed_courses": completed,
            "in_progress_courses": in_progress,
            "average_progress": round(avg_progress, 1),
            "completion_rate": round((completed / total_courses) * 100, 1) if total_courses > 0 else 0
        }
    
    # ================================
    # REVIEW SYSTEM
    # ================================
    
    def get_review_summary(self) -> Dict[str, Any]:
        """Get summary of items due for review"""
        
        today = date.today().isoformat()
        
        # Flashcards due
        flashcards_due = self.db.execute_query("""
            SELECT COUNT(*) FROM flashcards WHERE next_review <= ?
        """, (today,))[0][0]
        
        # Unread bookmarks
        unread_bookmarks = self.db.execute_query("""
            SELECT COUNT(*) FROM bookmarks WHERE is_read = 0
        """)[0][0]
        
        # Courses in progress
        active_courses = self.db.execute_query("""
            SELECT COUNT(*) FROM courses WHERE status = 'in_progress'
        """)[0][0]
        
        return {
            "flashcards_due": flashcards_due,
            "unread_bookmarks": unread_bookmarks,
            "active_courses": active_courses,
            "total_review_items": flashcards_due + unread_bookmarks
        }