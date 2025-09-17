"""
StudyDev Configuration Management System
Handles all configuration settings, paths, and user preferences
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()

class Config:
    """Configuration manager for StudyDev"""
    
    def __init__(self):
        self.home_path = Path.home()
        self.config_dir = self.home_path / ".studydev"
        self.config_file = self.config_dir / "config.json"
        self.data_dir = self.config_dir / "data"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Load or create configuration
        self._config = self._load_config()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.config_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different data types
        (self.data_dir / "sessions").mkdir(exist_ok=True)
        (self.data_dir / "projects").mkdir(exist_ok=True)
        (self.data_dir / "study_materials").mkdir(exist_ok=True)
        (self.data_dir / "templates").mkdir(exist_ok=True)
        (self.data_dir / "backups").mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                console.print(f"⚠️  Warning: Could not load config file: {e}")
                console.print("Using default configuration...")
        
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration settings"""
        return {
            "user": {
                "name": "",
                "timezone": "UTC",
                "preferred_editor": "nano"
            },
            "session": {
                "pomodoro_duration": 25,  # minutes
                "short_break": 5,         # minutes
                "long_break": 15,         # minutes
                "long_break_after": 4,    # sessions
                "auto_start_breaks": False,
                "notification_sound": True
            },
            "project": {
                "default_git_init": True,
                "auto_readme": True,
                "default_license": "MIT",
                "template_path": str(self.data_dir / "templates")
            },
            "study": {
                "flashcard_review_interval": 7,  # days
                "bookmark_categories": [
                    "Programming", 
                    "Mathematics", 
                    "Science", 
                    "Documentation",
                    "Tutorials",
                    "Research"
                ],
                "course_progress_tracking": True
            },
            "ui": {
                "theme": "default",
                "show_progress_bars": True,
                "rich_output": True,
                "compact_mode": False
            },
            "data": {
                "auto_backup": True,
                "backup_frequency": "daily",  # daily, weekly, monthly
                "keep_backups": 30,  # number of backups to keep
                "export_format": "json"  # json, csv, yaml
            }
        }
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=4, sort_keys=True)
        except IOError as e:
            console.print(f"❌ Error saving config: {e}")
            raise
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'session.pomodoro_duration')"""
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self._config
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the final value
        config[keys[-1]] = value
        self.save_config()
    
    @property
    def config_path(self) -> str:
        """Get the configuration file path"""
        return str(self.config_file)
    
    @property  
    def data_path(self) -> str:
        """Get the data directory path"""
        return str(self.data_dir)
    
    @property
    def database_path(self) -> str:
        """Get the database file path"""
        return str(self.data_dir / "studydev.db")
    
    def get_template_path(self, template_name: str) -> str:
        """Get path for a specific template"""
        return str(self.data_dir / "templates" / f"{template_name}.json")
    
    def get_backup_path(self, backup_name: str) -> str:
        """Get path for a specific backup"""
        return str(self.data_dir / "backups" / backup_name)
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self._config = self._default_config()
        self.save_config()
        console.print("🔄 Configuration reset to defaults")
    
    def display_config(self):
        """Display current configuration in a readable format"""
        from rich.tree import Tree
        
        tree = Tree("🎯 StudyDev Configuration")
        
        for section, settings in self._config.items():
            section_tree = tree.add(f"📁 {section.title()}")
            
            if isinstance(settings, dict):
                for key, value in settings.items():
                    section_tree.add(f"{key}: [bold blue]{value}[/bold blue]")
            else:
                section_tree.add(f"[bold blue]{settings}[/bold blue]")
        
        console.print(tree)