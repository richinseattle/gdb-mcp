#!/usr/bin/env python3
"""
GDB MCP Server

A Model Context Protocol server that provides GDB debugging functionality
for use with Claude Desktop, VSCode Copilot, or other AI assistants.
"""

import logging
from mcp.server.fastmcp import FastMCP
from modules.sessionManager import GDBSessionManager
from modules.gdbTools import GDBTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session manager and tools
sessionManager = GDBSessionManager()
gdbTools = GDBTools(sessionManager)

# Create the MCP server
mcp = FastMCP("GDB Debugger")

# Session Management Tools
@mcp.tool()
def gdb_start(gdb_path: str = "gdb") -> str:
    """
    Start a new GDB debugging session.
    """
    return gdbTools.start_session(gdb_path)

@mcp.tool()
def gdb_terminate(session_id: str) -> str:
    """
    Terminate a GDB debugging session.
    """
    return gdbTools.terminate_session(session_id)

@mcp.tool()
def gdb_list_sessions() -> str:
    """
    List all active GDB sessions.
    """
    return gdbTools.list_sessions()

# Program Loading Tools
@mcp.tool()
def gdb_load(session_id: str, program_path: str) -> str:
    """
    Load a program into an existing GDB session.
    """
    return gdbTools.load_program(session_id, program_path)

@mcp.tool()
def gdb_attach(session_id: str, pid: int) -> str:
    """
    Attach GDB to a running process.
    """
    return gdbTools.attach_to_process(session_id, pid)

@mcp.tool()
def gdb_load_core(session_id: str, core_file: str) -> str:
    """
    Load a core dump file for analysis.
    """
    return gdbTools.load_core_dump(session_id, core_file)

# Execution Control Tools
@mcp.tool()
def gdb_continue(session_id: str) -> str:
    """
    Continue program execution.
    """
    return gdbTools.continue_execution(session_id)

@mcp.tool()
def gdb_step(session_id: str) -> str:
    """
    Step program execution (step into functions).
    """
    return gdbTools.step_execution(session_id)

@mcp.tool()
def gdb_next(session_id: str) -> str:
    """
    Step over function calls (next line).
    """
    return gdbTools.next_execution(session_id)

@mcp.tool()
def gdb_finish(session_id: str) -> str:
    """
    Execute until the current function returns.
    """
    return gdbTools.finish_function(session_id)

# Debugging Tools
@mcp.tool()
def gdb_set_breakpoint(session_id: str, location: str) -> str:
    """
    Set a breakpoint at the specified location.
    """
    return gdbTools.set_breakpoint(session_id, location)

@mcp.tool()
def gdb_backtrace(session_id: str) -> str:
    """
    Show the call stack (backtrace).
    """
    return gdbTools.get_backtrace(session_id)

@mcp.tool()
def gdb_print(session_id: str, expression: str) -> str:
    """
    Print the value of an expression.
    """
    return gdbTools.print_expression(session_id, expression)

@mcp.tool()
def gdb_examine(session_id: str, address: str, format_spec: str = "x") -> str:
    """
    Examine memory at the specified address.
    """
    return gdbTools.examine_memory(session_id, address, format_spec)

@mcp.tool()
def gdb_info_registers(session_id: str) -> str:
    """
    Display processor registers.
    """
    return gdbTools.get_registers(session_id)

@mcp.tool()
def gdb_command(session_id: str, command: str) -> str:
    """
    Execute an arbitrary GDB command.
    
    Args:
        session_id: The GDB session ID
        command: The GDB command to execute
    
    Returns:
        Output from the GDB command
    """
    return gdbTools.execute_command(session_id, command)

@mcp.tool()
def gdb_disassemble_function(session_id: str, function_name: str, mixed_mode: bool = False) -> str:
    """
    Disassemble a function with optional source code mixing.
    
    Args:
        session_id: The GDB session ID
        function_name: Name of the function to disassemble
        mixed_mode: If True, mix source code with assembly
    
    Returns:
        Disassembly of the function
    """
    return gdbTools.disassemble_function(session_id, function_name, mixed_mode)

@mcp.tool()
def gdb_disassemble_address_range(session_id: str, start_addr: str, end_addr: str, mixed_mode: bool = False) -> str:
    """
    Disassemble a range of memory addresses.
    
    Args:
        session_id: The GDB session ID
        start_addr: Starting address (e.g., "0x400000")
        end_addr: Ending address (e.g., "0x400100")
        mixed_mode: If True, mix source code with assembly
    
    Returns:
        Disassembly of the address range
    """
    return gdbTools.disassemble_address_range(session_id, start_addr, end_addr, mixed_mode)

