"""GDB debugging tools and utilities."""

import logging
from pathlib import Path
from typing import List, Dict, Any
from .sessionManager import GDBSessionManager

logger = logging.getLogger(__name__)

def format_gdb_response(response: List[Dict[str, Any]]) -> str:
    """Format GDB response for better readability."""
    if not response:
        return "No response from GDB"
    
    formatted_lines = []
    for msg in response:
        msg_type = msg.get('type', 'unknown')
        payload = msg.get('payload', '')
        
        if msg_type == 'console':
            formatted_lines.append(f"Console: {payload}")
        elif msg_type == 'log':
            formatted_lines.append(f"Log: {payload}")
        elif msg_type == 'target':
            formatted_lines.append(f"Target: {payload}")
        elif msg_type == 'result':
            message = msg.get('message', '')
            if message == 'done':
                payload_str = str(payload) if payload else "Command completed successfully"
                formatted_lines.append(f"Result: {payload_str}")
            else:
                formatted_lines.append(f"Result ({message}): {payload}")
        else:
            formatted_lines.append(f"{msg_type.title()}: {payload}")
    
    return '\n'.join(formatted_lines) if formatted_lines else "Command executed"

class GDBTools:
    """Collection of GDB debugging tools."""
    
    def __init__(self, sessionManager: GDBSessionManager):
        self.sessionManager = sessionManager
    
    def start_session(self, gdb_path: str = "gdb") -> str:
        """Start a new GDB debugging session."""
        try:
            session_id = self.sessionManager.create_session(gdb_path)
            return f"GDB session started successfully. Session ID: {session_id}"
        except Exception as e:
            return f"Error starting GDB session: {str(e)}"
    
    def terminate_session(self, session_id: str) -> str:
        """Terminate a GDB debugging session."""
        try:
            if self.sessionManager.terminate_session(session_id):
                return f"GDB session '{session_id}' terminated successfully"
            else:
                return f"GDB session '{session_id}' not found"
        except Exception as e:
            return f"Error terminating session: {str(e)}"
    
    def list_sessions(self) -> str:
        """List all active GDB sessions."""
        sessions = self.sessionManager.list_sessions()
        if not sessions:
            return "No active GDB sessions"
        
        session_list = [f"- {session_id}" for session_id in sessions]
        return f"Active GDB sessions:\n" + "\n".join(session_list)
    
    def load_program(self, session_id: str, program_path: str) -> str:
        """Load a program into an existing GDB session."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            
            if not Path(program_path).exists():
                return f"Error: Program file '{program_path}' does not exist"
            
            response = gdb.write(f"file {program_path}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error loading program: {str(e)}"
    
    def execute_command(self, session_id: str, command: str) -> str:
        """Execute an arbitrary GDB command."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(command)
            return format_gdb_response(response)
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def attach_to_process(self, session_id: str, pid: int) -> str:
        """Attach GDB to a running process."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"attach {pid}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error attaching to process: {str(e)}"
    
    def load_core_dump(self, session_id: str, core_file: str) -> str:
        """Load a core dump file for analysis."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            
            if not Path(core_file).exists():
                return f"Error: Core file '{core_file}' does not exist"
            
            response = gdb.write(f"core {core_file}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error loading core dump: {str(e)}"
    
    def set_breakpoint(self, session_id: str, location: str) -> str:
        """Set a breakpoint at the specified location."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"break {location}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error setting breakpoint: {str(e)}"
    
    def continue_execution(self, session_id: str) -> str:
        """Continue program execution."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("continue")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error continuing execution: {str(e)}"
    
    def step_execution(self, session_id: str) -> str:
        """Step program execution (step into functions)."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("step")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error stepping execution: {str(e)}"
    
    def next_execution(self, session_id: str) -> str:
        """Step over function calls (next line)."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("next")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error stepping to next line: {str(e)}"
    
    def finish_function(self, session_id: str) -> str:
        """Execute until the current function returns."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("finish")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error finishing function: {str(e)}"
    
    def get_backtrace(self, session_id: str) -> str:
        """Show the call stack (backtrace)."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("backtrace")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting backtrace: {str(e)}"
    
    def print_expression(self, session_id: str, expression: str) -> str:
        """Print the value of an expression."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"print {expression}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error printing expression: {str(e)}"
    
    def examine_memory(self, session_id: str, address: str, format_spec: str = "x") -> str:
        """Examine memory at the specified address."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"x/{format_spec} {address}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error examining memory: {str(e)}"
    
    def get_registers(self, session_id: str) -> str:
        """Display processor registers."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("info registers")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting register info: {str(e)}"
    
    def disassemble_function(self, session_id: str, function_name: str, mixed_mode: bool = False) -> str:
        """Disassemble a function using GDB MI commands."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            # Use GDB MI command for better structured output
            mode = "1" if mixed_mode else "0"
            response = gdb.write(f"-data-disassemble -f {function_name} -- {mode}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error disassembling function: {str(e)}"
    
    def disassemble_address_range(self, session_id: str, start_addr: str, end_addr: str, mixed_mode: bool = False) -> str:
        """Disassemble a range of addresses."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            mode = "1" if mixed_mode else "0"
            response = gdb.write(f"-data-disassemble -s {start_addr} -e {end_addr} -- {mode}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error disassembling address range: {str(e)}"
    
    def disassemble_around_pc(self, session_id: str, instruction_count: int = 10, mixed_mode: bool = False) -> str:
        """Disassemble instructions around the current program counter."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            mode = "1" if mixed_mode else "0"
            # Disassemble around current PC
            response = gdb.write(f"-data-disassemble -s $pc -e \"$pc + {instruction_count * 4}\" -- {mode}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error disassembling around PC: {str(e)}"
    
    def get_local_variables(self, session_id: str, print_values: bool = True) -> str:
        """Get local variables in the current frame."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            # Use GDB MI command: 0=no values, 1=all values, 2=simple values
            values_flag = "1" if print_values else "0"
            response = gdb.write(f"-stack-list-locals {values_flag}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting local variables: {str(e)}"
    
    def get_function_arguments(self, session_id: str, print_values: bool = True) -> str:
        """Get function arguments for all stack frames."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            values_flag = "1" if print_values else "0"
            response = gdb.write(f"-stack-list-arguments {values_flag}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting function arguments: {str(e)}"
    
    def get_stack_frames(self, session_id: str, low_frame: int = None, high_frame: int = None) -> str:
        """Get detailed stack frame information."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            if low_frame is not None and high_frame is not None:
                response = gdb.write(f"-stack-list-frames {low_frame} {high_frame}")
            else:
                response = gdb.write("-stack-list-frames")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting stack frames: {str(e)}"
    
    def evaluate_expression(self, session_id: str, expression: str) -> str:
        """Evaluate an expression using GDB MI for structured output."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"-data-evaluate-expression \"{expression}\"")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"
    
    def get_register_names(self, session_id: str) -> str:
        """Get list of register names."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("-data-list-register-names")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting register names: {str(e)}"
    
    def get_register_values(self, session_id: str, register_numbers: list = None) -> str:
        """Get register values with structured output."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            if register_numbers:
                reg_list = " ".join(map(str, register_numbers))
                response = gdb.write(f"-data-list-register-values x {reg_list}")
            else:
                response = gdb.write("-data-list-register-values x")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting register values: {str(e)}"
    
    def get_changed_registers(self, session_id: str) -> str:
        """Get list of registers that have changed since last stop."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("-data-list-changed-registers")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting changed registers: {str(e)}"
    
    def read_memory_bytes(self, session_id: str, address: str, byte_count: int) -> str:
        """Read raw memory bytes."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"-data-read-memory-bytes {address} {byte_count}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error reading memory bytes: {str(e)}"
    
    def get_thread_info(self, session_id: str) -> str:
        """Get information about threads."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("-thread-info")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting thread info: {str(e)}"
    
    def switch_thread(self, session_id: str, thread_id: str) -> str:
        """Switch to a different thread."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"-thread-select {thread_id}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error switching thread: {str(e)}"
    
    def get_breakpoint_list(self, session_id: str) -> str:
        """Get list of all breakpoints."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("-break-list")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting breakpoint list: {str(e)}"
    
    def delete_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        """Delete a specific breakpoint."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"-break-delete {breakpoint_number}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error deleting breakpoint: {str(e)}"
    
    def enable_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        """Enable a specific breakpoint."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"-break-enable {breakpoint_number}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error enabling breakpoint: {str(e)}"
    
    def disable_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        """Disable a specific breakpoint."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"-break-disable {breakpoint_number}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error disabling breakpoint: {str(e)}"
    
    def set_watchpoint(self, session_id: str, expression: str, watch_type: str = "write") -> str:
        """Set a watchpoint on a variable or expression."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            if watch_type == "read":
                response = gdb.write(f"-break-watch -r {expression}")
            elif watch_type == "access":
                response = gdb.write(f"-break-watch -a {expression}")
            else:  # write
                response = gdb.write(f"-break-watch {expression}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error setting watchpoint: {str(e)}"
    
    def get_symbol_info(self, session_id: str, symbol_name: str) -> str:
        """Get information about a symbol."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write(f"-symbol-info-functions --name {symbol_name}")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error getting symbol info: {str(e)}"
    
    def list_source_files(self, session_id: str) -> str:
        """List all source files in the program."""
        try:
            gdb = self.sessionManager.get_session(session_id)
            response = gdb.write("-file-list-exec-source-files")
            return format_gdb_response(response)
        except Exception as e:
            return f"Error listing source files: {str(e)}"