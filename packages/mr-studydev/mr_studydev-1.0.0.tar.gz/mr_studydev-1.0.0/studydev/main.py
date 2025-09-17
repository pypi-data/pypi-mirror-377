#!/usr/bin/env python3
"""
StudyDev - Ultimate Student & Developer Productivity CLI Tool
Main entry point and command dispatcher
"""

import typer
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich import box

from studydev.core.config import Config
from studydev.core.database import Database
from studydev.modules.session.commands import session_app
from studydev.modules.project.commands import project_app
from studydev.modules.study.commands import study_app
from studydev.utils.interactive import InteractiveUI

# Initialize Rich console and interactive UI
console = Console()
interactive_ui = InteractiveUI()

# Main CLI application
app = typer.Typer(
    name="studydev",
    help="🎯 Ultimate Student & Developer Productivity CLI Tool",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Add sub-applications
app.add_typer(session_app, name="session", help="📚 Study & Dev Session Manager")
app.add_typer(project_app, name="project", help="📝 Academic Project Organizer") 
app.add_typer(study_app, name="study", help="🔖 Study Material Aggregator")


@app.command()
def init():
    """🚀 Initialize StudyDev configuration and database"""
    try:
        # Show beautiful welcome animation
        interactive_ui.show_welcome_animation()
        
        # Initialize system
        interactive_ui.show_loading_animation("Initializing StudyDev system...", 1.5)
        
        config = Config()
        db = Database()
        
        console.print("\n🎉 [bold green]StudyDev initialized successfully![/bold green]")
        console.print(f"📍 Config location: {config.config_path}")
        console.print(f"📁 Data location: {config.data_path}")
        console.print("\n✨ You're ready to boost your productivity!")
        
        # Show quick start menu
        show_quick_start = Confirm.ask("\n🚀 Would you like to see the quick start guide?")
        if show_quick_start:
            show_quick_start_guide()
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Initialization failed:[/bold red] {e}")
        raise typer.Exit(1)


@app.command() 
def status():
    """📊 Show StudyDev status and statistics"""
    try:
        config = Config()
        db = Database()
        
        # Show loading animation
        interactive_ui.show_loading_animation("Loading your StudyDev dashboard...", 1.0)
        
        # Get comprehensive status data
        from studydev.utils.integration import IntegrationManager
        integration = IntegrationManager()
        dashboard_data = integration.generate_dashboard_data()
        
        # Calculate productivity metrics
        recent_stats = dashboard_data["recent_stats"]
        productivity_score = recent_stats["productivity_score"]
        
        # Show productivity gauge
        productivity_gauge = interactive_ui.create_productivity_gauge(productivity_score)
        console.print(productivity_gauge)
        
        # Show comprehensive status summary
        status_data = {
            "total_sessions": dashboard_data.get("total_sessions", 0),
            "total_hours": dashboard_data.get("total_hours", 0),
            "streak": dashboard_data.get("current_streak", 0),
            "active_projects": recent_stats.get("active_projects", 0),
            "completed_projects": dashboard_data.get("completed_projects", 0),
            "due_soon": len([d for d in dashboard_data.get("upcoming_deadlines", []) if d.get("days_left", 0) <= 7]),
            "total_flashcards": dashboard_data.get("total_flashcards", 0),
            "flashcards_due": dashboard_data.get("flashcards_due", 0),
            "total_bookmarks": dashboard_data.get("total_bookmarks", 0),
            "productivity_score": productivity_score,
            "productivity_level": recent_stats.get("productivity_level", "Starting")
        }
        
        status_summary = interactive_ui.create_status_summary(status_data)
        console.print(status_summary)
        
        # Show streak celebration if applicable
        if dashboard_data["current_streak"] >= 3:
            interactive_ui.show_streak_celebration(dashboard_data["current_streak"])
        
        # System status
        console.print(f"\n📍 [dim]Config Path: {config.config_path}[/dim]")
        console.print(f"📁 [dim]Data Path: {config.data_path}[/dim]")
        console.print(f"🗃️  [dim]Database: {'✅ Connected' if db.is_connected() else '❌ Not Connected'}[/dim]")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Status check failed:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def backup(
    path: str = typer.Option(None, help="Custom backup path"),
    include_config: bool = typer.Option(True, help="Include configuration in backup")
):
    """💾 Create a backup of all StudyDev data"""
    try:
        from datetime import datetime
        import shutil
        from pathlib import Path
        
        config = Config()
        db = Database()
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"studydev_backup_{timestamp}"
        
        if path:
            backup_dir = Path(path).expanduser() / backup_name
        else:
            backup_dir = Path(config.data_path) / "backups" / backup_name
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        console.print(f"\n💾 [bold blue]Creating StudyDev backup...[/bold blue]")
        console.print(f"📁 Backup location: {backup_dir}")
        
        # Backup database
        db_backup_path = str(backup_dir / "studydev.db")
        db.backup_database(db_backup_path)
        
        # Backup configuration
        if include_config:
            config_backup_path = backup_dir / "config.json"
            if Path(config.config_path).exists():
                shutil.copy2(config.config_path, config_backup_path)
                console.print("⚙️  [green]Configuration backed up[/green]")
            else:
                # Save current config to create the file, then backup
                config.save_config()
                shutil.copy2(config.config_path, config_backup_path)
                console.print("⚙️  [green]Configuration created and backed up[/green]")
        
        # Backup templates
        templates_dir = Path(config.data_path) / "templates"
        if templates_dir.exists():
            backup_templates_dir = backup_dir / "templates"
            shutil.copytree(templates_dir, backup_templates_dir)
            console.print("📋 [green]Templates backed up[/green]")
        
        # Create backup manifest
        manifest = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "includes_config": include_config,
            "database_size_mb": round(Path(db_backup_path).stat().st_size / 1024 / 1024, 2)
        }
        
        import json
        with open(backup_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        console.print(f"\n✅ [bold green]Backup completed successfully![/bold green]")
        console.print(f"📦 Backup size: ~{manifest['database_size_mb']} MB")
        console.print(f"🎯 Restore with: studydev restore --path {backup_dir}")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Backup failed:[/bold red] {e}")
        raise typer.Exit(1)

@app.command()
def restore(
    path: str = typer.Argument(..., help="Path to backup directory"),
    confirm: bool = typer.Option(False, "--yes", help="Skip confirmation prompt")
):
    """🔄 Restore StudyDev data from backup"""
    try:
        from pathlib import Path
        import shutil
        import json
        
        backup_dir = Path(path).expanduser()
        
        if not backup_dir.exists():
            console.print(f"❌ [red]Backup directory not found: {path}[/red]")
            raise typer.Exit(1)
        
        # Check manifest
        manifest_file = backup_dir / "manifest.json"
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            console.print(f"\n📋 [bold]Backup Information:[/bold]")
            console.print(f"📅 Created: {manifest.get('created_at', 'Unknown')}")
            console.print(f"📦 Size: ~{manifest.get('database_size_mb', 0)} MB")
        
        if not confirm:
            import typer
            if not typer.confirm("\n⚠️  This will replace all current StudyDev data. Continue?"):
                console.print("❌ [yellow]Restore cancelled[/yellow]")
                raise typer.Exit(0)
        
        config = Config()
        db = Database()
        
        console.print(f"\n🔄 [bold blue]Restoring StudyDev data...[/bold blue]")
        
        # Restore database
        db_backup = backup_dir / "studydev.db"
        if db_backup.exists():
            db.restore_database(str(db_backup))
        else:
            console.print("⚠️  [yellow]No database backup found[/yellow]")
        
        # Restore configuration
        config_backup = backup_dir / "config.json"
        if config_backup.exists():
            shutil.copy2(config_backup, config.config_path)
            console.print("⚙️  [green]Configuration restored[/green]")
        
        # Restore templates
        templates_backup = backup_dir / "templates"
        if templates_backup.exists():
            templates_dir = Path(config.data_path) / "templates"
            if templates_dir.exists():
                shutil.rmtree(templates_dir)
            shutil.copytree(templates_backup, templates_dir)
            console.print("📋 [green]Templates restored[/green]")
        
        console.print(f"\n✅ [bold green]Restore completed successfully![/bold green]")
        console.print("🎯 StudyDev is ready to use with restored data")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Restore failed:[/bold red] {e}")
        raise typer.Exit(1)

@app.command()
def config(
    action: str = typer.Argument(..., help="Action (show/set/reset)"),
    key: str = typer.Option(None, help="Configuration key (dot notation)"),
    value: str = typer.Option(None, help="Configuration value")
):
    """⚙️  Manage StudyDev configuration"""
    try:
        config_manager = Config()
        
        if action == "show":
            if key:
                # Show specific key
                val = config_manager.get(key)
                console.print(f"\n⚙️  [bold]{key}:[/bold] {val}")
            else:
                # Show all configuration
                console.print(f"\n⚙️  [bold]StudyDev Configuration[/bold]")
                config_manager.display_config()
        
        elif action == "set":
            if not key or value is None:
                console.print("❌ [red]Both key and value required for set action[/red]")
                raise typer.Exit(1)
            
            # Parse value (try to convert to appropriate type)
            parsed_value = value
            if value.lower() in ['true', 'false']:
                parsed_value = value.lower() == 'true'
            elif value.isdigit():
                parsed_value = int(value)
            elif value.replace('.', '').isdigit():
                parsed_value = float(value)
            
            config_manager.set(key, parsed_value)
            console.print(f"✅ [green]Configuration updated: {key} = {parsed_value}[/green]")
        
        elif action == "reset":
            if typer.confirm("⚠️  Reset all configuration to defaults?"):
                config_manager.reset_to_defaults()
                console.print("✅ [green]Configuration reset to defaults[/green]")
            else:
                console.print("❌ [yellow]Reset cancelled[/yellow]")
        
        else:
            console.print(f"❌ [red]Unknown action: {action}. Use show/set/reset[/red]")
    
    except Exception as e:
        console.print(f"\n❌ [bold red]Configuration error:[/bold red] {e}")
        raise typer.Exit(1)

@app.command()
def export(
    format_type: str = typer.Option("json", help="Export format (json/csv)"),
    output: str = typer.Option(None, help="Output file path"),
    data_type: str = typer.Option("all", help="Data to export (all/sessions/projects/bookmarks/flashcards/courses)")
):
    """📤 Export StudyDev data to external formats"""
    try:
        from datetime import datetime
        from pathlib import Path
        import json
        import csv
        
        db = Database()
        
        # Generate default filename
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"studydev_export_{timestamp}.{format_type}"
        
        console.print(f"\n📤 [bold blue]Exporting StudyDev data...[/bold blue]")
        console.print(f"📋 Type: {data_type}")
        console.print(f"📄 Format: {format_type.upper()}")
        console.print(f"📁 Output: {output}")
        
        # Get data based on type
        export_data = {}
        
        if data_type in ["all", "sessions"]:
            sessions = db.execute_query("""
                SELECT s.*, p.name as project_name 
                FROM sessions s 
                LEFT JOIN projects p ON s.project_id = p.id 
                ORDER BY s.start_time DESC
            """)
            export_data["sessions"] = [dict(session) for session in sessions]
        
        if data_type in ["all", "projects"]:
            projects = db.execute_query("SELECT * FROM projects ORDER BY updated_at DESC")
            export_data["projects"] = [dict(project) for project in projects]
        
        if data_type in ["all", "bookmarks"]:
            bookmarks = db.execute_query("SELECT * FROM bookmarks ORDER BY created_at DESC")
            export_data["bookmarks"] = [dict(bookmark) for bookmark in bookmarks]
        
        if data_type in ["all", "flashcards"]:
            flashcards = db.execute_query("SELECT * FROM flashcards ORDER BY created_at DESC")
            export_data["flashcards"] = [dict(flashcard) for flashcard in flashcards]
        
        if data_type in ["all", "courses"]:
            courses = db.execute_query("SELECT * FROM courses ORDER BY updated_at DESC")
            export_data["courses"] = [dict(course) for course in courses]
        
        # Export to specified format
        if format_type == "json":
            with open(output, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        
        elif format_type == "csv":
            # For CSV, export each data type to separate files or sheets
            base_name = Path(output).stem
            for data_name, data_list in export_data.items():
                if data_list:
                    csv_file = f"{base_name}_{data_name}.csv"
                    with open(csv_file, 'w', newline='') as f:
                        if data_list:
                            writer = csv.DictWriter(f, fieldnames=data_list[0].keys())
                            writer.writeheader()
                            writer.writerows(data_list)
                    console.print(f"📄 [green]Exported {data_name} to {csv_file}[/green]")
        
        console.print(f"\n✅ [bold green]Export completed successfully![/bold green]")
        
        # Show stats
        total_records = sum(len(data) for data in export_data.values())
        console.print(f"📊 Total records exported: {total_records}")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Export failed:[/bold red] {e}")
        raise typer.Exit(1)

@app.command()
def dashboard():
    """📋 Show the StudyDev productivity dashboard"""
    try:
        from studydev.utils.integration import IntegrationManager
        
        integration = IntegrationManager()
        dashboard_data = integration.generate_dashboard_data()
        
        console.print("\n🎯 [bold blue]StudyDev Productivity Dashboard[/bold blue]")
        
        # Recent stats panel
        stats = dashboard_data["recent_stats"]
        stats_text = Text()
        stats_text.append(f"📋 Study Hours (7d): {stats['study_hours']}h\n", style="blue")
        stats_text.append(f"📝 Active Projects: {stats['active_projects']}\n", style="green")
        stats_text.append(f"🎆 Productivity: {stats['productivity_level']} ({stats['productivity_score']}/5)\n", style="magenta")
        stats_text.append(f"🔥 Current Streak: {dashboard_data['current_streak']} days\n", style="yellow")
        
        stats_panel = Panel(stats_text, title="Recent Performance", border_style="blue")
        console.print(stats_panel)
        
        # Review items
        if dashboard_data["flashcards_due"] > 0:
            console.print(f"\n🎴 [yellow]{dashboard_data['flashcards_due']} flashcards due for review[/yellow]")
        
        # Upcoming deadlines
        if dashboard_data["upcoming_deadlines"]:
            console.print(f"\n⏰ [bold red]Upcoming Deadlines[/bold red]")
            for deadline in dashboard_data["upcoming_deadlines"]:
                days_left = deadline['days_left']
                if days_left < 0:
                    color = "red"
                    status = f"{abs(days_left)} days overdue"
                elif days_left <= 3:
                    color = "yellow"
                    status = f"{days_left} days left"
                else:
                    color = "green"
                    status = f"{days_left} days left"
                
                console.print(f"  • [{color}]{deadline['name']}: {status}[/{color}]")
        
        # Recent sessions
        if dashboard_data["recent_sessions"]:
            console.print(f"\n📋 [bold]Recent Sessions[/bold]")
            
            sessions_table = Table()
            sessions_table.add_column("Date", style="dim")
            sessions_table.add_column("Type", style="cyan")
            sessions_table.add_column("Subject/Project", style="blue")
            sessions_table.add_column("Duration", justify="right")
            
            for session in dashboard_data["recent_sessions"]:
                subject_or_project = session["subject"] or session["project"] or "N/A"
                
                sessions_table.add_row(
                    session["date"],
                    session["type"].title(),
                    subject_or_project,
                    f"{session['duration_minutes']}m"
                )
            
            console.print(sessions_table)
        
        # Quick actions
        console.print(f"\n🚀 [bold]Quick Actions:[/bold]")
        if dashboard_data["flashcards_due"] > 0:
            console.print("  • [cyan]studydev study flashcard review[/cyan] - Review flashcards")
        console.print("  • [cyan]studydev session start[/cyan] - Start a study session")
        console.print("  • [cyan]studydev study review[/cyan] - Review study materials")
        console.print("  • [cyan]studydev report[/cyan] - Generate productivity report")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Dashboard error:[/bold red] {e}")
        raise typer.Exit(1)

@app.command()
def report(
    days: int = typer.Option(30, help="Number of days to include in report"),
    output: str = typer.Option(None, help="Save report to file (JSON format)")
):
    """📈 Generate comprehensive productivity report"""
    try:
        from studydev.utils.integration import IntegrationManager
        import json
        
        integration = IntegrationManager()
        report_data = integration.generate_productivity_report(days)
        
        console.print(f"\n📈 [bold blue]StudyDev Productivity Report ({days} days)[/bold blue]")
        console.print(f"📅 Period: {report_data['period']['start_date']} to {report_data['period']['end_date']}")
        
        # Overall productivity score
        productivity = report_data["integration"]["overall_productivity"]
        console.print(f"\n🎆 [bold]Overall Productivity: {productivity['level']} ({productivity['score']}/5)[/bold]")
        
        # Sessions summary
        sessions = report_data["sessions"]
        console.print(f"\n🎯 [bold]Study Sessions[/bold]")
        console.print(f"  • Total Sessions: {sessions['total_sessions']}")
        console.print(f"  • Total Time: {sessions['total_time_hours']} hours")
        console.print(f"  • Average Duration: {sessions['average_duration_minutes']} minutes")
        console.print(f"  • Average Rating: {sessions['average_rating']}/5")
        
        # Top subjects
        if sessions["subject_breakdown"]:
            console.print(f"\n📚 [bold]Top Study Subjects[/bold]")
            subjects = sorted(sessions["subject_breakdown"].items(), 
                            key=lambda x: x[1]["duration_hours"], reverse=True)[:5]
            
            for subject, data in subjects:
                console.print(f"  • {subject}: {data['duration_hours']}h ({data['sessions']} sessions)")
        
        # Projects summary
        projects = report_data["projects"]
        console.print(f"\n📝 [bold]Projects[/bold]")
        console.print(f"  • Active Projects: {projects['active_projects']}")
        console.print(f"  • Completed Projects: {projects['completed_projects']}")
        console.print(f"  • Overdue Projects: {projects['overdue_projects']}")
        
        # Study materials summary
        study = report_data["study"]
        console.print(f"\n📚 [bold]Study Materials[/bold]")
        console.print(f"  • Flashcards: {study['flashcards']['total_flashcards']} (Mastery: {study['flashcards']['mastery_rate']:.1f}%)")
        console.print(f"  • Bookmarks: {study['bookmarks']['total_bookmarks']} (Read: {study['bookmarks']['read_bookmarks']})")
        console.print(f"  • Courses: {study['courses']['total_courses']} (Avg Progress: {study['courses']['average_progress']:.1f}%)")
        
        # Integration insights
        integration_data = report_data["integration"]
        if integration_data["subject_overlap"]:
            console.print(f"\n🔗 [bold]Integration Insights[/bold]")
            console.print(f"  • Subject Overlap: {', '.join(integration_data['subject_overlap'])}")
            
            # Most effective subjects
            effectiveness = integration_data["subject_effectiveness"]
            if effectiveness:
                top_effective = sorted(effectiveness.items(), 
                                     key=lambda x: x[1]["effectiveness"], reverse=True)[:3]
                
                console.print(f"\n🎯 [bold]Most Effective Study Subjects[/bold]")
                for subject, data in top_effective:
                    console.print(f"  • {subject}: {data['effectiveness']} mastery/hour ({data['study_time_hours']}h study)")
        
        # Save to file if requested
        if output:
            with open(output, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            console.print(f"\n💾 [green]Report saved to: {output}[/green]")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Report generation failed:[/bold red] {e}")
        raise typer.Exit(1)

@app.command()
def version():
    """ℹ️  Show StudyDev version"""
    console.print("\n🎯 [bold blue]StudyDev[/bold blue] v1.0.0")
    console.print("Ultimate Student & Developer Productivity CLI Tool")
    console.print("Made with ❤️  by PrinceTheProgrammer\n")


def show_quick_start_guide():
    """Display an interactive quick start guide"""
    commands_help = {
        "Session Management 📚": {
            "session start": "Start a Pomodoro study session with timer",
            "session pause": "Pause current session",
            "session stop": "Stop and rate current session",
            "session stats": "View session statistics and streaks",
            "session history": "Show detailed session history"
        },
        "Project Organization 📋": {
            "project create <name>": "Create new project from template",
            "project list": "List all projects with progress",
            "project template list": "Show available project templates",
            "project update <id>": "Update project status or deadline"
        },
        "Study Materials 📖": {
            "study bookmark add <url>": "Add bookmark with automatic metadata",
            "study flashcard add": "Create new flashcard for study",
            "study flashcard review": "Review due flashcards with spaced repetition",
            "study course add <name>": "Track progress in online courses",
            "study review": "Show summary of due materials"
        },
        "Dashboard & Reports 📈": {
            "status": "Beautiful productivity dashboard",
            "dashboard": "Show current productivity metrics",
            "report": "Generate comprehensive productivity report"
        },
        "Data Management 💾": {
            "backup": "Create backup of all StudyDev data",
            "restore <path>": "Restore from backup",
            "export": "Export data to JSON/CSV formats",
            "config show": "Display current configuration"
        }
    }
    
    interactive_ui.create_help_display(commands_help)
    
    # Interactive menu for first steps
    first_steps = [
        {
            "label": "Start a Study Session",
            "value": "session_start",
            "icon": "🎯",
            "description": "Begin your first Pomodoro session"
        },
        {
            "label": "Create a Project",
            "value": "project_create",
            "icon": "📁",
            "description": "Set up a new academic or development project"
        },
        {
            "label": "Add Study Material",
            "value": "bookmark_add",
            "icon": "🔖",
            "description": "Save your first bookmark or flashcard"
        },
        {
            "label": "View Dashboard",
            "value": "dashboard",
            "icon": "📈",
            "description": "See your productivity overview"
        },
        {
            "label": "I'll explore myself",
            "value": "exit",
            "icon": "🚀",
            "description": "Ready to dive in independently"
        }
    ]
    
    choice = interactive_ui.create_interactive_menu(
        "🎆 What would you like to do first?",
        first_steps,
        "green"
    )
    
    if choice == "session_start":
        console.print("\n🚀 [green]Great choice! Run:[/green] [cyan]studydev session start[/cyan]")
    elif choice == "project_create":
        console.print("\n🚀 [green]Excellent! Run:[/green] [cyan]studydev project create MyProject[/cyan]")
    elif choice == "bookmark_add":
        console.print("\n🚀 [green]Perfect! Run:[/green] [cyan]studydev study bookmark add <url>[/cyan]")
    elif choice == "dashboard":
        console.print("\n🚀 [green]Nice! Run:[/green] [cyan]studydev status[/cyan]")
    else:
        console.print("\n🚀 [green]Have fun exploring! Use[/green] [cyan]studydev --help[/cyan] [green]anytime.[/green]")

@app.command()
def quickstart():
    """🎆 Interactive quick start guide for new users"""
    show_quick_start_guide()

@app.command() 
def help():
    """📚 Show comprehensive help with beautiful formatting"""
    commands_help = {
        "Session Management 📚": {
            "session start [--subject TEXT] [--project-id INT]": "Start focused Pomodoro study session",
            "session pause": "Pause current active session",
            "session resume": "Resume paused session", 
            "session stop [--rating INT]": "Stop session and provide rating",
            "session stats [--days INT]": "Show session statistics and analytics",
            "session history [--limit INT]": "Display detailed session history"
        },
        "Project Organization 📋": {
            "project create <name> [--template TEXT] [--description TEXT]": "Create new project from template",
            "project list [--status TEXT] [--sort TEXT]": "List projects with filtering/sorting",
            "project show <id>": "Show detailed project information",
            "project update <id> [--status] [--deadline]": "Update project details",
            "project template list": "Show available project templates",
            "project template create <name>": "Create custom project template"
        },
        "Study Materials 📖": {
            "study bookmark add <url> [--title] [--tags] [--subject]": "Add bookmark with metadata",
            "study bookmark list [--subject] [--unread]": "List bookmarks with filters",
            "study flashcard add [--subject]": "Create new flashcard interactively",
            "study flashcard review [--subject] [--limit]": "Review flashcards with spaced repetition",
            "study course add <name> [--url] [--total-lessons]": "Track online course progress",
            "study review [--subject] [--limit]": "Show comprehensive study review"
        },
        "Analytics & Reports 📈": {
            "status": "Beautiful productivity dashboard with metrics",
            "dashboard": "Real-time productivity overview", 
            "report [--days INT] [--output FILE]": "Generate detailed productivity report"
        },
        "Data Management 💾": {
            "init": "Initialize StudyDev with welcome guide",
            "backup [--path TEXT] [--include-config]": "Create comprehensive backup",
            "restore <path> [--yes]": "Restore from backup directory",
            "export [--format] [--data-type] [--output]": "Export data in JSON/CSV formats",
            "config show|set|reset [--key] [--value]": "Manage configuration settings"
        }
    }
    
    interactive_ui.create_help_display(commands_help)
    
    console.print(f"\n🎆 [bold green]Pro Tips:[/bold green]")
    console.print("• Start with [cyan]studydev init[/cyan] for first-time setup")
    console.print("• Use [cyan]studydev status[/cyan] for beautiful productivity dashboard")
    console.print("• Try [cyan]studydev session start[/cyan] for your first Pomodoro session")
    console.print("• All commands support [cyan]--help[/cyan] flag for detailed options")

def main():
    """Main entry point for the CLI application"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n\n👋 [yellow]Goodbye! Keep being productive![/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        console.print(f"\n❌ [bold red]An error occurred:[/bold red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    main()