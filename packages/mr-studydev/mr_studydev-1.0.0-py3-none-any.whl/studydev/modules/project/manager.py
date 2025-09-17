"""
StudyDev Project Manager - Core Logic
Handles project creation, templates, deadlines, and Git integration
"""

import os
import json
import subprocess
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm

from studydev.core.config import Config
from studydev.core.database import Database

console = Console()

class ProjectManager:
    """Manages academic and coding projects with templates and Git integration"""
    
    def __init__(self):
        self.config = Config()
        self.db = Database()
        self.templates_dir = Path(self.config.data_path) / "templates" / "projects"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._init_default_templates()
    
    def create_project(self, name: str, project_type: str = "academic", 
                      language: str = None, template: str = None, 
                      deadline: str = None, description: str = None,
                      path: str = None) -> Dict[str, Any]:
        """Create a new project with optional template and Git initialization"""
        
        # Check if project already exists
        existing = self.db.execute_query(
            "SELECT id FROM projects WHERE name = ?", (name,)
        )
        
        if existing:
            return {"success": False, "message": f"Project '{name}' already exists"}
        
        # Determine project path
        if path is None:
            # Create in current directory
            project_path = Path.cwd() / name.replace(" ", "_").lower()
        else:
            project_path = Path(path).expanduser()
        
        # Create project directory
        try:
            project_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {"success": False, "message": f"Failed to create directory: {e}"}
        
        # Apply template if specified
        template_applied = False
        if template or language:
            template_name = template or language
            template_applied = self._apply_template(template_name, project_path, name, language)
        
        # Initialize Git repository if enabled
        git_repo = None
        if self.config.get("project.default_git_init", True):
            git_repo = self._init_git_repo(project_path)
        
        # Parse deadline
        deadline_date = None
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date().isoformat()
            except ValueError:
                console.print(f"⚠️  [yellow]Invalid deadline format. Use YYYY-MM-DD[/yellow]")
        
        # Create database record
        project_data = {
            "name": name,
            "description": description,
            "project_type": project_type,
            "language": language,
            "path": str(project_path),
            "git_repo": git_repo,
            "deadline": deadline_date,
            "status": "active",
            "priority": 3,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insert into database
        project_id = self._create_project_record(project_data)
        project_data["id"] = project_id
        
        # Success message
        success_msg = f"Project '{name}' created successfully!"
        if template_applied:
            success_msg += f" (Template: {template_name})"
        if git_repo:
            success_msg += " (Git initialized)"
        
        return {
            "success": True, 
            "project_id": project_id,
            "message": success_msg,
            "path": str(project_path)
        }
    
    def list_projects(self, status: str = "all", project_type: str = "all",
                     sort_by: str = "updated_at") -> List[Dict[str, Any]]:
        """List all projects with filtering options"""
        
        # Build query
        query = """
            SELECT id, name, description, project_type, language, path, 
                   deadline, status, priority, created_at, updated_at
            FROM projects
            WHERE 1=1
        """
        params = []
        
        if status != "all":
            query += " AND status = ?"
            params.append(status)
        
        if project_type != "all":
            query += " AND project_type = ?"
            params.append(project_type)
        
        # Add ordering
        valid_sort_fields = ["name", "deadline", "priority", "created_at", "updated_at"]
        if sort_by in valid_sort_fields:
            query += f" ORDER BY {sort_by} DESC"
        else:
            query += " ORDER BY updated_at DESC"
        
        # Execute query
        projects = self.db.execute_query(query, tuple(params))
        
        # Format results
        project_list = []
        for project in projects:
            project_data = {
                "id": project[0],
                "name": project[1],
                "description": project[2],
                "type": project[3],
                "language": project[4],
                "path": project[5],
                "deadline": project[6],
                "status": project[7],
                "priority": project[8],
                "created_at": project[9],
                "updated_at": project[10],
                "days_until_deadline": self._days_until_deadline(project[6])
            }
            project_list.append(project_data)
        
        return project_list
    
    def get_upcoming_deadlines(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get projects with deadlines in the specified number of days"""
        
        target_date = (date.today() + timedelta(days=days_ahead)).isoformat()
        
        projects = self.db.execute_query("""
            SELECT id, name, deadline, status, priority
            FROM projects 
            WHERE deadline IS NOT NULL 
                AND deadline <= ? 
                AND status != 'completed'
                AND status != 'cancelled'
            ORDER BY deadline ASC
        """, (target_date,))
        
        deadlines = []
        for project in projects:
            project_id, name, deadline, status, priority = project
            days_left = self._days_until_deadline(deadline)
            
            # Determine urgency
            if days_left < 0:
                urgency = "overdue"
            elif days_left <= 1:
                urgency = "urgent"
            elif days_left <= 3:
                urgency = "soon"
            else:
                urgency = "upcoming"
            
            deadlines.append({
                "id": project_id,
                "name": name,
                "deadline": deadline,
                "days_left": days_left,
                "status": status,
                "priority": priority,
                "urgency": urgency
            })
        
        return deadlines
    
    def update_project(self, project_id: int, **updates) -> bool:
        """Update project fields"""
        
        # Build update query dynamically
        valid_fields = {
            "name", "description", "project_type", "language", 
            "deadline", "status", "priority"
        }
        
        update_fields = []
        params = []
        
        for field, value in updates.items():
            if field in valid_fields:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return False
        
        # Add updated timestamp
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(project_id)
        
        query = f"UPDATE projects SET {', '.join(update_fields)} WHERE id = ?"
        
        rows_affected = self.db.execute_update(query, tuple(params))
        return rows_affected > 0
    
    def delete_project(self, project_id: int, remove_files: bool = False) -> bool:
        """Delete a project and optionally its files"""
        
        # Get project info first
        project = self.db.execute_query(
            "SELECT name, path FROM projects WHERE id = ?", (project_id,)
        )
        
        if not project:
            return False
        
        project_name, project_path = project[0]
        
        # Remove files if requested
        if remove_files and project_path and Path(project_path).exists():
            try:
                if Confirm.ask(f"Really delete project files at {project_path}?"):
                    shutil.rmtree(project_path)
                    console.print(f"🗑️  [yellow]Project files deleted: {project_path}[/yellow]")
            except Exception as e:
                console.print(f"⚠️  [red]Failed to delete files: {e}[/red]")
        
        # Remove from database
        rows_affected = self.db.execute_update(
            "DELETE FROM projects WHERE id = ?", (project_id,)
        )
        
        if rows_affected > 0:
            console.print(f"✅ [green]Project '{project_name}' deleted from database[/green]")
            return True
        
        return False
    
    def get_project_templates(self) -> List[str]:
        """Get list of available project templates"""
        templates = []
        
        # Get built-in templates
        for template_file in self.templates_dir.glob("*.json"):
            template_name = template_file.stem
            templates.append(template_name)
        
        return sorted(templates)
    
    def create_template(self, name: str, language: str, files: Dict[str, str],
                       dependencies: List[str] = None) -> bool:
        """Create a custom project template"""
        
        template_data = {
            "name": name,
            "language": language,
            "description": f"Custom template for {language} projects",
            "files": files,
            "dependencies": dependencies or [],
            "created_at": datetime.now().isoformat()
        }
        
        template_path = self.templates_dir / f"{name}.json"
        
        try:
            with open(template_path, 'w') as f:
                json.dump(template_data, f, indent=4)
            
            console.print(f"✅ [green]Template '{name}' created successfully[/green]")
            return True
        except Exception as e:
            console.print(f"❌ [red]Failed to create template: {e}[/red]")
            return False
    
    def _apply_template(self, template_name: str, project_path: Path, 
                       project_name: str, language: str) -> bool:
        """Apply a template to the project directory"""
        
        template_file = self.templates_dir / f"{template_name}.json"
        
        if not template_file.exists():
            console.print(f"⚠️  [yellow]Template '{template_name}' not found[/yellow]")
            return False
        
        try:
            with open(template_file, 'r') as f:
                template = json.load(f)
            
            # Create template files
            for file_path, content in template.get("files", {}).items():
                file_full_path = project_path / file_path
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Replace placeholders in content
                content = content.replace("{{PROJECT_NAME}}", project_name)
                content = content.replace("{{LANGUAGE}}", language or "")
                content = content.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
                content = content.replace("{{AUTHOR}}", self.config.get("user.name", ""))
                
                with open(file_full_path, 'w') as f:
                    f.write(content)
            
            console.print(f"📋 [green]Template '{template_name}' applied successfully[/green]")
            return True
            
        except Exception as e:
            console.print(f"❌ [red]Failed to apply template: {e}[/red]")
            return False
    
    def _init_git_repo(self, project_path: Path) -> Optional[str]:
        """Initialize Git repository and return remote URL if set"""
        
        try:
            # Initialize git repo
            subprocess.run(
                ["git", "init"], 
                cwd=project_path, 
                capture_output=True, 
                check=True
            )
            
            # Create initial commit if files exist
            files = list(project_path.glob("*"))
            if files:
                subprocess.run(
                    ["git", "add", "."], 
                    cwd=project_path, 
                    capture_output=True, 
                    check=True
                )
                
                subprocess.run(
                    ["git", "commit", "-m", "Initial commit"], 
                    cwd=project_path, 
                    capture_output=True, 
                    check=True
                )
            
            console.print("🔧 [green]Git repository initialized[/green]")
            return str(project_path)
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            console.print("⚠️  [yellow]Git initialization failed - continuing without Git[/yellow]")
            return None
    
    def _create_project_record(self, project_data: Dict[str, Any]) -> int:
        """Create project record in database and return ID"""
        
        self.db.execute_update("""
            INSERT INTO projects (
                name, description, project_type, language, path, 
                git_repo, deadline, status, priority, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_data["name"],
            project_data.get("description"),
            project_data["project_type"],
            project_data.get("language"),
            project_data["path"],
            project_data.get("git_repo"),
            project_data.get("deadline"),
            project_data["status"],
            project_data["priority"],
            project_data["created_at"],
            project_data["updated_at"]
        ))
        
        # Get the ID of inserted record
        project_id = self.db.execute_query("SELECT last_insert_rowid()")[0][0]
        return project_id
    
    def _days_until_deadline(self, deadline_str: str) -> Optional[int]:
        """Calculate days until deadline"""
        if not deadline_str:
            return None
        
        try:
            deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            return (deadline_date - date.today()).days
        except ValueError:
            return None
    
    def _init_default_templates(self):
        """Initialize default project templates"""
        
        templates = {
            "python": {
                "name": "python",
                "language": "python", 
                "description": "Basic Python project template",
                "files": {
                    "main.py": '#!/usr/bin/env python3\n"""\n{{PROJECT_NAME}}\nCreated on {{DATE}}\nAuthor: {{AUTHOR}}\n"""\n\ndef main():\n    print("Hello, {{PROJECT_NAME}}!")\n\nif __name__ == "__main__":\n    main()\n',
                    "README.md": "# {{PROJECT_NAME}}\n\nA Python project created with StudyDev.\n\n## Description\n\nAdd your project description here.\n\n## Installation\n\n```bash\npython -m venv venv\nsource venv/bin/activate  # On Windows: venv\\Scripts\\activate\npip install -r requirements.txt\n```\n\n## Usage\n\n```bash\npython main.py\n```\n\n## Author\n\n{{AUTHOR}}\n",
                    "requirements.txt": "# Add your Python dependencies here\n",
                    ".gitignore": "__pycache__/\n*.py[cod]\n*$py.class\nvenv/\n.env\n*.egg-info/\nbuild/\ndist/\n"
                }
            },
            
            "javascript": {
                "name": "javascript",
                "language": "javascript",
                "description": "Basic JavaScript/Node.js project template",
                "files": {
                    "index.js": '/**\n * {{PROJECT_NAME}}\n * Created on {{DATE}}\n * Author: {{AUTHOR}}\n */\n\nconsole.log("Hello, {{PROJECT_NAME}}!");\n',
                    "package.json": '{\n  "name": "{{PROJECT_NAME}}",\n  "version": "1.0.0",\n  "description": "A JavaScript project created with StudyDev",\n  "main": "index.js",\n  "scripts": {\n    "start": "node index.js",\n    "test": "echo \\"Error: no test specified\\" && exit 1"\n  },\n  "author": "{{AUTHOR}}",\n  "license": "MIT"\n}\n',
                    "README.md": "# {{PROJECT_NAME}}\n\nA JavaScript project created with StudyDev.\n\n## Description\n\nAdd your project description here.\n\n## Installation\n\n```bash\nnpm install\n```\n\n## Usage\n\n```bash\nnpm start\n```\n\n## Author\n\n{{AUTHOR}}\n",
                    ".gitignore": "node_modules/\nnpm-debug.log*\n.env\n.DS_Store\n"
                }
            }
        }
        
        # Create template files if they don't exist
        for template_name, template_data in templates.items():
            template_file = self.templates_dir / f"{template_name}.json"
            
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    json.dump(template_data, f, indent=4)
    
    def update_project(self, project_id: int, **updates) -> Dict[str, Any]:
        """Update project fields in the database"""
        
        if not updates:
            return {
                "success": False,
                "message": "No updates provided"
            }
        
        try:
            # Build update query dynamically
            set_clauses = []
            values = []
            
            # Add updated_at timestamp
            updates['updated_at'] = datetime.now().isoformat()
            
            for field, value in updates.items():
                set_clauses.append(f"{field} = ?")
                values.append(value)
            
            # Add project_id for WHERE clause
            values.append(project_id)
            
            query = f"""
                UPDATE projects 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """
            
            self.db.execute_update(query, tuple(values))
            
            return {
                "success": True,
                "message": f"Project {project_id} updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update project: {str(e)}"
            }
