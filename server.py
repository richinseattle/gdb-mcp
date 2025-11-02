#!/usr/bin/env python3
"""
Multi-Debugger MCP Server

A Model Context Protocol server that provides debugging functionality
for GDB and LLDB debuggers, for use with Claude Desktop, VSCode Copilot, 
or other AI assistants.
"""

import logging
from mcp.server.fastmcp import FastMCP
from modules import DebuggerFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    debugger_tools, debugger_type = DebuggerFactory.create_tools()
    logger.info(f"Using {debugger_type.upper()} debugger")
    mcp = FastMCP(f"{debugger_type.upper()} Debugger")
except Exception as e:
    logger.error(f"No debuggers available: {e}")
    logger.info("Available debuggers:")
    logger.info(DebuggerFactory.list_debuggers())
    mcp = FastMCP("Debugger MCP (No Debuggers Available)")
    debugger_tools = None
    debugger_type = None

def _get_gdb_tools():
    """Helper function to get GDB tools with error handling."""
    try:
        tools, _ = DebuggerFactory.create_tools('gdb')
        return tools
    except Exception as e:
        raise RuntimeError(f"GDB not available: {str(e)}")

# Unified debugger tools (work with any available debugger)
@mcp.tool()
def debugger_status() -> str:
    """Get status of available debuggers."""
    return DebuggerFactory.list_debuggers()

@mcp.tool()
def debugger_start(debugger_type_param: str = None, debugger_path: str = None) -> str:
    """Start a debugging session with auto-detection or specified debugger type."""
    if not debugger_tools:
        return "Error: No debuggers are available on this system"
    
    # Use default debugger (don't create new instances to avoid session isolation)
    return debugger_tools.start_session(debugger_path)

@mcp.tool()
def debugger_terminate(session_id: str) -> str:
    """Terminate a debugging session."""
    if not debugger_tools:
        return "Error: No debuggers are available on this system"
    return debugger_tools.terminate_session(session_id)

@mcp.tool()
def debugger_list_sessions() -> str:
    """List all active debugging sessions."""
    if not debugger_tools:
        return "Error: No debuggers are available on this system"
    return debugger_tools.list_sessions()

@mcp.tool()
def debugger_command(session_id: str, command: str) -> str:
    """Execute an arbitrary debugger command."""
    if not debugger_tools:
        return "Error: No debuggers are available on this system"
    return debugger_tools.execute_command(session_id, command)
    
# GDB-specific tools (use gdb_command for advanced features)
@mcp.tool()
def gdb_start(gdb_path: str = "gdb") -> str:
    """Start a new GDB debugging session."""
    try:
        return _get_gdb_tools().start_session(gdb_path)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def gdb_terminate(session_id: str) -> str:
    """Terminate a GDB debugging session."""
    try:
        return _get_gdb_tools().terminate_session(session_id)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def gdb_list_sessions() -> str:
    """List all active GDB sessions."""
    try:
        return _get_gdb_tools().list_sessions()
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def gdb_command(session_id: str, command: str) -> str:
    """Execute any arbitrary GDB command. Use this for all GDB operations."""
    try:
        return _get_gdb_tools().execute_command(session_id, command)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.resource("gdb://sessions")
def list_gdb_sessions() -> str:
    """Resource that provides information about active GDB sessions."""
    try:
        tools, _ = DebuggerFactory.create_tools('gdb')
        sessions = tools.list_sessions()
        if not sessions:
            return "No active GDB sessions"
        
        session_info = [f"Session ID: {session_id}" for session_id in sessions]
        return "Active GDB Sessions:\n" + "\n".join(session_info)
    except Exception as e:
        return f"Error: {str(e)}"

# LLDB-specific tools
@mcp.tool()
def lldb_start(lldb_path: str = None) -> str:
    """Start a new LLDB debugging session."""
    try:
        tools, _ = DebuggerFactory.create_tools('lldb')
        return tools.start_session(lldb_path)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def lldb_terminate(session_id: str) -> str:
    """Terminate an LLDB debugging session."""
    try:
        tools, _ = DebuggerFactory.create_tools('lldb')
        return tools.terminate_session(session_id)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def lldb_list_sessions() -> str:
    """List all active LLDB sessions."""
    try:
        tools, _ = DebuggerFactory.create_tools('lldb')
        return tools.list_sessions()
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def lldb_command(session_id: str, command: str) -> str:
    """Execute an arbitrary LLDB command."""
    try:
        tools, _ = DebuggerFactory.create_tools('lldb')
        return tools.execute_command(session_id, command)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()