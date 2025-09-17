"""
StudyDev Database Management System
Handles all data persistence using SQLite
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager

from studydev.core.config import Config
from rich.console import Console

console = Console()

class Database:
    """Database manager for StudyDev using SQLite"""
    
    def __init__(self):
        self.config = Config()
        self.db_path = self.config.database_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database with all required tables"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create all tables
                self._create_sessions_table(cursor)
                self._create_projects_table(cursor)
                self._create_study_materials_table(cursor)
                self._create_flashcards_table(cursor)
                self._create_bookmarks_table(cursor)
                self._create_courses_table(cursor)
                
                conn.commit()
                
        except sqlite3.Error as e:
            console.print(f"❌ Database initialization error: {e}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def _create_sessions_table(self, cursor):
        """Create sessions table for time tracking"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type TEXT NOT NULL CHECK(session_type IN ('study', 'break', 'project')),
                project_id INTEGER,
                subject TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration INTEGER, -- in seconds
                notes TEXT,
                productivity_rating INTEGER CHECK(productivity_rating BETWEEN 1 AND 5),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_project_id ON sessions(project_id)")
    
    def _create_projects_table(self, cursor):
        """Create projects table for academic/coding projects"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                project_type TEXT NOT NULL CHECK(project_type IN ('academic', 'personal', 'work')),
                language TEXT, -- Programming language if applicable
                path TEXT, -- Local file system path
                git_repo TEXT, -- Git repository URL
                deadline TEXT, -- ISO format date
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'completed', 'paused', 'cancelled')),
                priority INTEGER DEFAULT 3 CHECK(priority BETWEEN 1 AND 5),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_study_materials_table(self, cursor):
        """Create study materials table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                material_type TEXT NOT NULL CHECK(material_type IN ('note', 'reference', 'summary', 'exercise')),
                subject TEXT NOT NULL,
                tags TEXT, -- JSON array of tags
                file_path TEXT, -- Path to associated file
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_flashcards_table(self, cursor):
        """Create flashcards table for spaced repetition"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                subject TEXT NOT NULL,
                difficulty INTEGER DEFAULT 3 CHECK(difficulty BETWEEN 1 AND 5),
                last_reviewed TEXT,
                next_review TEXT,
                review_count INTEGER DEFAULT 0,
                correct_streak INTEGER DEFAULT 0,
                tags TEXT, -- JSON array of tags
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_flashcards_next_review ON flashcards(next_review)")
    
    def _create_bookmarks_table(self, cursor):
        """Create bookmarks table for study resources"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                tags TEXT, -- JSON array of tags
                is_read BOOLEAN DEFAULT FALSE,
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                accessed_at TEXT
            )
        """)
    
    def _create_courses_table(self, cursor):
        """Create courses table for online course tracking"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                platform TEXT, -- Coursera, Udemy, etc.
                instructor TEXT,
                url TEXT,
                total_lessons INTEGER,
                completed_lessons INTEGER DEFAULT 0,
                progress_percentage REAL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'enrolled' CHECK(status IN ('enrolled', 'in_progress', 'completed', 'paused')),
                start_date TEXT,
                target_completion_date TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def is_connected(self) -> bool:
        """Check if database connection is working"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except sqlite3.Error:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Count records in each table
                tables = ['sessions', 'projects', 'study_materials', 'flashcards', 'bookmarks', 'courses']
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
                
                # Additional stats
                cursor.execute("""
                    SELECT 
                        COALESCE(SUM(duration), 0) as total_study_time,
                        COUNT(DISTINCT DATE(start_time)) as study_days
                    FROM sessions 
                    WHERE session_type = 'study'
                """)
                
                result = cursor.fetchone()
                stats['total_study_time_seconds'] = result[0] or 0
                stats['study_days'] = result[1] or 0
                stats['total_study_time_hours'] = round((result[0] or 0) / 3600, 2)
                
        except sqlite3.Error as e:
            console.print(f"❌ Error getting stats: {e}")
            
        return stats
    
    def backup_database(self, backup_path: str = None) -> str:
        """Create a backup of the database"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.config.get_backup_path(f"studydev_backup_{timestamp}.db")
        
        try:
            # Create backup directory if it doesn't exist
            Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            
            console.print(f"✅ Database backed up to: {backup_path}")
            return backup_path
            
        except sqlite3.Error as e:
            console.print(f"❌ Backup failed: {e}")
            raise
    
    def restore_database(self, backup_path: str):
        """Restore database from backup"""
        if not Path(backup_path).exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        try:
            # Create a backup of current database first
            current_backup = self.backup_database()
            console.print(f"📦 Current database backed up to: {current_backup}")
            
            # Restore from backup
            with sqlite3.connect(backup_path) as source:
                with sqlite3.connect(self.db_path) as target:
                    source.backup(target)
            
            console.print(f"✅ Database restored from: {backup_path}")
            
        except sqlite3.Error as e:
            console.print(f"❌ Restore failed: {e}")
            raise
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            console.print(f"❌ Query execution failed: {e}")
            raise
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            console.print(f"❌ Update execution failed: {e}")
            raise