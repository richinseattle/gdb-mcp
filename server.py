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
    
# GDB-specific tools
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
def gdb_load(session_id: str, program_path: str) -> str:
    """Load a program into an existing GDB session."""
    return gdbTools.load_program(session_id, program_path)

@mcp.tool()
def gdb_attach(session_id: str, pid: int) -> str:
    """Attach GDB to a running process."""
    return gdbTools.attach_to_process(session_id, pid)

@mcp.tool()
def gdb_load_core(session_id: str, core_file: str) -> str:
    """Load a core dump file for analysis."""
    return gdbTools.load_core_dump(session_id, core_file)
@mcp.tool()
def gdb_continue(session_id: str) -> str:
    """Continue program execution."""
    return gdbTools.continue_execution(session_id)

@mcp.tool()
def gdb_step(session_id: str) -> str:
    """Step into functions."""
    return gdbTools.step_execution(session_id)

@mcp.tool()
def gdb_next(session_id: str) -> str:
    """Step over function calls."""
    return gdbTools.next_execution(session_id)

@mcp.tool()
def gdb_finish(session_id: str) -> str:
    """Execute until the current function returns."""
    return gdbTools.finish_function(session_id)
@mcp.tool()
def gdb_set_breakpoint(session_id: str, location: str) -> str:
    """Set a breakpoint at the specified location."""
    return gdbTools.set_breakpoint(session_id, location)

@mcp.tool()
def gdb_backtrace(session_id: str) -> str:
    """Show the call stack."""
    return gdbTools.get_backtrace(session_id)

@mcp.tool()
def gdb_print(session_id: str, expression: str) -> str:
    """Print the value of an expression."""
    return gdbTools.print_expression(session_id, expression)

@mcp.tool()
def gdb_examine(session_id: str, address: str, format_spec: str = "x") -> str:
    """Examine memory at the specified address."""
    return gdbTools.examine_memory(session_id, address, format_spec)

@mcp.tool()
def gdb_info_registers(session_id: str) -> str:
    """Display processor registers."""
    return gdbTools.get_registers(session_id)

@mcp.tool()
def gdb_command(session_id: str, command: str) -> str:
    """Execute an arbitrary GDB command."""
    try:
        return _get_gdb_tools().execute_command(session_id, command)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def gdb_disassemble_function(session_id: str, function_name: str, mixed_mode: bool = False) -> str:
    """Disassemble a function with optional source code mixing."""
    return gdbTools.disassemble_function(session_id, function_name, mixed_mode)

@mcp.tool()
def gdb_disassemble_address_range(session_id: str, start_addr: str, end_addr: str, mixed_mode: bool = False) -> str:
    """Disassemble a range of memory addresses."""
    return gdbTools.disassemble_address_range(session_id, start_addr, end_addr, mixed_mode)

@mcp.tool()
def gdb_disassemble_around_pc(session_id: str, instruction_count: int = 10, mixed_mode: bool = False) -> str:
    """Disassemble instructions around the current program counter."""
    return gdbTools.disassemble_around_pc(session_id, instruction_count, mixed_mode)

@mcp.tool()
def gdb_get_local_variables(session_id: str, print_values: bool = True) -> str:
    """Get local variables in the current stack frame."""
    return gdbTools.get_local_variables(session_id, print_values)

@mcp.tool()
def gdb_get_function_arguments(session_id: str, print_values: bool = True) -> str:
    """Get function arguments for all stack frames."""
    return gdbTools.get_function_arguments(session_id, print_values)

@mcp.tool()
def gdb_get_stack_frames(session_id: str, low_frame: int = None, high_frame: int = None) -> str:
    """Get detailed stack frame information."""
    return gdbTools.get_stack_frames(session_id, low_frame, high_frame)

@mcp.tool()
def gdb_evaluate_expression(session_id: str, expression: str) -> str:
    """Evaluate an expression with structured output."""
    return gdbTools.evaluate_expression(session_id, expression)

@mcp.tool()
def gdb_get_register_names(session_id: str) -> str:
    """Get list of all register names."""
    return gdbTools.get_register_names(session_id)

@mcp.tool()
def gdb_get_register_values(session_id: str, register_numbers: list = None) -> str:
    """Get register values with structured output."""
    return gdbTools.get_register_values(session_id, register_numbers)

@mcp.tool()
def gdb_get_changed_registers(session_id: str) -> str:
    """Get registers that have changed since last stop."""
    return gdbTools.get_changed_registers(session_id)

@mcp.tool()
def gdb_read_memory_bytes(session_id: str, address: str, byte_count: int) -> str:
    """Read raw memory bytes from a specific address."""
    return gdbTools.read_memory_bytes(session_id, address, byte_count)

@mcp.tool()
def gdb_get_thread_info(session_id: str) -> str:
    """Get information about all threads."""
    return gdbTools.get_thread_info(session_id)

@mcp.tool()
def gdb_switch_thread(session_id: str, thread_id: str) -> str:
    """Switch to a different thread."""
    return gdbTools.switch_thread(session_id, thread_id)

@mcp.tool()
def gdb_get_breakpoint_list(session_id: str) -> str:
    """Get list of all breakpoints with detailed information."""
    return gdbTools.get_breakpoint_list(session_id)

@mcp.tool()
def gdb_delete_breakpoint(session_id: str, breakpoint_number: str) -> str:
    """Delete a specific breakpoint."""
    return gdbTools.delete_breakpoint(session_id, breakpoint_number)

@mcp.tool()
def gdb_enable_breakpoint(session_id: str, breakpoint_number: str) -> str:
    """Enable a specific breakpoint."""
    return gdbTools.enable_breakpoint(session_id, breakpoint_number)

@mcp.tool()
def gdb_disable_breakpoint(session_id: str, breakpoint_number: str) -> str:
    """Disable a specific breakpoint."""
    return gdbTools.disable_breakpoint(session_id, breakpoint_number)

@mcp.tool()
def gdb_set_watchpoint(session_id: str, expression: str, watch_type: str = "write") -> str:
    """Set a watchpoint on a variable or expression (write, read, or access)."""
    return gdbTools.set_watchpoint(session_id, expression, watch_type)

@mcp.tool()
def gdb_get_symbol_info(session_id: str, symbol_name: str) -> str:
    """Get information about a symbol."""
    return gdbTools.get_symbol_info(session_id, symbol_name)

@mcp.tool()
def gdb_list_source_files(session_id: str) -> str:
    """List all source files in the program."""
    return gdbTools.list_source_files(session_id)

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