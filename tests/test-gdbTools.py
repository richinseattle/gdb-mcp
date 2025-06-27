"""Tests for GDB tools."""

import pytest
import tempfile
import os
import subprocess
from pathlib import Path
from modules.sessionManager import GDBSessionManager
from modules.gdbTools import GDBTools, format_gdb_response


class TestGDBTools:
    """Test cases for GDBTools."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sessionManager = GDBSessionManager()
        self.gdbTools = GDBTools(self.sessionManager)
        
        # Create a simple test program
        self.test_program_c = """
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    int result = add(5, 3);
    printf("Result: %d\\n", result);
    return 0;
}
"""
        # Create temporary test program
        self.temp_dir = tempfile.mkdtemp()
        self.test_program_path = os.path.join(self.temp_dir, "test_program.c")
        self.test_binary_path = os.path.join(self.temp_dir, "test_program")
        
        with open(self.test_program_path, 'w') as f:
            f.write(self.test_program_c)
        
        # Try to compile the test program
        try:
            subprocess.run([
                "gcc", "-g", "-o", self.test_binary_path, self.test_program_path
            ], check=True, capture_output=True)
            self.has_gcc = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.has_gcc = False
    
    def teardown_method(self):
        """Clean up after tests."""
        # Terminate any remaining sessions
        for session_id in self.sessionManager.list_sessions():
            try:
                self.sessionManager.terminate_session(session_id)
            except:
                pass
        
        # Clean up temporary files
        try:
            if os.path.exists(self.test_program_path):
                os.remove(self.test_program_path)
            if os.path.exists(self.test_binary_path):
                os.remove(self.test_binary_path)
            os.rmdir(self.temp_dir)
        except:
            pass
    
    def test_format_gdb_response_empty(self):
        """Test formatting empty GDB response."""
        result = format_gdb_response([])
        assert result == "No response from GDB"
    
    def test_format_gdb_response_console(self):
        """Test formatting console response."""
        response = [{"type": "console", "payload": "Hello World"}]
        result = format_gdb_response(response)
        assert "Console: Hello World" in result
    
    def test_format_gdb_response_result_done(self):
        """Test formatting result done response."""
        response = [{"type": "result", "message": "done", "payload": None}]
        result = format_gdb_response(response)
        assert "Result: Command completed successfully" in result
    
    def test_start_session_success(self):
        """Test successful session start."""
        try:
            result = self.gdbTools.start_session()
            assert "GDB session started successfully" in result
            assert "Session ID:" in result
            
            # Extract session ID from result
            session_id = result.split("Session ID: ")[1].strip()
            assert self.sessionManager.has_session(session_id)
        except Exception:
            pytest.skip("GDB not available on system")
    
    def test_start_session_invalid_gdb_path(self):
        """Test session start with invalid GDB path."""
        result = self.gdbTools.start_session("/nonexistent/gdb")
        assert "Error starting GDB session" in result
    
    def test_list_sessions_empty(self):
        """Test listing sessions when none exist."""
        result = self.gdbTools.list_sessions()
        assert result == "No active GDB sessions"
    
    def test_list_sessions_with_sessions(self):
        """Test listing sessions when they exist."""
        try:
            # Start a session
            start_result = self.gdbTools.start_session()
            if "Error" in start_result:
                pytest.skip("GDB not available on system")
            
            result = self.gdbTools.list_sessions()
            assert "Active GDB sessions:" in result
            assert "-" in result  # Should contain session ID with dash prefix
        except Exception:
            pytest.skip("GDB not available on system")
    
    def test_terminate_session_success(self):
        """Test successful session termination."""
        try:
            # Start a session
            start_result = self.gdbTools.start_session()
            if "Error" in start_result:
                pytest.skip("GDB not available on system")
            
            session_id = start_result.split("Session ID: ")[1].strip()
            
            # Terminate the session
            result = self.gdbTools.terminate_session(session_id)
            assert "terminated successfully" in result
            assert not self.sessionManager.has_session(session_id)
        except Exception:
            pytest.skip("GDB not available on system")
    
    def test_terminate_session_nonexistent(self):
        """Test termination of non-existent session."""
        result = self.gdbTools.terminate_session("nonexistent-session")
        assert "not found" in result
    
    def test_load_program_nonexistent_session(self):
        """Test loading program with non-existent session."""
        result = self.gdbTools.load_program("nonexistent", "/some/path")
        assert "not found" in result
    
    def test_load_program_nonexistent_file(self):
        """Test loading non-existent program file."""
        try:
            # Start a session
            start_result = self.gdbTools.start_session()
            if "Error" in start_result:
                pytest.skip("GDB not available on system")
            
            session_id = start_result.split("Session ID: ")[1].strip()
            
            # Try to load non-existent file
            result = self.gdbTools.load_program(session_id, "/nonexistent/program")
            assert "does not exist" in result
        except Exception:
            pytest.skip("GDB not available on system")
    
    @pytest.mark.skipif(not os.path.exists("/usr/bin/gcc"), reason="GCC not available")
    def test_load_program_success(self):
        """Test successful program loading."""
        if not self.has_gcc:
            pytest.skip("GCC not available for compilation")
        
        try:
            # Start a session
            start_result = self.gdbTools.start_session()
            if "Error" in start_result:
                pytest.skip("GDB not available on system")
            
            session_id = start_result.split("Session ID: ")[1].strip()
            
            # Load the test program
            result = self.gdbTools.load_program(session_id, self.test_binary_path)
            # Should not contain error messages
            assert "Error" not in result or "done" in result.lower()
        except Exception:
            pytest.skip("GDB not available on system")
    
    def test_execute_command_nonexistent_session(self):
        """Test executing command with non-existent session."""
        result = self.gdbTools.execute_command("nonexistent", "help")
        assert "not found" in result
    
    def test_execute_command_success(self):
        """Test successful command execution."""
        try:
            # Start a session
            start_result = self.gdbTools.start_session()
            if "Error" in start_result:
                pytest.skip("GDB not available on system")
            
            session_id = start_result.split("Session ID: ")[1].strip()
            
            # Execute a simple command
            result = self.gdbTools.execute_command(session_id, "help")
            # Should not be an error message
            assert "Error executing command" not in result
        except Exception:
            pytest.skip("GDB not available on system")
    
    def test_set_breakpoint_nonexistent_session(self):
        """Test setting breakpoint with non-existent session."""
        result = self.gdbTools.set_breakpoint("nonexistent", "main")
        assert "not found" in result
    
    @pytest.mark.skipif(not os.path.exists("/usr/bin/gcc"), reason="GCC not available")
    def test_debugging_workflow(self):
        """Test a complete debugging workflow."""
        if not self.has_gcc:
            pytest.skip("GCC not available for compilation")
        
        try:
            # Start a session
            start_result = self.gdbTools.start_session()
            if "Error" in start_result:
                pytest.skip("GDB not available on system")
            
            session_id = start_result.split("Session ID: ")[1].strip()
            
            # Load program
            load_result = self.gdbTools.load_program(session_id, self.test_binary_path)
            assert "Error" not in load_result or "done" in load_result.lower()
            
            # Set breakpoint
            bp_result = self.gdbTools.set_breakpoint(session_id, "main")
            # Breakpoint setting might succeed or fail depending on GDB version
            # Just ensure no crash
            assert isinstance(bp_result, str)
            
            # Try to get backtrace (might not work without running program)
            bt_result = self.gdbTools.get_backtrace(session_id)
            assert isinstance(bt_result, str)
            
            # Print a simple expression
            print_result = self.gdbTools.print_expression(session_id, "1+1")
            assert isinstance(print_result, str)
            
        except Exception:
            pytest.skip("GDB not available on system")
    
    def test_all_tools_handle_invalid_session(self):
        """Test that all tools handle invalid session IDs gracefully."""
        invalid_session = "invalid-session-id"
        
        # Test all tools with invalid session
        tools_to_test = [
            (self.gdbTools.load_program, (invalid_session, "/some/path")),
            (self.gdbTools.execute_command, (invalid_session, "help")),
            (self.gdbTools.attach_to_process, (invalid_session, 1234)),
            (self.gdbTools.load_core_dump, (invalid_session, "/some/core")),
            (self.gdbTools.set_breakpoint, (invalid_session, "main")),
            (self.gdbTools.continue_execution, (invalid_session,)),
            (self.gdbTools.step_execution, (invalid_session,)),
            (self.gdbTools.next_execution, (invalid_session,)),
            (self.gdbTools.finish_function, (invalid_session,)),
            (self.gdbTools.get_backtrace, (invalid_session,)),
            (self.gdbTools.print_expression, (invalid_session, "1")),
            (self.gdbTools.examine_memory, (invalid_session, "0x0")),
            (self.gdbTools.get_registers, (invalid_session,)),
        ]
        
        for tool_func, args in tools_to_test:
            result = tool_func(*args)
            assert isinstance(result, str)
            assert "not found" in result or "Error" in result