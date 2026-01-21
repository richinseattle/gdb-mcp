"""Abstract base classes for debugger implementations."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class DebuggerSessionManager(ABC):
    """Abstract base class for managing debugger sessions."""
    
    @abstractmethod
    def create_session(self, debugger_path: str = None) -> str:
        """Create a new debugger session and return its ID."""
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Any:
        """Get a debugger session by ID."""
        pass
    
    @abstractmethod
    def terminate_session(self, session_id: str) -> bool:
        """Terminate a debugger session."""
        pass
    
    @abstractmethod
    def list_sessions(self) -> list:
        """List all active session IDs."""
        pass
    
    @abstractmethod
    def has_session(self, session_id: str) -> bool:
        """Check if a session exists."""
        pass


class DebuggerTools(ABC):
    """Abstract base class for debugger tool implementations."""
    
    def __init__(self, session_manager: DebuggerSessionManager):
        self.session_manager = session_manager
    
    @abstractmethod
    def start_session(self, debugger_path: str = None) -> str:
        """Start a new debugging session."""
        pass
    
    @abstractmethod
    def terminate_session(self, session_id: str) -> str:
        """Terminate a debugging session."""
        pass
    
    @abstractmethod
    def list_sessions(self) -> str:
        """List all active debugging sessions."""
        pass
    
    @abstractmethod
    def load_program(self, session_id: str, program_path: str) -> str:
        """Load a program into the debugger."""
        pass
    
    @abstractmethod
    def execute_command(self, session_id: str, command: str) -> str:
        """Execute an arbitrary debugger command."""
        pass
    
    @abstractmethod
    def attach_to_process(self, session_id: str, pid: int) -> str:
        """Attach debugger to a running process."""
        pass
    
    @abstractmethod
    def load_core_dump(self, session_id: str, core_file: str) -> str:
        """Load a core dump file for analysis."""
        pass
    
    @abstractmethod
    def set_breakpoint(self, session_id: str, location: str) -> str:
        """Set a breakpoint at the specified location."""
        pass
    
    @abstractmethod
    def continue_execution(self, session_id: str) -> str:
        """Continue program execution."""
        pass
    
    @abstractmethod
    def step_execution(self, session_id: str) -> str:
        """Step into functions."""
        pass
    
    @abstractmethod
    def next_execution(self, session_id: str) -> str:
        """Step over function calls."""
        pass
    
    @abstractmethod
    def finish_function(self, session_id: str) -> str:
        """Execute until the current function returns."""
        pass
    
    @abstractmethod
    def get_backtrace(self, session_id: str) -> str:
        """Show the call stack."""
        pass
    
    @abstractmethod
    def print_expression(self, session_id: str, expression: str) -> str:
        """Print the value of an expression."""
        pass
    
    @abstractmethod
    def examine_memory(self, session_id: str, address: str, format_spec: str = "x") -> str:
        """Examine memory at the specified address."""
        pass
    
    @abstractmethod
    def get_registers(self, session_id: str) -> str:
        """Display processor registers."""
        pass
    
    @abstractmethod
    def disassemble_function(self, session_id: str, function_name: str, mixed_mode: bool = False) -> str:
        """Disassemble a function."""
        pass
    
    @abstractmethod
    def disassemble_address_range(self, session_id: str, start_addr: str, end_addr: str, mixed_mode: bool = False) -> str:
        """Disassemble a range of memory addresses."""
        pass
    
    @abstractmethod
    def disassemble_around_pc(self, session_id: str, instruction_count: int = 10, mixed_mode: bool = False) -> str:
        """Disassemble instructions around the current program counter."""
        pass
    
    @abstractmethod
    def get_local_variables(self, session_id: str, print_values: bool = True) -> str:
        """Get local variables in the current stack frame."""
        pass
    
    @abstractmethod
    def get_function_arguments(self, session_id: str, print_values: bool = True) -> str:
        """Get function arguments for all stack frames."""
        pass
    
    @abstractmethod
    def get_stack_frames(self, session_id: str, low_frame: Optional[int] = None, high_frame: Optional[int] = None) -> str:
        """Get detailed stack frame information."""
        pass
    
    @abstractmethod
    def evaluate_expression(self, session_id: str, expression: str) -> str:
        """Evaluate an expression with structured output."""
        pass
    
    @abstractmethod
    def get_register_names(self, session_id: str) -> str:
        """Get list of all register names."""
        pass
    
    @abstractmethod
    def get_register_values(self, session_id: str, register_numbers: Optional[list] = None) -> str:
        """Get register values with structured output."""
        pass
    
    @abstractmethod
    def get_changed_registers(self, session_id: str) -> str:
        """Get registers that have changed since last stop."""
        pass
    
    @abstractmethod
    def read_memory_bytes(self, session_id: str, address: str, byte_count: int) -> str:
        """Read raw memory bytes from a specific address."""
        pass
    
    @abstractmethod
    def get_thread_info(self, session_id: str) -> str:
        """Get information about all threads."""
        pass
    
    @abstractmethod
    def switch_thread(self, session_id: str, thread_id: str) -> str:
        """Switch to a different thread."""
        pass
    
    @abstractmethod
    def get_breakpoint_list(self, session_id: str) -> str:
        """Get list of all breakpoints with detailed information."""
        pass
    
    @abstractmethod
    def delete_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        """Delete a specific breakpoint."""
        pass
    
    @abstractmethod
    def enable_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        """Enable a specific breakpoint."""
        pass
    
    @abstractmethod
    def disable_breakpoint(self, session_id: str, breakpoint_number: str) -> str:
        """Disable a specific breakpoint."""
        pass
    
    @abstractmethod
    def set_watchpoint(self, session_id: str, expression: str, watch_type: str = "write") -> str:
        """Set a watchpoint on a variable or expression."""
        pass
    
    @abstractmethod
    def get_symbol_info(self, session_id: str, symbol_name: str) -> str:
        """Get information about a symbol."""
        pass
    
    @abstractmethod
    def list_source_files(self, session_id: str) -> str:
        """List all source files in the program."""
        pass
