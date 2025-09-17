"""
StudyDev Project Management Commands
Handles academic projects, assignments, deadlines, and project templates
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt

from studydev.modules.project.manager import ProjectManager

console = Console()

# Create the project sub-application
project_app = typer.Typer(
    help="📝 Academic Project Organizer - Manage assignments, deadlines, and project templates",
    rich_markup_mode="rich"
)

@project_app.command("new")
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    project_type: str = typer.Option("academic", help="Project type (academic/personal/work)"),
    language: str = typer.Option(None, help="Programming language"),
    template: str = typer.Option(None, help="Project template to use"),
    deadline: str = typer.Option(None, help="Project deadline (YYYY-MM-DD)"),
    description: str = typer.Option(None, help="Project description"),
    path: str = typer.Option(None, help="Custom project path")
):
    """🚀 Create a new project with optional template"""
    manager = ProjectManager()
    
    console.print(f"\n📝 Creating new {project_type} project: {name}")
    
    # Show available templates if language is specified but template is not
    if language and not template:
        available_templates = manager.get_project_templates()
        if language in available_templates:
            template = language
            console.print(f"📋 Using {language} template")
    
    # Create the project
    result = manager.create_project(
        name=name,
        project_type=project_type,
        language=language,
        template=template,
        deadline=deadline,
        description=description,
        path=path
    )
    
    if result["success"]:
        console.print(f"\n✅ [green]{result['message']}[/green]")
        console.print(f"📁 Path: {result['path']}")
        console.print(f"🆔 Project ID: {result['project_id']}")
        
        if template:
            console.print(f"\n📊 [cyan]Template applied! Your project is ready to use.[/cyan]")
        
        console.print("\n🚀 [bold]Next steps:[/bold]")
        console.print(f"  • cd {result['path']}")
        if template == "python":
            console.print("  • python main.py")
        elif template == "javascript":
            console.print("  • npm start")
        console.print("  • studydev session start --project \"" + name + "\"")
    else:
        console.print(f"\n❌ [red]{result['message']}[/red]")

@project_app.command("list")
def list_projects(
    status: str = typer.Option("all", help="Filter by status (active/completed/paused/all)"),
    project_type: str = typer.Option("all", help="Filter by type (academic/personal/work/all)"),
    sort_by: str = typer.Option("updated_at", help="Sort by field (name/deadline/priority/created_at/updated_at)")
):
    """📋 List all projects with status and details"""
    manager = ProjectManager()
    projects = manager.list_projects(status=status, project_type=project_type, sort_by=sort_by)
    
    if not projects:
        console.print(f"\n📋 [yellow]No projects found matching criteria.[/yellow]")
        console.print("Create your first project with: [cyan]studydev project new \"My Project\"[/cyan]")
        return
    
    console.print(f"\n📋 [bold]Projects ({len(projects)} found)[/bold]")
    console.print(f"[dim]Filtered by: Status={status}, Type={project_type}, Sorted by={sort_by}[/dim]")
    
    # Create projects table
    projects_table = Table()
    projects_table.add_column("ID", style="dim", width=4)
    projects_table.add_column("Name", style="bold blue")
    projects_table.add_column("Type", style="magenta")
    projects_table.add_column("Language", style="cyan")
    projects_table.add_column("Status", justify="center")
    projects_table.add_column("Priority", justify="center")
    projects_table.add_column("Deadline", style="yellow")
    projects_table.add_column("Path", style="green")
    
    for project in projects:
        # Status icon
        status_icons = {
            "active": "✅",
            "completed": "✔️",
            "paused": "⏸️", 
            "cancelled": "❌"
        }
        status_display = f"{status_icons.get(project['status'], project['status'])} {project['status']}"
        
        # Priority stars
        priority_stars = "⭐" * project['priority']
        
        # Deadline formatting
        deadline_display = "N/A"
        if project['deadline']:
            days_left = project['days_until_deadline']
            if days_left is not None:
                if days_left < 0:
                    deadline_display = f"[red]{project['deadline']} (OVERDUE)[/red]"
                elif days_left <= 3:
                    deadline_display = f"[yellow]{project['deadline']} ({days_left}d left)[/yellow]"
                else:
                    deadline_display = f"{project['deadline']} ({days_left}d left)"
            else:
                deadline_display = project['deadline']
        
        # Truncate path for display
        path_display = project['path'][-40:] if len(project['path']) > 40 else project['path']
        
        projects_table.add_row(
            str(project['id']),
            project['name'],
            project['type'].title(),
            project['language'] or "N/A",
            status_display,
            priority_stars,
            deadline_display,
            path_display
        )
    
    console.print(projects_table)
    
    # Show upcoming deadlines if any
    deadlines = manager.get_upcoming_deadlines()
    if deadlines:
        console.print(f"\n⏰ [bold red]Upcoming Deadlines ({len(deadlines)})[/bold red]")
        for deadline in deadlines[:3]:  # Show top 3
            urgency_colors = {
                "overdue": "red",
                "urgent": "red",
                "soon": "yellow",
                "upcoming": "green"
            }
            color = urgency_colors.get(deadline['urgency'], "white")
            console.print(f"  • [{color}]{deadline['name']}: {deadline['deadline']} ({deadline['days_left']}d left)[/{color}]")

@project_app.command("deadline")
def manage_deadlines(
    action: str = typer.Argument(..., help="Action (list/upcoming)"),
    days: int = typer.Option(7, help="Number of days to look ahead (for upcoming)")
):
    """⏰ Manage project deadlines and get reminders"""
    manager = ProjectManager()
    
    if action == "list":
        projects = manager.list_projects()
        projects_with_deadlines = [p for p in projects if p['deadline']]
        
        if not projects_with_deadlines:
            console.print("\n⏰ [yellow]No projects with deadlines found.[/yellow]")
            return
        
        console.print(f"\n⏰ [bold]Project Deadlines ({len(projects_with_deadlines)})[/bold]")
        
        deadline_table = Table()
        deadline_table.add_column("Project", style="bold blue")
        deadline_table.add_column("Deadline", style="yellow")
        deadline_table.add_column("Days Left", justify="right")
        deadline_table.add_column("Status", justify="center")
        deadline_table.add_column("Priority", justify="center")
        
        # Sort by deadline
        projects_with_deadlines.sort(key=lambda x: x['deadline'])
        
        for project in projects_with_deadlines:
            days_left = project['days_until_deadline']
            
            # Format days left with color
            if days_left is None:
                days_display = "N/A"
            elif days_left < 0:
                days_display = f"[red]{abs(days_left)} overdue[/red]"
            elif days_left == 0:
                days_display = "[red]TODAY![/red]"
            elif days_left <= 3:
                days_display = f"[yellow]{days_left}[/yellow]"
            else:
                days_display = str(days_left)
            
            # Status icons
            status_icons = {
                "active": "✅",
                "completed": "✔️",
                "paused": "⏸️",
                "cancelled": "❌"
            }
            status_display = status_icons.get(project['status'], project['status'])
            
            # Priority stars
            priority_stars = "⭐" * project['priority']
            
            deadline_table.add_row(
                project['name'],
                project['deadline'],
                days_display,
                status_display,
                priority_stars
            )
        
        console.print(deadline_table)
    
    elif action == "upcoming":
        deadlines = manager.get_upcoming_deadlines(days)
        
        if not deadlines:
            console.print(f"\n⏰ [green]No upcoming deadlines in the next {days} days![/green]")
            return
        
        console.print(f"\n⏰ [bold red]Upcoming Deadlines (next {days} days)[/bold red]")
        
        upcoming_table = Table()
        upcoming_table.add_column("Project", style="bold blue")
        upcoming_table.add_column("Deadline", style="yellow")
        upcoming_table.add_column("Days Left", justify="right")
        upcoming_table.add_column("Urgency", justify="center")
        upcoming_table.add_column("Priority", justify="center")
        
        for deadline in deadlines:
            # Urgency icons and colors
            urgency_display = {
                "overdue": "[red]🔥 OVERDUE[/red]",
                "urgent": "[red]⚠️ URGENT[/red]",
                "soon": "[yellow]⏰ SOON[/yellow]",
                "upcoming": "[green]📅 UPCOMING[/green]"
            }
            
            days_display = str(deadline['days_left']) if deadline['days_left'] >= 0 else f"{abs(deadline['days_left'])} overdue"
            priority_stars = "⭐" * deadline['priority']
            
            upcoming_table.add_row(
                deadline['name'],
                deadline['deadline'],
                days_display,
                urgency_display.get(deadline['urgency'], deadline['urgency']),
                priority_stars
            )
        
        console.print(upcoming_table)
        
        # Show actionable suggestions
        overdue_count = sum(1 for d in deadlines if d['urgency'] == 'overdue')
        urgent_count = sum(1 for d in deadlines if d['urgency'] == 'urgent')
        
        if overdue_count > 0:
            console.print(f"\n🔥 [bold red]You have {overdue_count} overdue projects![/bold red]")
            console.print("[red]Consider updating project status or extending deadlines.[/red]")
        elif urgent_count > 0:
            console.print(f"\n⚠️ [yellow]You have {urgent_count} urgent projects to focus on![/yellow]")
            console.print("[yellow]Start a session: studydev session start --project \"Project Name\"[/yellow]")
    
    else:
        console.print(f"❌ [red]Unknown action: {action}. Use 'list' or 'upcoming'[/red]")

@project_app.command("update")
def update_project(
    project_id: int = typer.Argument(..., help="Project ID to update"),
    status: str = typer.Option(None, help="New status (active/completed/paused/cancelled)"),
    deadline: str = typer.Option(None, help="New deadline (YYYY-MM-DD)"),
    priority: int = typer.Option(None, help="New priority (1-5)"),
    name: str = typer.Option(None, help="New project name"),
    description: str = typer.Option(None, help="New project description")
):
    """✏️ Update project details (status, deadline, priority, etc.)"""
    manager = ProjectManager()
    
    # Check if project exists
    projects = manager.list_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        console.print(f"❌ [red]Project with ID {project_id} not found[/red]")
        console.print("\n📋 Available projects:")
        for p in projects[:5]:  # Show first 5 projects
            console.print(f"  • ID {p['id']}: {p['name']} ({p['status']})")
        return
    
    console.print(f"\n✏️ Updating project: [bold blue]{project['name']}[/bold blue] (ID: {project_id})")
    
    # Update fields
    updates = {}
    update_messages = []
    
    if status:
        if status not in ['active', 'completed', 'paused', 'cancelled']:
            console.print("❌ [red]Invalid status. Use: active/completed/paused/cancelled[/red]")
            return
        updates['status'] = status
        update_messages.append(f"Status: {project['status']} → [green]{status}[/green]")
    
    if deadline:
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(deadline, '%Y-%m-%d')
            updates['deadline'] = deadline
            update_messages.append(f"Deadline: {project.get('deadline', 'None')} → [yellow]{deadline}[/yellow]")
        except ValueError:
            console.print("❌ [red]Invalid date format. Use YYYY-MM-DD[/red]")
            return
    
    if priority:
        if not 1 <= priority <= 5:
            console.print("❌ [red]Priority must be between 1 and 5[/red]")
            return
        updates['priority'] = priority
        update_messages.append(f"Priority: {'⭐' * project['priority']} → [yellow]{'⭐' * priority}[/yellow]")
    
    if name:
        updates['name'] = name
        update_messages.append(f"Name: {project['name']} → [blue]{name}[/blue]")
    
    if description:
        updates['description'] = description
        update_messages.append(f"Description updated")
    
    if not updates:
        console.print("❌ [yellow]No updates specified. Use --status, --deadline, --priority, --name, or --description[/yellow]")
        return
    
    # Apply updates
    result = manager.update_project(project_id, **updates)
    
    if result['success']:
        console.print(f"\n✅ [green]{result['message']}[/green]")
        
        # Show what changed
        console.print("\n📊 [bold]Changes made:[/bold]")
        for msg in update_messages:
            console.print(f"  • {msg}")
        
        # Show celebration for completion
        if status == 'completed':
            console.print("\n🎉 [bold green]Congratulations on completing your project![/bold green]")
            console.print("🏆 [cyan]Another step towards your goals! Keep up the great work![/cyan]")
    else:
        console.print(f"\n❌ [red]{result['message']}[/red]")

@project_app.command("template")
def manage_templates(
    action: str = typer.Argument(..., help="Action (list/show)"),
    name: str = typer.Option(None, help="Template name to show details")
):
    """📋 Manage project templates for different languages"""
    manager = ProjectManager()
    
    if action == "list":
        templates = manager.get_project_templates()
        
        if not templates:
            console.print("\n📋 [yellow]No templates found.[/yellow]")
            return
        
        console.print(f"\n📋 [bold]Available Templates ({len(templates)})[/bold]")
        
        template_table = Table()
        template_table.add_column("Template Name", style="cyan")
        template_table.add_column("Language", style="green")
        template_table.add_column("Description", style="dim")
        
        for template_name in templates:
            # Try to load template details
            template_file = manager.templates_dir / f"{template_name}.json"
            if template_file.exists():
                try:
                    import json
                    with open(template_file, 'r') as f:
                        template_data = json.load(f)
                    
                    template_table.add_row(
                        template_name,
                        template_data.get("language", "N/A"),
                        template_data.get("description", "No description")
                    )
                except:
                    template_table.add_row(
                        template_name,
                        "Unknown",
                        "Template file corrupted"
                    )
            else:
                template_table.add_row(template_name, "Unknown", "Template not found")
        
        console.print(template_table)
        console.print("\n🚀 [cyan]Use a template with: studydev project new \"My Project\" --template <name>[/cyan]")
    
    elif action == "show":
        if not name:
            console.print("❌ [red]Template name required for 'show' action[/red]")
            return
        
        template_file = manager.templates_dir / f"{name}.json"
        if not template_file.exists():
            console.print(f"❌ [red]Template '{name}' not found[/red]")
            return
        
        try:
            import json
            with open(template_file, 'r') as f:
                template_data = json.load(f)
            
            console.print(f"\n📋 [bold]Template: {name}[/bold]")
            console.print(f"Language: {template_data.get('language', 'N/A')}")
            console.print(f"Description: {template_data.get('description', 'N/A')}")
            
            files = template_data.get('files', {})
            if files:
                console.print(f"\n📁 [bold]Files ({len(files)})[/bold]")
                for file_path in files.keys():
                    console.print(f"  • {file_path}")
        
        except Exception as e:
            console.print(f"❌ [red]Failed to load template: {e}[/red]")
    
    else:
        console.print(f"❌ [red]Unknown action: {action}. Use 'list' or 'show'[/red]")
