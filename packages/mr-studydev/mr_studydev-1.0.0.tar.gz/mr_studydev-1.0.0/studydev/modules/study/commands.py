"""
StudyDev Study Materials Management Commands
Handles bookmarks, flashcards, course tracking, and study resources
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm

from studydev.modules.study.manager import StudyMaterialsManager

console = Console()

# Create the study sub-application
study_app = typer.Typer(
    help="🔖 Study Material Aggregator - Manage bookmarks, flashcards, and course progress",
    rich_markup_mode="rich"
)

@study_app.command("bookmark")
def manage_bookmarks(
    action: str = typer.Argument(..., help="Action (add/list/search/remove/read)"),
    url: str = typer.Option(None, help="URL to bookmark"),
    title: str = typer.Option(None, help="Bookmark title"),
    category: str = typer.Option("General", help="Bookmark category"),
    tags: str = typer.Option(None, help="Comma-separated tags"),
    description: str = typer.Option(None, help="Bookmark description"),
    bookmark_id: int = typer.Option(None, help="Bookmark ID for remove/read actions"),
    unread_only: bool = typer.Option(False, help="Show only unread bookmarks (for list)")
):
    """🔖 Manage study resource bookmarks"""
    manager = StudyMaterialsManager()
    
    if action == "add":
        if not url or not title:
            console.print("❌ [red]URL and title are required for adding bookmarks[/red]")
            return
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        result = manager.add_bookmark(
            url=url,
            title=title,
            category=category,
            description=description,
            tags=tag_list
        )
        
        if result["success"]:
            console.print(f"\n✅ [green]{result['message']}[/green]")
            console.print(f"🆔 Bookmark ID: {result['bookmark_id']}")
        else:
            console.print(f"\n❌ [red]{result['message']}[/red]")
    
    elif action == "list":
        # Parse filtering options
        category_filter = None if category == "General" else category
        tag_filter = [tag.strip() for tag in tags.split(",")] if tags else None
        is_read_filter = None if not unread_only else False
        
        bookmarks = manager.list_bookmarks(
            category=category_filter,
            tags=tag_filter,
            is_read=is_read_filter
        )
        
        if not bookmarks:
            console.print("\n🔖 [yellow]No bookmarks found matching criteria.[/yellow]")
            return
        
        console.print(f"\n🔖 [bold]Bookmarks ({len(bookmarks)} found)[/bold]")
        
        # Create bookmarks table
        bookmarks_table = Table()
        bookmarks_table.add_column("ID", style="dim", width=4)
        bookmarks_table.add_column("Title", style="bold blue")
        bookmarks_table.add_column("Category", style="magenta")
        bookmarks_table.add_column("Tags", style="cyan")
        bookmarks_table.add_column("Status", justify="center")
        bookmarks_table.add_column("Rating", justify="center")
        bookmarks_table.add_column("URL", style="green")
        
        for bookmark in bookmarks:
            # Status icon
            status_icon = "✅" if bookmark["is_read"] else "🔴"
            status_text = "Read" if bookmark["is_read"] else "Unread"
            
            # Rating stars
            rating_stars = "⭐" * (bookmark["rating"] or 0) if bookmark["rating"] else "N/A"
            
            # Tags display
            tags_display = ", ".join(bookmark["tags"]) if bookmark["tags"] else "N/A"
            
            # Truncate URL for display
            url_display = bookmark["url"][:50] + "..." if len(bookmark["url"]) > 50 else bookmark["url"]
            
            bookmarks_table.add_row(
                str(bookmark["id"]),
                bookmark["title"],
                bookmark["category"],
                tags_display,
                f"{status_icon} {status_text}",
                rating_stars,
                url_display
            )
        
        console.print(bookmarks_table)
        
        # Show categories summary
        categories = manager.get_bookmark_categories()
        if categories:
            console.print(f"\n📁 [bold]Categories:[/bold] {', '.join(categories)}")
    
    elif action == "search":
        if not title:  # Using title as search term
            console.print("❌ [red]Search term required (use --title option)[/red]")
            return
        
        bookmarks = manager.list_bookmarks(search=title)
        
        if not bookmarks:
            console.print(f"\n🔍 [yellow]No bookmarks found matching '{title}'[/yellow]")
            return
        
        console.print(f"\n🔍 [bold]Search Results for '{title}' ({len(bookmarks)} found)[/bold]")
        
        for bookmark in bookmarks:
            console.print(f"\n• [bold blue]{bookmark['title']}[/bold blue]")
            console.print(f"  🌐 {bookmark['url']}")
            console.print(f"  📁 {bookmark['category']} | ID: {bookmark['id']}")
            if bookmark["description"]:
                console.print(f"  📝 {bookmark['description']}")
    
    elif action == "read":
        if not bookmark_id:
            console.print("❌ [red]Bookmark ID required for read action[/red]")
            return
        
        success = manager.access_bookmark(bookmark_id)
        if success:
            console.print(f"\n✅ [green]Bookmark {bookmark_id} marked as read[/green]")
        else:
            console.print(f"\n❌ [red]Failed to update bookmark {bookmark_id}[/red]")
    
    elif action == "remove":
        if not bookmark_id:
            console.print("❌ [red]Bookmark ID required for remove action[/red]")
            return
        
        if Confirm.ask(f"Really delete bookmark {bookmark_id}?"):
            success = manager.delete_bookmark(bookmark_id)
            if success:
                console.print(f"\n✅ [green]Bookmark {bookmark_id} deleted[/green]")
            else:
                console.print(f"\n❌ [red]Failed to delete bookmark {bookmark_id}[/red]")
    
    else:
        console.print(f"❌ [red]Unknown action: {action}. Use add/list/search/read/remove[/red]")

@study_app.command("flashcard")
def manage_flashcards(
    action: str = typer.Argument(..., help="Action (add/review/list/stats)"),
    subject: str = typer.Option(None, help="Subject for flashcards"),
    question: str = typer.Option(None, help="Question text"),
    answer: str = typer.Option(None, help="Answer text"),
    difficulty: int = typer.Option(3, help="Difficulty level (1-5)"),
    tags: str = typer.Option(None, help="Comma-separated tags"),
    limit: int = typer.Option(10, help="Limit for review session")
):
    """🎴 Manage flashcards with spaced repetition system"""
    manager = StudyMaterialsManager()
    
    if action == "add":
        if not all([subject, question, answer]):
            console.print("❌ [red]Subject, question, and answer are required[/red]")
            return
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        result = manager.add_flashcard(
            question=question,
            answer=answer,
            subject=subject,
            difficulty=difficulty,
            tags=tag_list
        )
        
        if result["success"]:
            console.print(f"\n✅ [green]{result['message']}[/green]")
            console.print(f"🆔 Flashcard ID: {result['flashcard_id']}")
            console.print(f"📅 Next review: Tomorrow")
        else:
            console.print(f"\n❌ [red]{result['message']}[/red]")
    
    elif action == "review":
        cards = manager.get_flashcards_for_review(subject=subject, limit=limit)
        
        if not cards:
            console.print(f"\n🎴 [green]No flashcards due for review{f' in {subject}' if subject else ''}![/green]")
            console.print("🎆 You're all caught up! Great job!")
            return
        
        console.print(f"\n🎴 [bold]Flashcard Review Session[/bold]")
        console.print(f"📅 {len(cards)} cards due for review{f' in {subject}' if subject else ''}")
        
        correct_count = 0
        total_cards = len(cards)
        
        for i, card in enumerate(cards, 1):
            console.print(f"\n📇 [bold]Card {i}/{total_cards}[/bold] - {card['subject']}")
            
            # Show question
            question_panel = Panel(
                Text(card['question'], style="bold blue"),
                title="Question",
                border_style="blue"
            )
            console.print(question_panel)
            
            # Wait for user to think
            Prompt.ask("[dim]Press Enter when ready to see the answer[/dim]", default="")
            
            # Show answer
            answer_panel = Panel(
                Text(card['answer'], style="bold green"),
                title="Answer",
                border_style="green"
            )
            console.print(answer_panel)
            
            # Get user feedback
            correct = Confirm.ask("Did you get it right?")
            
            if correct:
                correct_count += 1
                console.print("✅ [green]Correct![/green]")
            else:
                console.print("❌ [red]Don't worry, you'll get it next time![/red]")
            
            # Update flashcard
            review_result = manager.review_flashcard(card['id'], correct)
            
            if review_result["success"]:
                next_days = review_result["next_review_days"]
                streak = review_result["correct_streak"]
                
                if correct:
                    console.print(f"📅 Next review: {next_days} day(s) | Streak: {streak}")
                else:
                    console.print("📅 Next review: Tomorrow (incorrect answer)")
        
        # Session summary
        accuracy = (correct_count / total_cards) * 100
        console.print(f"\n🎆 [bold]Review Session Complete![/bold]")
        console.print(f"🎯 Score: {correct_count}/{total_cards} ({accuracy:.1f}%)")
        
        if accuracy >= 80:
            console.print("🎉 [green]Excellent work! You're mastering these concepts![/green]")
        elif accuracy >= 60:
            console.print("💪 [yellow]Good job! Keep reviewing to improve![/yellow]")
        else:
            console.print("📝 [blue]Don't give up! Regular review is key to learning![/blue]")
    
    elif action == "list":
        # Get all subjects if none specified
        subjects = [subject] if subject else manager.get_flashcard_subjects()
        
        if not subjects:
            console.print("\n🎴 [yellow]No flashcards found. Add some with: studydev study flashcard add[/yellow]")
            return
        
        console.print(f"\n🎴 [bold]Flashcard Summary[/bold]")
        
        # Create subjects table
        subjects_table = Table()
        subjects_table.add_column("Subject", style="cyan")
        subjects_table.add_column("Total Cards", justify="right")
        subjects_table.add_column("Due for Review", justify="right")
        subjects_table.add_column("Mastery Rate", justify="right")
        
        for subj in subjects:
            stats = manager.get_flashcard_stats(subj)
            
            subjects_table.add_row(
                subj,
                str(stats['total_cards']),
                str(stats['due_for_review']),
                f"{stats['mastery_rate']:.1f}%"
            )
        
        console.print(subjects_table)
    
    elif action == "stats":
        if subject:
            stats = manager.get_flashcard_stats(subject)
            console.print(f"\n🎴 [bold]Flashcard Stats - {subject}[/bold]")
        else:
            stats = manager.get_flashcard_stats()
            console.print(f"\n🎴 [bold]Overall Flashcard Stats[/bold]")
        
        stats_text = Text()
        stats_text.append(f"📊 Total Cards: {stats['total_cards']}\n", style="blue")
        stats_text.append(f"📅 Due for Review: {stats['due_for_review']}\n", style="yellow")
        stats_text.append(f"🎯 Average Streak: {stats['average_streak']}\n", style="green")
        stats_text.append(f"🎆 Mastery Rate: {stats['mastery_rate']:.1f}%\n", style="magenta")
        
        stats_panel = Panel(stats_text, title="Statistics", border_style="blue")
        console.print(stats_panel)
        
        if stats['due_for_review'] > 0:
            console.print(f"\n⏰ [cyan]Ready for review! Run: studydev study flashcard review{f' --subject {subject}' if subject else ''}[/cyan]")
    
    else:
        console.print(f"❌ [red]Unknown action: {action}. Use add/review/list/stats[/red]")

@study_app.command("course")
def manage_courses(
    action: str = typer.Argument(..., help="Action (add/list/update/stats)"),
    title: str = typer.Option(None, help="Course title"),
    platform: str = typer.Option(None, help="Learning platform"),
    instructor: str = typer.Option(None, help="Course instructor"),
    url: str = typer.Option(None, help="Course URL"),
    total_lessons: int = typer.Option(None, help="Total number of lessons"),
    completed_lessons: int = typer.Option(None, help="Number of completed lessons"),
    course_id: int = typer.Option(None, help="Course ID for update actions"),
    target_date: str = typer.Option(None, help="Target completion date (YYYY-MM-DD)")
):
    """🎓 Track online course progress"""
    manager = StudyMaterialsManager()
    
    if action == "add":
        if not title:
            console.print("❌ [red]Course title is required[/red]")
            return
        
        result = manager.add_course(
            title=title,
            platform=platform,
            instructor=instructor,
            url=url,
            total_lessons=total_lessons,
            target_completion_date=target_date
        )
        
        if result["success"]:
            console.print(f"\n✅ [green]{result['message']}[/green]")
            console.print(f"🆔 Course ID: {result['course_id']}")
        else:
            console.print(f"\n❌ [red]{result['message']}[/red]")
    
    elif action == "list":
        courses = manager.list_courses()
        
        if not courses:
            console.print("\n🎓 [yellow]No courses found. Add some with: studydev study course add[/yellow]")
            return
        
        console.print(f"\n🎓 [bold]Course Progress ({len(courses)} courses)[/bold]")
        
        # Create courses table
        courses_table = Table()
        courses_table.add_column("ID", style="dim", width=4)
        courses_table.add_column("Title", style="bold blue")
        courses_table.add_column("Platform", style="magenta")
        courses_table.add_column("Progress", justify="center")
        courses_table.add_column("Status", justify="center")
        courses_table.add_column("Lessons", justify="center")
        
        for course in courses:
            # Progress bar
            progress_pct = course["progress_percentage"]
            if progress_pct >= 100:
                progress_display = "[green]✅ 100%[/green]"
            elif progress_pct >= 50:
                progress_display = f"[yellow]🔄 {progress_pct:.1f}%[/yellow]"
            else:
                progress_display = f"[red]📚 {progress_pct:.1f}%[/red]"
            
            # Status icons
            status_icons = {
                "enrolled": "📝",
                "in_progress": "📚", 
                "completed": "✅",
                "paused": "⏸️"
            }
            status_display = f"{status_icons.get(course['status'], course['status'])} {course['status'].title()}"
            
            # Lessons display
            if course["total_lessons"]:
                lessons_display = f"{course['completed_lessons']}/{course['total_lessons']}"
            else:
                lessons_display = f"{course['completed_lessons']} done"
            
            courses_table.add_row(
                str(course["id"]),
                course["title"],
                course["platform"] or "N/A",
                progress_display,
                status_display,
                lessons_display
            )
        
        console.print(courses_table)
    
    elif action == "update":
        if not course_id or completed_lessons is None:
            console.print("❌ [red]Course ID and completed lessons count required[/red]")
            return
        
        result = manager.update_course_progress(course_id, completed_lessons)
        
        if result["success"]:
            console.print(f"\n✅ [green]{result['message']}[/green]")
            console.print(f"🎯 Status: {result['status'].title()}")
            
            if result["status"] == "completed":
                console.print("🎉 [green]Congratulations! Course completed![/green]")
        else:
            console.print(f"\n❌ [red]{result['message']}[/red]")
    
    elif action == "stats":
        stats = manager.get_course_stats()
        
        console.print(f"\n🎓 [bold]Course Statistics[/bold]")
        
        stats_text = Text()
        stats_text.append(f"📚 Total Courses: {stats['total_courses']}\n", style="blue")
        stats_text.append(f"✅ Completed: {stats['completed_courses']}\n", style="green")
        stats_text.append(f"📝 In Progress: {stats['in_progress_courses']}\n", style="yellow")
        stats_text.append(f"📈 Average Progress: {stats['average_progress']:.1f}%\n", style="cyan")
        stats_text.append(f"🎆 Completion Rate: {stats['completion_rate']:.1f}%\n", style="magenta")
        
        stats_panel = Panel(stats_text, title="Course Statistics", border_style="blue")
        console.print(stats_panel)
        
        if stats['in_progress_courses'] > 0:
            console.print(f"\n💪 [cyan]Keep going! You have {stats['in_progress_courses']} courses in progress.[/cyan]")
    
    else:
        console.print(f"❌ [red]Unknown action: {action}. Use add/list/update/stats[/red]")

@study_app.command("review")
def review_materials(
    material_type: str = typer.Option("all", help="Type to review (flashcards/bookmarks/all)"),
    subject: str = typer.Option(None, help="Filter by subject"),
    limit: int = typer.Option(10, help="Maximum items to show")
):
    """📜 Review study materials (flashcards, bookmarks, etc.)"""
    manager = StudyMaterialsManager()
    
    # Get review summary
    summary = manager.get_review_summary()
    
    console.print(f"\n📜 [bold]Study Review Dashboard[/bold]")
    
    # Show overall summary
    summary_text = Text()
    summary_text.append(f"🎴 Flashcards due: {summary['flashcards_due']}\n", style="blue")
    summary_text.append(f"🔖 Unread bookmarks: {summary['unread_bookmarks']}\n", style="yellow")
    summary_text.append(f"🎓 Active courses: {summary['active_courses']}\n", style="green")
    summary_text.append(f"🎯 Total items to review: {summary['total_review_items']}\n", style="magenta")
    
    summary_panel = Panel(summary_text, title="Review Summary", border_style="blue")
    console.print(summary_panel)
    
    # Show specific review items based on type
    if material_type in ["flashcards", "all"]:
        if summary['flashcards_due'] > 0:
            console.print(f"\n🎴 [bold]Flashcards Due for Review[/bold]")
            
            cards = manager.get_flashcards_for_review(subject=subject, limit=limit)
            
            if cards:
                cards_table = Table()
                cards_table.add_column("Subject", style="cyan")
                cards_table.add_column("Question Preview", style="blue")
                cards_table.add_column("Difficulty", justify="center")
                cards_table.add_column("Streak", justify="center")
                
                for card in cards:
                    # Truncate question for preview
                    question_preview = card['question'][:50] + "..." if len(card['question']) > 50 else card['question']
                    difficulty_stars = "⭐" * card['difficulty']
                    streak_display = f"{card['correct_streak'] or 0}🔥"
                    
                    cards_table.add_row(
                        card['subject'],
                        question_preview,
                        difficulty_stars,
                        streak_display
                    )
                
                console.print(cards_table)
                console.print(f"\n⏰ [cyan]Start review: studydev study flashcard review{f' --subject {subject}' if subject else ''}[/cyan]")
        else:
            console.print(f"\n🎴 [green]No flashcards due for review! Great job staying current![/green]")
    
    if material_type in ["bookmarks", "all"]:
        if summary['unread_bookmarks'] > 0:
            console.print(f"\n🔖 [bold]Unread Bookmarks[/bold]")
            
            unread_bookmarks = manager.list_bookmarks(is_read=False)
            
            if unread_bookmarks:
                bookmarks_table = Table()
                bookmarks_table.add_column("Title", style="blue")
                bookmarks_table.add_column("Category", style="magenta")
                bookmarks_table.add_column("Added", style="dim")
                
                for bookmark in unread_bookmarks[:limit]:
                    # Format date
                    from datetime import datetime
                    created_date = datetime.fromisoformat(bookmark['created_at']).strftime("%m-%d")
                    
                    bookmarks_table.add_row(
                        bookmark['title'][:40] + "..." if len(bookmark['title']) > 40 else bookmark['title'],
                        bookmark['category'],
                        created_date
                    )
                
                console.print(bookmarks_table)
                console.print(f"\n📚 [cyan]View bookmarks: studydev study bookmark list --unread-only[/cyan]")
        else:
            console.print(f"\n🔖 [green]No unread bookmarks! You're up to date![/green]")
    
    # Show actionable next steps
    if summary['total_review_items'] > 0:
        console.print(f"\n🚀 [bold]Suggested Actions:[/bold]")
        
        if summary['flashcards_due'] > 0:
            console.print(f"  • Review {min(summary['flashcards_due'], 10)} flashcards (10-15 min)")
        
        if summary['unread_bookmarks'] > 0:
            console.print(f"  • Read {min(summary['unread_bookmarks'], 3)} bookmarks (15-20 min)")
        
        if summary['active_courses'] > 0:
            console.print(f"  • Continue progress on {summary['active_courses']} active courses")
    
    else:
        console.print(f"\n🎉 [green]All caught up! Consider adding new study materials or starting a learning session.[/green]")
