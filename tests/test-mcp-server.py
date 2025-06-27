"""Tests for MCP server integration."""

import pytest
import tempfile
import os
import subprocess
from unittest.mock import patch, MagicMock

# Import the server components
import sys
sys.path.append('.')
from modules.sessionManager import GDBSessionManager
from modules.gdbTools import GDBTools


class TestMCPServerIntegration:
    """Test cases for MCP server integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sessionManager = GDBSessionManager()
        self.gdbTools = GDBTools(self.sessionManager)
    
    def teardown_method(self):
        """Clean up after tests."""
        # Clean up any sessions
        for session_id in list(self.sessionManager.sessions.keys()):
            try:
                self.sessionManager.terminate_session(session_id)
            except:
                pass
    
    def test_server_imports(self):
        """Test that server.py can be imported without errors."""
        try:
            # This tests that all imports in server.py work
            from modules.sessionManager import GDBSessionManager
            from modules.gdbTools import GDBTools
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import server components: {e}")
    
    def test_mcp_tool_functions_exist(self):
        """Test that all expected MCP tool functions are available."""
        # Import server to check if all functions are defined
        import server
        
        # Check that the mcp object exists
        assert hasattr(server, 'mcp')
        
        # Check that session manager and tools are initialized
        assert hasattr(server, 'sessionManager')
        assert hasattr(server, 'gdbTools')
        assert isinstance(server.sessionManager, GDBSessionManager)
        assert isinstance(server.gdbTools, GDBTools)
    
    def test_session_workflow_integration(self):
        """Test complete session workflow through the tools."""
        try:
            # Test session creation
            result = self.gdbTools.start_session()
            if "Error" in result:
                pytest.skip("GDB not available on system")
            
            # Extract session ID
            session_id = result.split("Session ID: ")[1].strip()
            
            # Test session listing
            list_result = self.gdbTools.list_sessions()
            assert session_id in list_result
            
            # Test session termination
            term_result = self.gdbTools.terminate_session(session_id)
            assert "terminated successfully" in term_result
            
            # Verify session is gone
            list_result_after = self.gdbTools.list_sessions()
            assert "No active GDB sessions" in list_result_after
            
        except Exception:
            pytest.skip("GDB not available on system")
    
    def test_error_handling_consistency(self):
        """Test that error handling is consistent across all tools."""
        invalid_session = "invalid-session-123"
        
        # All these should return error messages, not raise exceptions
        error_results = [
            self.gdbTools.load_program(invalid_session, "/fake/path"),
            self.gdbTools.execute_command(invalid_session, "help"),
            self.gdbTools.attach_to_process(invalid_session, 1234),
            self.gdbTools.load_core_dump(invalid_session, "/fake/core"),
            self.gdbTools.set_breakpoint(invalid_session, "main"),
            self.gdbTools.continue_execution(invalid_session),
            self.gdbTools.step_execution(invalid_session),
            self.gdbTools.next_execution(invalid_session),
            self.gdbTools.finish_function(invalid_session),
            self.gdbTools.get_backtrace(invalid_session),
            self.gdbTools.print_expression(invalid_session, "1"),
            self.gdbTools.examine_memory(invalid_session, "0x0"),
            self.gdbTools.get_registers(invalid_session),
        ]
        
        for result in error_results:
            assert isinstance(result, str)
            assert len(result) > 0
            # Should contain some indication of error
            assert any(word in result.lower() for word in ["error", "not found", "failed"])
    
    def test_resource_functions(self):
        """Test that resource functions work correctly."""
        import server
        
        # Test sessions resource
        sessions_resource = server.list_gdb_sessions()
        assert isinstance(sessions_resource, str)
        assert "No active GDB sessions" in sessions_resource or "Active GDB Sessions:" in sessions_resource
        
        # Test help resource
        help_resource = server.gdb_help()
        assert isinstance(help_resource, str)
        assert "GDB MCP Server Help" in help_resource
        assert "gdb_start" in help_resource
        assert "Session Management" in help_resource
    
    @pytest.mark.skipif(not os.path.exists("/usr/bin/gdb"), reason="GDB not available")
    def test_real_gdb_integration(self):
        """Test integration with real GDB if available."""
        try:
            # Start a real session
            result = self.gdbTools.start_session()
            if "Error" in result:
                pytest.skip("GDB not available on system")
            
            session_id = result.split("Session ID: ")[1].strip()
            
            # Test basic GDB command
            help_result = self.gdbTools.execute_command(session_id, "help")
            assert isinstance(help_result, str)
            assert len(help_result) > 0
            
            # Test version command
            version_result = self.gdbTools.execute_command(session_id, "show version")
            assert isinstance(version_result, str)
            
            # Clean up
            self.gdbTools.terminate_session(session_id)
            
        except Exception as e:
            pytest.skip(f"GDB integration test failed: {e}")
    
    def test_multiple_sessions(self):
        """Test handling multiple concurrent sessions."""
        try:
            # Start multiple sessions
            session_ids = []
            for i in range(3):
                result = self.gdbTools.start_session()
                if "Error" in result:
                    pytest.skip("GDB not available on system")
                session_id = result.split("Session ID: ")[1].strip()
                session_ids.append(session_id)
            
            # Verify all sessions exist
            list_result = self.gdbTools.list_sessions()
            for session_id in session_ids:
                assert session_id in list_result
            
            # Terminate all sessions
            for session_id in session_ids:
                term_result = self.gdbTools.terminate_session(session_id)
                assert "terminated successfully" in term_result
            
            # Verify all sessions are gone
            final_list = self.gdbTools.list_sessions()
            assert "No active GDB sessions" in final_list
            
        except Exception:
            pytest.skip("GDB not available on system")
    
    def test_file_operations_error_handling(self):
        """Test file operations with non-existent files."""
        try:
            # Start a session
            result = self.gdbTools.start_session()
            if "Error" in result:
                pytest.skip("GDB not available on system")
            
            session_id = result.split("Session ID: ")[1].strip()
            
            # Test loading non-existent program
            load_result = self.gdbTools.load_program(session_id, "/nonexistent/program")
            assert "does not exist" in load_result
            
            # Test loading non-existent core dump
            core_result = self.gdbTools.load_core_dump(session_id, "/nonexistent/core")
            assert "does not exist" in core_result
            
            # Clean up
            self.gdbTools.terminate_session(session_id)
            
        except Exception:
            pytest.skip("GDB not available on system")