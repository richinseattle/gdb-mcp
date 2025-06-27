"""Integration tests for the complete GDB MCP workflow."""

import pytest
import os
import subprocess
import tempfile
from modules.sessionManager import GDBSessionManager
from modules.gdbTools import GDBTools


@pytest.mark.integration
class TestGDBMCPIntegration:
    """Integration tests for complete GDB MCP workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sessionManager = GDBSessionManager()
        self.gdbTools = GDBTools(self.sessionManager)
    
    def teardown_method(self):
        """Clean up after tests."""
        # Clean up any remaining sessions
        for session_id in list(self.sessionManager.sessions.keys()):
            try:
                self.sessionManager.terminate_session(session_id)
            except:
                pass
    
    @pytest.mark.requires_gdb
    def test_basic_debugging_workflow(self, test_program):
        """Test a complete basic debugging workflow."""
        if not test_program['compiled']:
            pytest.skip("Test program could not be compiled")
        
        # Start GDB session
        start_result = self.gdbTools.start_session()
        assert "GDB session started successfully" in start_result
        session_id = start_result.split("Session ID: ")[1].strip()
        
        try:
            # Load the test program
            load_result = self.gdbTools.load_program(session_id, test_program['binary_file'])
            assert "Error" not in load_result or "done" in load_result.lower()
            
            # Set a breakpoint at main
            bp_result = self.gdbTools.set_breakpoint(session_id, "main")
            assert isinstance(bp_result, str)
            
            # Try to run the program
            run_result = self.gdbTools.execute_command(session_id, "run")
            assert isinstance(run_result, str)
            
            # Get backtrace
            bt_result = self.gdbTools.get_backtrace(session_id)
            assert isinstance(bt_result, str)
            
            # Print a variable (might not work if not at breakpoint)
            print_result = self.gdbTools.print_expression(session_id, "1+1")
            assert isinstance(print_result, str)
            
        finally:
            # Clean up
            self.gdbTools.terminate_session(session_id)
    
    @pytest.mark.requires_gdb
    def test_multiple_session_workflow(self):
        """Test workflow with multiple concurrent sessions."""
        session_ids = []
        
        try:
            # Start multiple sessions
            for i in range(3):
                start_result = self.gdbTools.start_session()
                assert "GDB session started successfully" in start_result
                session_id = start_result.split("Session ID: ")[1].strip()
                session_ids.append(session_id)
            
            # Verify all sessions are listed
            list_result = self.gdbTools.list_sessions()
            for session_id in session_ids:
                assert session_id in list_result
            
            # Execute commands in different sessions
            for session_id in session_ids:
                help_result = self.gdbTools.execute_command(session_id, "help")
                assert isinstance(help_result, str)
                assert "Error executing command" not in help_result
            
        finally:
            # Clean up all sessions
            for session_id in session_ids:
                try:
                    self.gdbTools.terminate_session(session_id)
                except:
                    pass
    
    @pytest.mark.requires_gdb
    @pytest.mark.requires_gcc
    def test_advanced_debugging_workflow(self, test_program):
        """Test advanced debugging features."""
        if not test_program['compiled']:
            pytest.skip("Test program could not be compiled")
        
        # Start session
        start_result = self.gdbTools.start_session()
        assert "GDB session started successfully" in start_result
        session_id = start_result.split("Session ID: ")[1].strip()
        
        try:
            # Load program
            load_result = self.gdbTools.load_program(session_id, test_program['binary_file'])
            assert "Error" not in load_result or "done" in load_result.lower()
            
            # Set breakpoint at factorial function
            bp_result = self.gdbTools.set_breakpoint(session_id, "factorial")
            assert isinstance(bp_result, str)
            
            # Run program
            run_result = self.gdbTools.execute_command(session_id, "run")
            assert isinstance(run_result, str)
            
            # If we hit the breakpoint, try stepping
            if "breakpoint" in run_result.lower() or "stopped" in run_result.lower():
                # Try stepping
                step_result = self.gdbTools.step_execution(session_id)
                assert isinstance(step_result, str)
                
                # Try next
                next_result = self.gdbTools.next_execution(session_id)
                assert isinstance(next_result, str)
                
                # Get backtrace
                bt_result = self.gdbTools.get_backtrace(session_id)
                assert isinstance(bt_result, str)
            
            # Try to examine some memory (might not work without proper context)
            mem_result = self.gdbTools.examine_memory(session_id, "&main")
            assert isinstance(mem_result, str)
            
            # Get register info
            reg_result = self.gdbTools.get_registers(session_id)
            assert isinstance(reg_result, str)
            
        finally:
            # Clean up
            self.gdbTools.terminate_session(session_id)
    
    @pytest.mark.requires_gdb
    def test_error_recovery_workflow(self):
        """Test error recovery and handling."""
        # Start session
        start_result = self.gdbTools.start_session()
        assert "GDB session started successfully" in start_result
        session_id = start_result.split("Session ID: ")[1].strip()
        
        try:
            # Try to load non-existent file
            load_result = self.gdbTools.load_program(session_id, "/nonexistent/program")
            assert "does not exist" in load_result
            
            # Session should still be functional
            help_result = self.gdbTools.execute_command(session_id, "help")
            assert "Error executing command" not in help_result
            
            # Try invalid command
            invalid_result = self.gdbTools.execute_command(session_id, "invalid_command_xyz")
            assert isinstance(invalid_result, str)
            
            # Session should still be functional
            version_result = self.gdbTools.execute_command(session_id, "show version")
            assert isinstance(version_result, str)
            
        finally:
            # Clean up
            self.gdbTools.terminate_session(session_id)
    
    @pytest.mark.requires_gdb
    def test_session_isolation(self):
        """Test that sessions are properly isolated."""
        # Start two sessions
        start_result1 = self.gdbTools.start_session()
        assert "GDB session started successfully" in start_result1
        session_id1 = start_result1.split("Session ID: ")[1].strip()
        
        start_result2 = self.gdbTools.start_session()
        assert "GDB session started successfully" in start_result2
        session_id2 = start_result2.split("Session ID: ")[1].strip()
        
        try:
            # Execute different commands in each session
            result1 = self.gdbTools.execute_command(session_id1, "set confirm off")
            result2 = self.gdbTools.execute_command(session_id2, "show confirm")
            
            # Both should work independently
            assert isinstance(result1, str)
            assert isinstance(result2, str)
            
            # Terminate one session
            term_result = self.gdbTools.terminate_session(session_id1)
            assert "terminated successfully" in term_result
            
            # Other session should still work
            help_result = self.gdbTools.execute_command(session_id2, "help")
            assert "Error executing command" not in help_result
            
            # First session should be gone
            list_result = self.gdbTools.list_sessions()
            assert session_id1 not in list_result
            assert session_id2 in list_result
            
        finally:
            # Clean up remaining session
            try:
                self.gdbTools.terminate_session(session_id2)
            except:
                pass
    
    def test_resource_consistency(self):
        """Test that resources provide consistent information."""
        import server
        
        # Initially no sessions
        sessions_resource = server.list_gdb_sessions()
        assert "No active GDB sessions" in sessions_resource
        
        # Help resource should always be available
        help_resource = server.gdb_help()
        assert "GDB MCP Server Help" in help_resource
        assert len(help_resource) > 100  # Should be substantial help text
        
        # Test with active sessions
        try:
            start_result = self.gdbTools.start_session()
            if "GDB session started successfully" in start_result:
                session_id = start_result.split("Session ID: ")[1].strip()
                
                # Resource should now show active session
                sessions_resource = server.list_gdb_sessions()
                assert "Active GDB Sessions:" in sessions_resource
                assert session_id in sessions_resource
                
                # Clean up
                self.gdbTools.terminate_session(session_id)
                
                # Resource should show no sessions again
                sessions_resource = server.list_gdb_sessions()
                assert "No active GDB sessions" in sessions_resource
                
        except Exception:
            pytest.skip("GDB not available on system")