"""GDB debugging tools and utilities."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Callable
from functools import wraps
from .sessionManager import GDBSessionManager

logger = logging.getLogger(__name__)

def handle_gdb_errors(operation: str) -> Callable:
    """Decorator to handle GDB operation errors consistently."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> str:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return f"Error {operation}: {str(e)}"
        return wrapper
    return decorator

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
    
    @handle_gdb_errors("starting GDB session")
    def start_session(self, gdb_path: str = "gdb") -> str:
        session_id = self.sessionManager.create_session(gdb_path)
        return f"GDB session started successfully. Session ID: {session_id}"
    
    @handle_gdb_errors("terminating session")
    def terminate_session(self, session_id: str) -> str:
        if self.sessionManager.terminate_session(session_id):
            return f"GDB session '{session_id}' terminated successfully"
        return f"GDB session '{session_id}' not found"
    
    def list_sessions(self) -> str:
        sessions = self.sessionManager.list_sessions()
        if not sessions:
            return "No active GDB sessions"
        return "Active GDB sessions:\n" + "\n".join(f"- {sid}" for sid in sessions)
    
    @handle_gdb_errors("loading program")
    def load_program(self, session_id: str, program_path: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        if not Path(program_path).exists():
            return f"Error: Program file '{program_path}' does not exist"
        response = gdb.write(f"file {program_path}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("executing command")
    def execute_command(self, session_id: str, command: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(command)
        return format_gdb_response(response)
    
    @handle_gdb_errors("attaching to process")
    def attach_to_process(self, session_id: str, pid: int) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"attach {pid}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("loading core dump")
    def load_core_dump(self, session_id: str, core_file: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        if not Path(core_file).exists():
            return f"Error: Core file '{core_file}' does not exist"
        response = gdb.write(f"core {core_file}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("setting breakpoint")
    def set_breakpoint(self, session_id: str, location: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"break {location}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("continuing execution")
    def continue_execution(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("continue")
        return format_gdb_response(response)
    
    @handle_gdb_errors("stepping execution")
    def step_execution(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("step")
        return format_gdb_response(response)
    
    @handle_gdb_errors("stepping to next line")
    def next_execution(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("next")
        return format_gdb_response(response)
    
    @handle_gdb_errors("finishing function")
    def finish_function(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("finish")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting backtrace")
    def get_backtrace(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("backtrace")
        return format_gdb_response(response)
    
    @handle_gdb_errors("printing expression")
    def print_expression(self, session_id: str, expression: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"print {expression}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("examining memory")
    def examine_memory(self, session_id: str, address: str, format_spec: str = "x") -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"x/{format_spec} {address}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting register info")
    def get_registers(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("info registers")
        return format_gdb_response(response)
    
    @handle_gdb_errors("disassembling function")
    def disassemble_function(self, session_id: str, function_name: str, mixed_mode: bool = False) -> str:
        gdb = self.sessionManager.get_session(session_id)
        mode = "1" if mixed_mode else "0"
        response = gdb.write(f"-data-disassemble -f {function_name} -- {mode}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("disassembling address range")
    def disassemble_address_range(self, session_id: str, start_addr: str, end_addr: str, mixed_mode: bool = False) -> str:
        gdb = self.sessionManager.get_session(session_id)
        mode = "1" if mixed_mode else "0"
        response = gdb.write(f"-data-disassemble -s {start_addr} -e {end_addr} -- {mode}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("disassembling around PC")
    def disassemble_around_pc(self, session_id: str, instruction_count: int = 10, mixed_mode: bool = False) -> str:
        gdb = self.sessionManager.get_session(session_id)
        mode = "1" if mixed_mode else "0"
        response = gdb.write(f"-data-disassemble -s $pc -e \"$pc + {instruction_count * 4}\" -- {mode}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting local variables")
    def get_local_variables(self, session_id: str, print_values: bool = True) -> str:
        gdb = self.sessionManager.get_session(session_id)
        values_flag = "1" if print_values else "0"
        response = gdb.write(f"-stack-list-locals {values_flag}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting function arguments")
    def get_function_arguments(self, session_id: str, print_values: bool = True) -> str:
        gdb = self.sessionManager.get_session(session_id)
        values_flag = "1" if print_values else "0"
        response = gdb.write(f"-stack-list-arguments {values_flag}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting stack frames")
    def get_stack_frames(self, session_id: str, low_frame: int = None, high_frame: int = None) -> str:
        gdb = self.sessionManager.get_session(session_id)
        if low_frame is not None and high_frame is not None:
            response = gdb.write(f"-stack-list-frames {low_frame} {high_frame}")
        else:
            response = gdb.write("-stack-list-frames")
        return format_gdb_response(response)
    
    @handle_gdb_errors("evaluating expression")
    def evaluate_expression(self, session_id: str, expression: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"-data-evaluate-expression \"{expression}\"")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting register names")
    def get_register_names(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("-data-list-register-names")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting register values")
    def get_register_values(self, session_id: str, register_numbers: list = None) -> str:
        gdb = self.sessionManager.get_session(session_id)
        if register_numbers:
            reg_list = " ".join(map(str, register_numbers))
            response = gdb.write(f"-data-list-register-values x {reg_list}")
        else:
            response = gdb.write("-data-list-register-values x")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting changed registers")
    def get_changed_registers(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("-data-list-changed-registers")
        return format_gdb_response(response)
    
    @handle_gdb_errors("reading memory bytes")
    def read_memory_bytes(self, session_id: str, address: str, byte_count: int) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"-data-read-memory-bytes {address} {byte_count}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting thread info")
    def get_thread_info(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("-thread-info")
        return format_gdb_response(response)
    
    @handle_gdb_errors("switching thread")
    def switch_thread(self, session_id: str, thread_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"-thread-select {thread_id}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting breakpoint list")
    def get_breakpoint_list(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("-break-list")
        return format_gdb_response(response)
    
    @handle_gdb_errors("deleting breakpoint")
    def delete_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"-break-delete {breakpoint_number}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("enabling breakpoint")
    def enable_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"-break-enable {breakpoint_number}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("disabling breakpoint")
    def disable_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"-break-disable {breakpoint_number}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("setting watchpoint")
    def set_watchpoint(self, session_id: str, expression: str, watch_type: str = "write") -> str:
        gdb = self.sessionManager.get_session(session_id)
        if watch_type == "read":
            response = gdb.write(f"-break-watch -r {expression}")
        elif watch_type == "access":
            response = gdb.write(f"-break-watch -a {expression}")
        else:
            response = gdb.write(f"-break-watch {expression}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("getting symbol info")
    def get_symbol_info(self, session_id: str, symbol_name: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write(f"-symbol-info-functions --name {symbol_name}")
        return format_gdb_response(response)
    
    @handle_gdb_errors("listing source files")
    def list_source_files(self, session_id: str) -> str:
        gdb = self.sessionManager.get_session(session_id)
        response = gdb.write("-file-list-exec-source-files")
        return format_gdb_response(response)