@mcp.tool()
def gdb_disassemble_around_pc(session_id: str, instruction_count: int = 10, mixed_mode: bool = False) -> str:
    """
    Disassemble instructions around the current program counter.
    
    Args:
        session_id: The GDB session ID
        instruction_count: Number of instructions to disassemble
        mixed_mode: If True, mix source code with assembly
    
    Returns:
        Disassembly around current PC
    """
    return gdbTools.disassemble_around_pc(session_id, instruction_count, mixed_mode)

@mcp.tool()
def gdb_get_local_variables(session_id: str, print_values: bool = True) -> str:
    """
    Get local variables in the current stack frame.
    
    Args:
        session_id: The GDB session ID
        print_values: If True, include variable values
    
    Returns:
        Local variables information
    """
    return gdbTools.get_local_variables(session_id, print_values)

@mcp.tool()
def gdb_get_function_arguments(session_id: str, print_values: bool = True) -> str:
    """
    Get function arguments for all stack frames.
    
    Args:
        session_id: The GDB session ID
        print_values: If True, include argument values
    
    Returns:
        Function arguments information
    """
    return gdbTools.get_function_arguments(session_id, print_values)

@mcp.tool()
def gdb_get_stack_frames(session_id: str, low_frame: int = None, high_frame: int = None) -> str:
    """
    Get detailed stack frame information.
    
    Args:
        session_id: The GDB session ID
        low_frame: Starting frame number (optional)
        high_frame: Ending frame number (optional)
    
    Returns:
        Detailed stack frame information
    """
    return gdbTools.get_stack_frames(session_id, low_frame, high_frame)

@mcp.tool()
def gdb_evaluate_expression(session_id: str, expression: str) -> str:
    """
    Evaluate an expression with structured output.
    
    Args:
        session_id: The GDB session ID
        expression: Expression to evaluate
    
    Returns:
        Evaluation result
    """
    return gdbTools.evaluate_expression(session_id, expression)

@mcp.tool()
def gdb_get_register_names(session_id: str) -> str:
    """
    Get list of all register names.
    
    Args:
        session_id: The GDB session ID
    
    Returns:
        List of register names
    """
    return gdbTools.get_register_names(session_id)

@mcp.tool()
def gdb_get_register_values(session_id: str, register_numbers: list = None) -> str:
    """
    Get register values with structured output.
    
    Args:
        session_id: The GDB session ID
        register_numbers: List of register numbers (optional)
    
    Returns:
        Register values
    """
    return gdbTools.get_register_values(session_id, register_numbers)

@mcp.tool()
def gdb_get_changed_registers(session_id: str) -> str:
    """
    Get registers that have changed since last stop.
    
    Args:
        session_id: The GDB session ID
    
    Returns:
        List of changed registers
    """
    return gdbTools.get_changed_registers(session_id)

@mcp.tool()
def gdb_read_memory_bytes(session_id: str, address: str, byte_count: int) -> str:
    """
    Read raw memory bytes from a specific address.
    
    Args:
        session_id: The GDB session ID
        address: Memory address to read from
        byte_count: Number of bytes to read
    
    Returns:
        Raw memory data
    """
    return gdbTools.read_memory_bytes(session_id, address, byte_count)

@mcp.tool()
def gdb_get_thread_info(session_id: str) -> str:
    """
    Get information about all threads.
    
    Args:
        session_id: The GDB session ID
    
    Returns:
        Thread information
    """
    return gdbTools.get_thread_info(session_id)

@mcp.tool()
def gdb_switch_thread(session_id: str, thread_id: str) -> str:
    """
    Switch to a different thread.
    
    Args:
        session_id: The GDB session ID
        thread_id: ID of the thread to switch to
    
    Returns:
        Result of thread switch
    """
    return gdbTools.switch_thread(session_id, thread_id)

@mcp.tool()
def gdb_get_breakpoint_list(session_id: str) -> str:
    """
    Get list of all breakpoints with detailed information.
    
    Args:
        session_id: The GDB session ID
    
    Returns:
        Detailed breakpoint list
    """
    return gdbTools.get_breakpoint_list(session_id)

@mcp.tool()
def gdb_delete_breakpoint(session_id: str, breakpoint_number: str) -> str:
    """
    Delete a specific breakpoint.
    
    Args:
        session_id: The GDB session ID
        breakpoint_number: Number of the breakpoint to delete
    
    Returns:
        Result of breakpoint deletion
    """
    return gdbTools.delete_breakpoint(session_id, breakpoint_number)

@mcp.tool()
def gdb_enable_breakpoint(session_id: str, breakpoint_number: str) -> str:
    """
    Enable a specific breakpoint.
    
    Args:
        session_id: The GDB session ID
        breakpoint_number: Number of the breakpoint to enable
    
    Returns:
        Result of breakpoint enabling
    """
    return gdbTools.enable_breakpoint(session_id, breakpoint_number)

