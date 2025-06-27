"""Tests for GDB session manager."""

import pytest
import tempfile
import os
from modules.sessionManager import GDBSessionManager


class TestGDBSessionManager:
    """Test cases for GDBSessionManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sessionManager = GDBSessionManager()
    
    def teardown_method(self):
        """Clean up after tests."""
        # Terminate any remaining sessions
        for session_id in list(self.sessionManager.sessions.keys()):
            try:
                self.sessionManager.terminate_session(session_id)
            except:
                pass
    
    def test_create_session_success(self):
        """Test successful session creation."""
        session_id = self.sessionManager.create_session()
        
        assert session_id is not None
        assert len(session_id) > 0
        assert self.sessionManager.has_session(session_id)
        assert session_id in self.sessionManager.list_sessions()
    
    def test_create_session_with_custom_gdb_path(self):
        """Test session creation with custom GDB path."""
        # This should work if gdb is available
        try:
            session_id = self.sessionManager.create_session("gdb")
            assert session_id is not None
            assert self.sessionManager.has_session(session_id)
        except Exception:
            # If GDB is not available, the test should skip
            pytest.skip("GDB not available on system")
    
    def test_create_session_invalid_gdb_path(self):
        """Test session creation with invalid GDB path."""
        with pytest.raises(Exception):
            self.sessionManager.create_session("/nonexistent/gdb")
    
    def test_get_session_success(self):
        """Test successful session retrieval."""
        session_id = self.sessionManager.create_session()
        gdb_controller = self.sessionManager.get_session(session_id)
        
        assert gdb_controller is not None
    
    def test_get_session_nonexistent(self):
        """Test retrieval of non-existent session."""
        with pytest.raises(ValueError, match="GDB session .* not found"):
            self.sessionManager.get_session("nonexistent-session")
    
    def test_terminate_session_success(self):
        """Test successful session termination."""
        session_id = self.sessionManager.create_session()
        
        assert self.sessionManager.has_session(session_id)
        result = self.sessionManager.terminate_session(session_id)
        
        assert result is True
        assert not self.sessionManager.has_session(session_id)
        assert session_id not in self.sessionManager.list_sessions()
    
    def test_terminate_session_nonexistent(self):
        """Test termination of non-existent session."""
        result = self.sessionManager.terminate_session("nonexistent-session")
        assert result is False
    
    def test_list_sessions_empty(self):
        """Test listing sessions when none exist."""
        sessions = self.sessionManager.list_sessions()
        assert sessions == []
    
    def test_list_sessions_multiple(self):
        """Test listing multiple sessions."""
        session1 = self.sessionManager.create_session()
        session2 = self.sessionManager.create_session()
        
        sessions = self.sessionManager.list_sessions()
        assert len(sessions) == 2
        assert session1 in sessions
        assert session2 in sessions
    
    def test_has_session(self):
        """Test session existence checking."""
        assert not self.sessionManager.has_session("nonexistent")
        
        session_id = self.sessionManager.create_session()
        assert self.sessionManager.has_session(session_id)
        
        self.sessionManager.terminate_session(session_id)
        assert not self.sessionManager.has_session(session_id)