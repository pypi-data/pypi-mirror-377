"""
StudyDev Core Functionality Tests
Basic test suite to ensure system reliability
"""

import pytest
import tempfile
import os
from pathlib import Path
from studydev.core.config import Config
from studydev.core.database import Database


class TestConfig:
    """Test configuration management"""
    
    def test_config_initialization(self):
        """Test that configuration initializes properly"""
        config = Config()
        assert config is not None
        assert hasattr(config, 'config_path')
        assert hasattr(config, 'data_path')
    
    def test_config_defaults(self):
        """Test default configuration values"""
        config = Config()
        # Test some default values
        assert config.get('session.default_duration', 25) == 25
        assert isinstance(config.get('session.notification_sound', True), bool)
    
    def test_config_set_get(self):
        """Test setting and getting configuration values"""
        config = Config()
        test_key = 'test.value'
        test_value = 'test_data'
        
        config.set(test_key, test_value)
        retrieved_value = config.get(test_key)
        
        assert retrieved_value == test_value


class TestDatabase:
    """Test database functionality"""
    
    def test_database_initialization(self):
        """Test that database initializes properly"""
        db = Database()
        assert db is not None
        assert hasattr(db, 'db_path')
    
    def test_database_connection(self):
        """Test database connection"""
        db = Database()
        assert db.is_connected() is True
    
    def test_database_table_creation(self):
        """Test that required tables are created"""
        db = Database()
        
        # Check that core tables exist
        tables = db.execute_query("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        
        table_names = [table[0] for table in tables]
        
        # Ensure core tables exist
        assert 'sessions' in table_names
        assert 'projects' in table_names
        assert 'bookmarks' in table_names
        assert 'flashcards' in table_names
        assert 'courses' in table_names
    
    def test_database_insert_and_query(self):
        """Test basic database operations"""
        db = Database()
        
        # Insert test data
        result = db.execute_update("""
            INSERT INTO sessions (session_type, subject, start_time, duration)
            VALUES (?, ?, ?, ?)
        """, ('study', 'Test Subject', '2024-01-01T10:00:00', 1500))
        
        assert result is not None
        
        # Query test data
        sessions = db.execute_query("""
            SELECT * FROM sessions WHERE subject = ?
        """, ('Test Subject',))
        
        assert len(sessions) >= 1
        assert sessions[0][2] == 'Test Subject'  # subject column


class TestCLICommands:
    """Test CLI command functionality"""
    
    def test_help_command(self):
        """Test that help command works"""
        import subprocess
        result = subprocess.run(['studydev', '--help'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'StudyDev' in result.stdout
    
    def test_version_command(self):
        """Test that version command works"""
        import subprocess
        result = subprocess.run(['studydev', 'version'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'StudyDev' in result.stdout


class TestSessionManager:
    """Test session management functionality"""
    
    def test_session_manager_import(self):
        """Test that SessionManager can be imported"""
        from studydev.modules.session.manager import SessionManager
        
        session_manager = SessionManager()
        assert session_manager is not None
    
    def test_session_stats_structure(self):
        """Test that session stats return proper structure"""
        from studydev.modules.session.manager import SessionManager
        
        session_manager = SessionManager()
        stats = session_manager.get_session_stats('today')
        
        assert isinstance(stats, dict)
        assert 'total_sessions' in stats
        assert 'total_time_seconds' in stats
        assert 'total_time_hours' in stats
        assert 'subjects' in stats
        assert 'session_types' in stats


class TestProjectManager:
    """Test project management functionality"""
    
    def test_project_manager_import(self):
        """Test that ProjectManager can be imported"""
        from studydev.modules.project.manager import ProjectManager
        
        project_manager = ProjectManager()
        assert project_manager is not None
    
    def test_project_templates(self):
        """Test project template functionality"""
        from studydev.modules.project.manager import ProjectManager
        
        project_manager = ProjectManager()
        templates = project_manager.get_available_templates()
        
        assert isinstance(templates, dict)
        # Should have at least some default templates
        assert len(templates) > 0


class TestStudyManager:
    """Test study materials functionality"""
    
    def test_study_manager_import(self):
        """Test that StudyManager can be imported"""
        from studydev.modules.study.manager import StudyManager
        
        study_manager = StudyManager()
        assert study_manager is not None
    
    def test_spaced_repetition_intervals(self):
        """Test spaced repetition interval calculation"""
        from studydev.modules.study.manager import StudyManager
        
        study_manager = StudyManager()
        
        # Test interval calculation for new card
        interval = study_manager._calculate_next_interval(0, 4)  # rating 4 (good)
        assert interval > 0
        
        # Test interval increase for repeated card
        next_interval = study_manager._calculate_next_interval(interval, 4)
        assert next_interval > interval


class TestInteractiveUI:
    """Test interactive UI functionality"""
    
    def test_interactive_ui_import(self):
        """Test that InteractiveUI can be imported"""
        from studydev.utils.interactive import InteractiveUI
        
        ui = InteractiveUI()
        assert ui is not None
        assert hasattr(ui, 'motivational_messages')
    
    def test_productivity_gauge(self):
        """Test productivity gauge creation"""
        from studydev.utils.interactive import InteractiveUI
        
        ui = InteractiveUI()
        gauge = ui.create_productivity_gauge(3.5)
        
        assert gauge is not None
        # Should be a Rich Panel object
        assert hasattr(gauge, 'renderable')


class TestIntegration:
    """Test integration between modules"""
    
    def test_integration_manager_import(self):
        """Test that IntegrationManager can be imported"""
        from studydev.utils.integration import IntegrationManager
        
        integration = IntegrationManager()
        assert integration is not None
    
    def test_dashboard_data_structure(self):
        """Test dashboard data generation"""
        from studydev.utils.integration import IntegrationManager
        
        integration = IntegrationManager()
        dashboard_data = integration.generate_dashboard_data()
        
        assert isinstance(dashboard_data, dict)
        assert 'recent_stats' in dashboard_data
        assert 'current_streak' in dashboard_data
        assert 'flashcards_due' in dashboard_data
    
    def test_productivity_report_structure(self):
        """Test productivity report generation"""
        from studydev.utils.integration import IntegrationManager
        
        integration = IntegrationManager()
        report = integration.generate_productivity_report(7)  # 7 days
        
        assert isinstance(report, dict)
        assert 'period' in report
        assert 'sessions' in report
        assert 'projects' in report
        assert 'study' in report


# Integration Tests
class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_full_workflow(self):
        """Test a complete workflow"""
        # This is a basic integration test
        # In practice, you'd want more comprehensive E2E tests
        
        from studydev.core.config import Config
        from studydev.core.database import Database
        
        # Initialize components
        config = Config()
        db = Database()
        
        # Verify system is functional
        assert config is not None
        assert db is not None
        assert db.is_connected()
        
        # Test basic data operations
        test_data = db.execute_query("SELECT COUNT(*) FROM sessions")
        assert test_data is not None
        assert len(test_data) > 0


if __name__ == '__main__':
    # Run tests if executed directly
    pytest.main([__file__, '-v'])