@mcp.tool()
def gdb_disable_breakpoint(session_id: str, breakpoint_number: str) -> str:
    """
    Disable a specific breakpoint.
    
    Args:
        session_id: The GDB session ID
        breakpoint_number: Number of the breakpoint to disable
    
    Returns:
        Result of breakpoint disabling
    """
    return gdbTools.disable_breakpoint(session_id, breakpoint_number)

@mcp.tool()
def gdb_set_watchpoint(session_id: str, expression: str, watch_type: str = "write") -> str:
    """
    Set a watchpoint on a variable or expression.
    
    Args:
        session_id: The GDB session ID
        expression: Variable or expression to watch
        watch_type: Type of watchpoint ("write", "read", "access")
    
    Returns:
        Result of watchpoint creation
    """
    return gdbTools.set_watchpoint(session_id, expression, watch_type)

@mcp.tool()
def gdb_get_symbol_info(session_id: str, symbol_name: str) -> str:
    """
    Get information about a symbol.
    
    Args:
        session_id: The GDB session ID
        symbol_name: Name of the symbol to analyze
    
    Returns:
        Symbol information
    """
    return gdbTools.get_symbol_info(session_id, symbol_name)

@mcp.tool()
def gdb_list_source_files(session_id: str) -> str:
    """
    List all source files in the program.
    
    Args:
        session_id: The GDB session ID
    
    Returns:
        List of source files
    """
    return gdbTools.list_source_files(session_id)

# Resources
@mcp.resource("gdb://sessions")
def list_gdb_sessions() -> str:
    """Resource that provides information about active GDB sessions."""
    sessions = sessionManager.list_sessions()
    if not sessions:
        return "No active GDB sessions"
    
    session_info = [f"Session ID: {session_id}" for session_id in sessions]
    return "Active GDB Sessions:\n" + "\n".join(session_info)

@mcp.resource("gdb://help")
def gdb_help() -> str:
    """Resource that provides help information about available GDB tools."""
    help_text = """
# GDB MCP Server Help

This server provides the following GDB debugging tools:

## Session Management
- **gdb_start**: Start a new GDB debugging session
- **gdb_terminate**: Terminate a GDB session
- **gdb_list_sessions**: List all active GDB sessions

## Program Loading
- **gdb_load**: Load a program into GDB
- **gdb_attach**: Attach to a running process
- **gdb_load_core**: Load a core dump file

## Execution Control
- **gdb_continue**: Continue program execution
- **gdb_step**: Step into functions
- **gdb_next**: Step over function calls
- **gdb_finish**: Execute until current function returns

## Debugging
- **gdb_set_breakpoint**: Set breakpoints
- **gdb_backtrace**: Show call stack
- **gdb_print**: Print expression values
- **gdb_examine**: Examine memory
- **gdb_info_registers**: Display registers

## General
- **gdb_command**: Execute arbitrary GDB commands

## Advanced Disassembly
- **gdb_disassemble_function**: Disassemble a function
- **gdb_disassemble_address_range**: Disassemble a range of memory addresses
- **gdb_disassemble_around_pc**: Disassemble instructions around the current program counter

## Variable and Stack Analysis
- **gdb_get_local_variables**: Get local variables in the current stack frame
- **gdb_get_function_arguments**: Get function arguments for all stack frames
- **gdb_get_stack_frames**: Get detailed stack frame information
- **gdb_evaluate_expression**: Evaluate an expression with structured output

## Advanced Register Tools
- **gdb_get_register_names**: Get list of all register names
- **gdb_get_register_values**: Get register values with structured output
- **gdb_get_changed_registers**: Get registers that have changed since last stop

## Memory Analysis
- **gdb_read_memory_bytes**: Read raw memory bytes from a specific address

## Thread Management
- **gdb_get_thread_info**: Get information about all threads
- **gdb_switch_thread**: Switch to a different thread

## Advanced Breakpoint Management
- **gdb_get_breakpoint_list**: Get list of all breakpoints with detailed information
- **gdb_delete_breakpoint**: Delete a specific breakpoint
- **gdb_enable_breakpoint**: Enable a specific breakpoint
- **gdb_disable_breakpoint**: Disable a specific breakpoint
- **gdb_set_watchpoint**: Set a watchpoint on a variable or expression

## Symbol and Source Analysis
- **gdb_get_symbol_info**: Get information about a symbol
- **gdb_list_source_files**: List all source files in the program

## Usage Example
1. Start a session: `gdb_start()`
2. Load a program: `gdb_load(session_id, "/path/to/program")`
3. Set breakpoint: `gdb_set_breakpoint(session_id, "main")`
4. Run program: `gdb_command(session_id, "run")`
5. Continue debugging with other tools...
"""
    return help_text

if __name__ == "__main__":
    mcp.run()