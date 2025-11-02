"""LLDB debugging tools and utilities."""

import logging
from pathlib import Path
from typing import Optional, Callable
from functools import wraps
from .sessionManager import LLDBSessionManager, is_lldb_available
from ..base.debuggerBase import DebuggerTools

logger = logging.getLogger(__name__)

def handle_lldb_errors(operation: str) -> Callable:
    """Decorator to handle LLDB operation errors consistently."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> str:
            try:
                if not is_lldb_available():
                    return f"Error {operation}: LLDB not available on this system"
                return func(*args, **kwargs)
            except Exception as e:
                return f"Error {operation}: {str(e)}"
        return wrapper
    return decorator

def format_lldb_error(error: 'lldb.SBError') -> str:
    """Format LLDB error for display."""
    if not error.Success():
        return f"LLDB Error: {error.GetCString()}"
    return "Success"

def format_lldb_response(result: str, error: Optional['lldb.SBError'] = None) -> str:
    """Format LLDB response for better readability."""
    if error and not error.Success():
        return f"Error: {error.GetCString()}"
    
    if not result:
        return "Command completed successfully"
    
    return result.strip()


class LLDBTools(DebuggerTools):
    """Collection of LLDB debugging tools."""
    
    def __init__(self, session_manager: LLDBSessionManager):
        super().__init__(session_manager)
        self.session_manager = session_manager
    
    @handle_lldb_errors("starting LLDB session")
    def start_session(self, debugger_path: Optional[str] = None) -> str:
        session_id = self.session_manager.create_session(debugger_path)
        return f"LLDB session started successfully. Session ID: {session_id}"
    
    @handle_lldb_errors("terminating session")
    def terminate_session(self, session_id: str) -> str:
        if self.session_manager.terminate_session(session_id):
            return f"LLDB session '{session_id}' terminated successfully"
        return f"LLDB session '{session_id}' not found"
    
    def list_sessions(self) -> str:
        sessions = self.session_manager.list_sessions()
        if not sessions:
            return "No active LLDB sessions"
        return "Active LLDB sessions:\n" + "\n".join(f"- {sid}" for sid in sessions)
    
    @handle_lldb_errors("loading program")
    def load_program(self, session_id: str, program_path: str) -> str:
        debugger = self.session_manager.get_session(session_id)
        
        if not Path(program_path).exists():
            return f"Error: Program file '{program_path}' does not exist"
        
        target = debugger.CreateTarget(program_path)
        if not target.IsValid():
            return f"Failed to create target for '{program_path}'"
        
        return f"Successfully loaded program: {program_path}"
    
    @handle_lldb_errors("executing command")
    def execute_command(self, session_id: str, command: str) -> str:
        lldb = _get_lldb()
        if not lldb:
            return "Error: LLDB not available"
            
        debugger = self.session_manager.get_session(session_id)
        
        # Get command interpreter
        interpreter = debugger.GetCommandInterpreter()
        result = lldb.SBCommandReturnObject()
        
        # Execute command
        interpreter.HandleCommand(command, result)
        
        if result.Succeeded():
            output = result.GetOutput() or result.GetError() or "Command executed"
            return format_lldb_response(output)
        else:
            error_msg = result.GetError() or "Command failed"
            return f"Error: {error_msg}"
    
    @handle_lldb_errors("attaching to process")
    def attach_to_process(self, session_id: str, pid: int) -> str:
        debugger = self.session_manager.get_session(session_id)
        
        target = debugger.CreateTarget("")
        if not target.IsValid():
            return "Failed to create target for attach"
        
        error = lldb.SBError()
        process = target.AttachToProcessWithID(debugger.GetListener(), pid, error)
        
        if error.Success() and process.IsValid():
            return f"Successfully attached to process {pid}"
        else:
            return f"Failed to attach to process {pid}: {format_lldb_error(error)}"
    
    @handle_lldb_errors("loading core dump")
    def load_core_dump(self, session_id: str, core_file: str) -> str:
        debugger = self.session_manager.get_session(session_id)
        
        if not Path(core_file).exists():
            return f"Error: Core file '{core_file}' does not exist"
        
        target = debugger.CreateTarget("")
        if not target.IsValid():
            return "Failed to create target for core dump"
        
        error = lldb.SBError()
        process = target.LoadCore(core_file, error)
        
        if error.Success() and process.IsValid():
            return f"Successfully loaded core dump: {core_file}"
        else:
            return f"Failed to load core dump: {format_lldb_error(error)}"
    
    @handle_lldb_errors("setting breakpoint")
    def set_breakpoint(self, session_id: str, location: str) -> str:
        debugger = self.session_manager.get_session(session_id)
        target = debugger.GetSelectedTarget()
        
        if not target.IsValid():
            return "No target available. Load a program first."
        
        # Try to set breakpoint by name first, then by location
        if location.isdigit() or location.startswith("0x"):
            # Address breakpoint
            try:
                addr = int(location, 0)  # Auto-detect base (hex/decimal)
                bp = target.BreakpointCreateByAddress(addr)
            except ValueError:
                bp = target.BreakpointCreateByName(location)
        else:
            # Function/symbol breakpoint
            bp = target.BreakpointCreateByName(location)
        
        if bp.IsValid():
            num_locations = bp.GetNumLocations()
            return f"Breakpoint set at {location} ({num_locations} location{'s' if num_locations != 1 else ''})"
        else:
            return f"Failed to set breakpoint at {location}"
    
    @handle_lldb_errors("continuing execution")
    def continue_execution(self, session_id: str) -> str:
        debugger = self.session_manager.get_session(session_id)
        target = debugger.GetSelectedTarget()
        
        if not target.IsValid():
            return "No target available"
        
        process = target.GetProcess()
        if not process.IsValid():
            return "No process available. Start or attach to a process first."
        
        error = process.Continue()
        if error.Success():
            state = process.GetState()
            return f"Process continued. State: {lldb.SBDebugger.StateAsCString(state)}"
        else:
            return f"Failed to continue: {format_lldb_error(error)}"
    
    @handle_lldb_errors("stepping execution")
    def step_execution(self, session_id: str) -> str:
        debugger = self.session_manager.get_session(session_id)
        target = debugger.GetSelectedTarget()
        
        if not target.IsValid():
            return "No target available"
        
        process = target.GetProcess()
        if not process.IsValid():
            return "No process available"
        
        thread = process.GetSelectedThread()
        if not thread.IsValid():
            return "No thread selected"
        
        thread.StepInto()
        state = process.GetState()
        return f"Step completed. State: {lldb.SBDebugger.StateAsCString(state)}"
    
    @handle_lldb_errors("stepping to next line")
    def next_execution(self, session_id: str) -> str:
        debugger = self.session_manager.get_session(session_id)
        target = debugger.GetSelectedTarget()
        
        if not target.IsValid():
            return "No target available"
        
        process = target.GetProcess()
        if not process.IsValid():
            return "No process available"
        
        thread = process.GetSelectedThread()
        if not thread.IsValid():
            return "No thread selected"
        
        thread.StepOver()
        state = process.GetState()
        return f"Next completed. State: {lldb.SBDebugger.StateAsCString(state)}"
    
    @handle_lldb_errors("finishing function")
    def finish_function(self, session_id: str) -> str:
        debugger = self.session_manager.get_session(session_id)
        target = debugger.GetSelectedTarget()
        
        if not target.IsValid():
            return "No target available"
        
        process = target.GetProcess()
        if not process.IsValid():
            return "No process available"
        
        thread = process.GetSelectedThread()
        if not thread.IsValid():
            return "No thread selected"
        
        thread.StepOut()
        state = process.GetState()
        return f"Finish completed. State: {lldb.SBDebugger.StateAsCString(state)}"
    
    @handle_lldb_errors("getting backtrace")
    def get_backtrace(self, session_id: str) -> str:
        debugger = self.session_manager.get_session(session_id)
        target = debugger.GetSelectedTarget()
        
        if not target.IsValid():
            return "No target available"
        
        process = target.GetProcess()
        if not process.IsValid():
            return "No process available"
        
        thread = process.GetSelectedThread()
        if not thread.IsValid():
            return "No thread selected"
        
        backtrace_lines = []
        for i in range(thread.GetNumFrames()):
            frame = thread.GetFrameAtIndex(i)
            if frame.IsValid():
                func_name = frame.GetFunctionName() or "<unknown>"
                file_spec = frame.GetLineEntry().GetFileSpec()
                filename = file_spec.GetFilename() or "<unknown>"
                line_num = frame.GetLineEntry().GetLine()
                
                backtrace_lines.append(f"#{i}: {func_name} at {filename}:{line_num}")
        
        return "\n".join(backtrace_lines) if backtrace_lines else "No backtrace available"
    
    @handle_lldb_errors("printing expression")
    def print_expression(self, session_id: str, expression: str) -> str:
        debugger = self.session_manager.get_session(session_id)
        target = debugger.GetSelectedTarget()
        
        if not target.IsValid():
            return "No target available"
        
        process = target.GetProcess()
        if not process.IsValid():
            return "No process available"
        
        thread = process.GetSelectedThread()
        if not thread.IsValid():
            return "No thread selected"
        
        frame = thread.GetSelectedFrame()
        if not frame.IsValid():
            return "No frame selected"
        
        # Evaluate expression
        value = frame.EvaluateExpression(expression)
        if value.IsValid():
            return f"{expression} = {value.GetValue() or value.GetSummary() or 'N/A'}"
        else:
            error = value.GetError()
            return f"Failed to evaluate '{expression}': {error.GetCString() if error else 'Unknown error'}"
    
    @handle_lldb_errors("examining memory")
    def examine_memory(self, session_id: str, address: str, format_spec: str = "x") -> str:
        debugger = self.session_manager.get_session(session_id)
        target = debugger.GetSelectedTarget()
        
        if not target.IsValid():
            return "No target available"
        
        process = target.GetProcess()
        if not process.IsValid():
            return "No process available"
        
        # Parse address
        try:
            if address.startswith("&"):
                # Variable address - evaluate it
                thread = process.GetSelectedThread()
                frame = thread.GetSelectedFrame()
                addr_value = frame.EvaluateExpression(address)
                if not addr_value.IsValid():
                    return f"Failed to evaluate address: {address}"
                addr = addr_value.GetValueAsUnsigned()
            else:
                addr = int(address, 0)  # Auto-detect base
        except ValueError:
            return f"Invalid address format: {address}"
        
        # Read memory (default 16 bytes)
        error = lldb.SBError()
        memory_data = process.ReadMemory(addr, 16, error)
        
        if error.Success() and memory_data:
            # Format as hex dump
            hex_bytes = " ".join(f"{b:02x}" for b in memory_data)
            return f"0x{addr:x}: {hex_bytes}"
        else:
            return f"Failed to read memory at {address}: {format_lldb_error(error)}"
    
    @handle_lldb_errors("getting register info")
    def get_registers(self, session_id: str) -> str:
        debugger = self.session_manager.get_session(session_id)
        target = debugger.GetSelectedTarget()
        
        if not target.IsValid():
            return "No target available"
        
        process = target.GetProcess()
        if not process.IsValid():
            return "No process available"
        
        thread = process.GetSelectedThread()
        if not thread.IsValid():
            return "No thread selected"
        
        frame = thread.GetSelectedFrame()
        if not frame.IsValid():
            return "No frame selected"
        
        # Get register context
        registers = frame.GetRegisters()
        reg_lines = []
        
        for reg_set_idx in range(registers.GetSize()):
            reg_set = registers.GetValueAtIndex(reg_set_idx)
            reg_set_name = reg_set.GetName()
            reg_lines.append(f"[{reg_set_name}]")
            
            for reg_idx in range(reg_set.GetNumChildren()):
                reg = reg_set.GetChildAtIndex(reg_idx)
                name = reg.GetName()
                value = reg.GetValue()
                reg_lines.append(f"  {name}: {value}")
        
        return "\n".join(reg_lines) if reg_lines else "No registers available"
    
    # Disassembly methods
    @handle_lldb_errors("disassembling function")
    def disassemble_function(self, session_id: str, function_name: str, mixed_mode: bool = False) -> str:
        return self.execute_command(session_id, f"disassemble --name {function_name}")
    
    @handle_lldb_errors("disassembling address range")
    def disassemble_address_range(self, session_id: str, start_addr: str, end_addr: str, mixed_mode: bool = False) -> str:
        return self.execute_command(session_id, f"disassemble --start-address {start_addr} --end-address {end_addr}")
    
    @handle_lldb_errors("disassembling around PC")
    def disassemble_around_pc(self, session_id: str, instruction_count: int = 10, mixed_mode: bool = False) -> str:
        return self.execute_command(session_id, f"disassemble --pc --count {instruction_count}")
    
    # Variable and stack analysis
    @handle_lldb_errors("getting local variables")
    def get_local_variables(self, session_id: str, print_values: bool = True) -> str:
        return self.execute_command(session_id, "frame variable" if print_values else "frame variable --no-values")
    
    @handle_lldb_errors("getting function arguments")
    def get_function_arguments(self, session_id: str, print_values: bool = True) -> str:
        return self.execute_command(session_id, "frame variable --no-locals" if print_values else "frame variable --no-locals --no-values")
    
    @handle_lldb_errors("getting stack frames")
    def get_stack_frames(self, session_id: str, low_frame: Optional[int] = None, high_frame: Optional[int] = None) -> str:
        if low_frame is not None and high_frame is not None:
            return self.execute_command(session_id, f"thread backtrace --count {high_frame - low_frame + 1}")
        return self.execute_command(session_id, "thread backtrace")
    
    @handle_lldb_errors("evaluating expression")
    def evaluate_expression(self, session_id: str, expression: str) -> str:
        return self.print_expression(session_id, expression)  # Same as print for LLDB
    
    # Register methods
    @handle_lldb_errors("getting register names")
    def get_register_names(self, session_id: str) -> str:
        return self.execute_command(session_id, "register read --all")
    
    @handle_lldb_errors("getting register values")
    def get_register_values(self, session_id: str, register_numbers: Optional[list] = None) -> str:
        if register_numbers:
            reg_names = " ".join(str(r) for r in register_numbers)
            return self.execute_command(session_id, f"register read {reg_names}")
        return self.execute_command(session_id, "register read")
    
    @handle_lldb_errors("getting changed registers")
    def get_changed_registers(self, session_id: str) -> str:
        # LLDB doesn't have direct equivalent, return all registers
        return self.execute_command(session_id, "register read")
    
    @handle_lldb_errors("reading memory bytes")
    def read_memory_bytes(self, session_id: str, address: str, byte_count: int) -> str:
        return self.execute_command(session_id, f"memory read --size {byte_count} --format bytes {address}")
    
    # Thread management
    @handle_lldb_errors("getting thread info")
    def get_thread_info(self, session_id: str) -> str:
        return self.execute_command(session_id, "thread list")
    
    @handle_lldb_errors("switching thread")
    def switch_thread(self, session_id: str, thread_id: str) -> str:
        return self.execute_command(session_id, f"thread select {thread_id}")
    
    # Breakpoint management
    @handle_lldb_errors("getting breakpoint list")
    def get_breakpoint_list(self, session_id: str) -> str:
        return self.execute_command(session_id, "breakpoint list")
    
    @handle_lldb_errors("deleting breakpoint")
    def delete_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        return self.execute_command(session_id, f"breakpoint delete {breakpoint_number}")
    
    @handle_lldb_errors("enabling breakpoint")
    def enable_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        return self.execute_command(session_id, f"breakpoint enable {breakpoint_number}")
    
    @handle_lldb_errors("disabling breakpoint")
    def disable_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        return self.execute_command(session_id, f"breakpoint disable {breakpoint_number}")
    
    @handle_lldb_errors("setting watchpoint")
    def set_watchpoint(self, session_id: str, expression: str, watch_type: str = "write") -> str:
        if watch_type == "read":
            return self.execute_command(session_id, f"watchpoint set expression -w read -- {expression}")
        elif watch_type == "access":
            return self.execute_command(session_id, f"watchpoint set expression -w read_write -- {expression}")
        else:  # write
            return self.execute_command(session_id, f"watchpoint set expression -w write -- {expression}")
    
    # Symbol and source analysis
    @handle_lldb_errors("getting symbol info")
    def get_symbol_info(self, session_id: str, symbol_name: str) -> str:
        return self.execute_command(session_id, f"image lookup --name {symbol_name}")
    
    @handle_lldb_errors("listing source files")
    def list_source_files(self, session_id: str) -> str:
        return self.execute_command(session_id, "target modules dump symtab")
    
    @staticmethod
    def is_available() -> bool:
        """Check if LLDB is available on this system."""
        return is_lldb_available()

def _get_lldb():
    """Get LLDB module if available."""
    if is_lldb_available():
        from .sessionManager import lldb
        return lldb
    return None
