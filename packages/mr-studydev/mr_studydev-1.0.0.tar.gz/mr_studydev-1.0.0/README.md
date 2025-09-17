# 🎯 StudyDev - Ultimate Student & Developer Productivity CLI Tool

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CLI](https://img.shields.io/badge/interface-CLI-brightgreen.svg)](https://github.com/yourusername/studydev)

> *Supercharge your productivity with the most comprehensive study and development CLI tool ever created!*

**StudyDev** combines the power of Pomodoro sessions, project organization, and intelligent study material management into one beautiful, feature-rich command-line interface. Built with love for students, developers, and lifelong learners who want to optimize their productivity workflow.

## ✨ Features

### 🍅 **Advanced Pomodoro Session Manager**
- **Interactive Timer**: Beautiful real-time progress display with motivational messages
- **Smart Pause/Resume**: Full session control with keyboard interrupt handling
- **Productivity Ratings**: Rate and track your session effectiveness (1-5 scale)
- **Achievement System**: Unlock achievements for consistency and milestones
- **Session Analytics**: Detailed statistics, streaks, and productivity insights
- **Subject Tracking**: Link sessions to specific subjects or projects

### 📋 **Intelligent Project Organizer** 
- **Template System**: Pre-built templates for Python, JavaScript, Research, Thesis, etc.
- **Git Integration**: Automatic repository initialization and .gitignore setup
- **Deadline Management**: Visual urgency indicators and overdue tracking
- **Progress Tracking**: Monitor project completion and milestones
- **Custom Templates**: Create and share your own project templates
- **Smart Filtering**: Sort and filter projects by status, deadline, or type

### 📚 **Smart Study Material Aggregator**
- **Bookmark Management**: Auto-fetch metadata, tags, and subject classification
- **Spaced Repetition Flashcards**: SRS algorithm for optimal memory retention
- **Course Progress Tracking**: Monitor online course completion and learning goals
- **Subject Organization**: Intelligent categorization across all study materials
- **Review Dashboard**: Unified view of due flashcards, unread bookmarks, and active courses
- **Search & Filter**: Powerful filtering by subject, tags, and completion status

### 📊 **Beautiful Analytics & Reports**
- **Productivity Dashboard**: Real-time overview with stunning visual metrics
- **Progress Visualization**: Beautiful gauges, charts, and progress indicators
- **Comprehensive Reports**: Detailed analytics with customizable date ranges
- **Streak Tracking**: Monitor and celebrate study consistency
- **Cross-Module Insights**: Discover patterns between sessions, projects, and materials
- **Export Options**: Generate reports in JSON/CSV for external analysis

### 🎨 **Stunning Interactive UI**
- **Animated Welcome**: Eye-catching ASCII art and smooth animations
- **Rich Terminal Output**: Colors, borders, progress bars, and beautiful tables
- **Interactive Menus**: Guided workflows with intuitive navigation
- **Loading Animations**: Smooth spinners and progress indicators
- **Achievement Celebrations**: Animated unlock notifications for milestones
- **Contextual Help**: Beautiful command reference with examples

### 💾 **Enterprise-Grade Data Management**
- **Automatic Backups**: Comprehensive backup/restore system
- **Data Export**: Multiple formats (JSON, CSV) for data portability
- **Configuration Management**: Flexible settings with easy management
- **SQLite Database**: Reliable local storage with data integrity
- **Multi-Platform**: Works on Linux, macOS, and Windows

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/studydev.git
cd studydev

# Create virtual environment
python -m venv studydevenv
source studydevenv/bin/activate  # On Windows: studydevenv\Scripts\activate

# Install dependencies
pip install -e .

# Initialize StudyDev (with beautiful welcome animation!)
studydev init
```

### Your First Session

```bash
# Start a 25-minute Pomodoro session
studydev session start --subject "Python Learning"

# View beautiful productivity dashboard
studydev status

# Get comprehensive help
studydev help
```

## 📖 Usage Guide

### Session Management

```bash
# Start a study session
studydev session start                    # 25-minute default
studydev session start --subject "Math"  # With subject
studydev session start --project-id 1    # Link to project

# Control active session
studydev session pause                   # Pause timer
studydev session resume                  # Resume paused session
studydev session stop --rating 5         # Stop and rate (1-5)

# View analytics
studydev session stats                   # Overall statistics
studydev session stats --days 7          # Last week
studydev session history --limit 10      # Recent sessions
```

### Project Organization

```bash
# Create projects
studydev project create "My Web App"                    # Basic project
studydev project create "Research Paper" --template research  # From template
studydev project create "ML Project" --description "Deep learning model"

# Manage projects
studydev project list                     # All projects
studydev project list --status active    # Filter by status
studydev project show 1                  # Project details
studydev project update 1 --status completed --deadline "2024-03-01"

# Templates
studydev project template list           # Available templates  
studydev project template create custom  # Create custom template
```

### Study Materials

```bash
# Bookmarks
studydev study bookmark add "https://python.org" --subject "Python" --tags "docs,reference"
studydev study bookmark list --subject Python    # Filter by subject
studydev study bookmark list --unread             # Unread only

# Flashcards with spaced repetition
studydev study flashcard add --subject "Spanish"  # Interactive creation
studydev study flashcard review                   # Review due cards
studydev study flashcard review --subject "Math" --limit 10
studydev study flashcard stats                    # Learning progress

# Course tracking
studydev study course add "Machine Learning Course" --url "coursera.org/ml" --total-lessons 50
studydev study course update 1 --progress 75      # Update completion
studydev study course list                        # All courses

# Unified review
studydev study review                             # All due materials
studydev study review --subject "Computer Science" --limit 20
```

### Analytics & Reports

```bash
# Real-time dashboard
studydev status                          # Beautiful productivity overview
studydev dashboard                       # Detailed current metrics

# Comprehensive reports
studydev report                          # Last 30 days
studydev report --days 7                 # Custom period
studydev report --output report.json     # Save to file
```

### Data Management

```bash
# Backup & restore
studydev backup                          # Create timestamped backup
studydev backup --path ~/backups        # Custom location
studydev restore ~/backups/studydev_backup_20240101_120000

# Export data
studydev export --format json           # Export all data
studydev export --format csv --data-type sessions  # Specific data
studydev export --output my_data.json   # Custom filename

# Configuration
studydev config show                     # View all settings
studydev config set session.default_duration 30    # Update setting
studydev config reset                    # Reset to defaults
```

## 🎨 Screenshots & Examples

### Beautiful Dashboard
```
╭─────────────────────────── 🎯 Productivity Meter ────────────────────────────╮
│                     🚀 PRODUCTIVITY LEVEL: EXCELLENT                         │
│                                                                               │
│                     ████████████████████████░░░░░░░░░ 78.2%                  │
│                     Score: 3.9/5.0                                           │
╰───────────────────────────────────────────────────────────────────────────────╯
```

### Interactive Timer
```
╭──────────────────── StudyDev Timer - Study ─────────────────────╮
│                          🍅 Study Session                        │
│                          📚 Machine Learning                     │
│                                                                  │
│                          ⏰ 15:42                                │
│                                                                  │
│                     ██████████████████░░░░░░░░░░░░░ 62.1%        │
│                                                                  │
│                     🔥 Great progress! Keep going!               │
╰──────────────────────────────────────────────────────────────────╯
```

### Project Overview
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Projects ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID │ Name              │ Status    │ Deadline   │ Urgency │ Progress ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━┩
│ 1  │ Web Portfolio     │ active    │ 2024-02-15 │ 🟡 Soon │ ██████░░ │
│ 2  │ Research Paper    │ active    │ 2024-01-30 │ 🔴 Due! │ ████░░░░ │
│ 3  │ ML Course Project │ planning  │ 2024-03-01 │ 🟢 Safe │ ██░░░░░░ │
└────┴───────────────────┴───────────┴────────────┴─────────┴──────────┘
```

## 🛠️ Advanced Features

### Interactive Mode

StudyDev provides guided interactive experiences:

```bash
studydev quickstart                      # Interactive quick start guide
studydev init                           # Animated welcome with setup
```

### Productivity Insights

- **Streak Tracking**: Monitor consecutive study days
- **Subject Effectiveness**: Analyze which subjects have highest productivity ratings
- **Project Productivity**: See which projects get most study time
- **Time Distribution**: Understand how you spend your learning time
- **Achievement System**: Unlock motivational milestones

### Spaced Repetition Algorithm

StudyDev uses a sophisticated SRS algorithm for flashcards:

- **Difficulty Adjustment**: Cards adjust based on your performance
- **Optimal Intervals**: Science-based scheduling for maximum retention
- **Performance Tracking**: Monitor learning progress over time
- **Smart Prioritization**: Focus on cards that need the most attention

## 🧪 Testing

StudyDev includes comprehensive testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=studydev

# Run specific test modules  
pytest tests/test_session.py
pytest tests/test_projects.py
pytest tests/test_study.py
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
git clone https://github.com/yourusername/studydev.git
cd studydev

# Install development dependencies
pip install -e ".[dev]"

# Run linting and formatting
black studydev/
flake8 studydev/

# Run tests
pytest --cov=studydev
```

## 📝 Configuration

StudyDev stores configuration in `~/.studydev/config.json`. Key settings:

```json
{
  "session": {
    "default_duration": 25,
    "notification_sound": true,
    "auto_break": false
  },
  "study": {
    "spaced_repetition_algorithm": "sm2",
    "review_batch_size": 20
  },
  "ui": {
    "color_scheme": "default",
    "animation_speed": "normal"
  }
}
```

## 📊 Data Storage

- **Database**: SQLite database at `~/.studydev/data/studydev.db`
- **Backups**: Stored in `~/.studydev/data/backups/`
- **Templates**: Custom templates in `~/.studydev/data/templates/`
- **Config**: Configuration at `~/.studydev/config.json`

## 🐛 Troubleshooting

### Common Issues

**Installation Problems**
```bash
# Ensure Python 3.8+
python --version

# Create fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate
pip install --upgrade pip
pip install -e .
```

**Database Issues**
```bash
# Reset database
rm ~/.studydev/data/studydev.db
studydev init
```

**Permission Errors**
```bash
# Fix permissions
chmod -R 755 ~/.studydev/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **Rich Library**: For beautiful terminal output
- **Typer**: For the elegant CLI framework
- **SQLite**: For reliable local data storage
- **Community**: For feedback and contributions

## 🔗 Links

- **Documentation**: [Full Documentation](https://studydev.readthedocs.io)
- **Issues**: [Report Bugs](https://github.com/yourusername/studydev/issues)
- **Discussions**: [Feature Requests](https://github.com/yourusername/studydev/discussions)
- **Changelog**: [Release Notes](CHANGELOG.md)

---

<div align="center">

**Made with ❤️ by [PrinceTheProgrammer](https://github.com/PrinceTheProgrammer)**

*Happy learning and coding! 🚀*

</div>