"""Debugger factory for creating appropriate debugger instances."""

import logging
from typing import Optional, Tuple
from .base.debuggerBase import DebuggerSessionManager, DebuggerTools
from .gdb import GDBSessionManager, GDBTools
from .lldb import LLDBSessionManager, LLDBTools

logger = logging.getLogger(__name__)

class DebuggerFactory:
    """Factory for creating debugger session managers and tools."""
    
    @staticmethod
    def get_available_debuggers() -> dict:
        """Get information about available debuggers."""
        return {
            'gdb': {
                'available': GDBSessionManager.is_available(),
                'name': 'GNU Debugger (GDB)',
                'description': 'Traditional Unix debugger'
            },
            'lldb': {
                'available': LLDBSessionManager.is_available(),
                'name': 'LLVM Debugger (LLDB)', 
                'description': 'Modern LLVM-based debugger (macOS native)'
            }
        }
    
    @staticmethod
    def create_session_manager(debugger_type: Optional[str] = None) -> Tuple[DebuggerSessionManager, str]:
        """
        Create a debugger session manager.
        
        Args:
            debugger_type: 'gdb', 'lldb', or None for auto-detection
            
        Returns:
            Tuple of (session_manager, actual_debugger_type)
            
        Raises:
            RuntimeError: If no debuggers are available or specified type unavailable
        """
        available = DebuggerFactory.get_available_debuggers()
        
        # If specific type requested, try to use it
        if debugger_type:
            debugger_type = debugger_type.lower()
            if debugger_type not in available:
                raise ValueError(f"Unknown debugger type: {debugger_type}")
            
            if not available[debugger_type]['available']:
                raise RuntimeError(f"{available[debugger_type]['name']} is not available on this system")
            
            if debugger_type == 'gdb':
                return GDBSessionManager(), 'gdb'
            elif debugger_type == 'lldb':
                return LLDBSessionManager(), 'lldb'
        
        # Auto-detection: prefer LLDB on macOS, GDB elsewhere
        import platform
        if platform.system() == 'Darwin':  # macOS
            if available['lldb']['available']:
                logger.info("Auto-selected LLDB (native macOS debugger)")
                return LLDBSessionManager(), 'lldb'
            elif available['gdb']['available']:
                logger.info("Auto-selected GDB (LLDB not available)")
                return GDBSessionManager(), 'gdb'
        else:
            if available['gdb']['available']:
                logger.info("Auto-selected GDB")
                return GDBSessionManager(), 'gdb'
            elif available['lldb']['available']:
                logger.info("Auto-selected LLDB")
                return LLDBSessionManager(), 'lldb'
        
        # No debuggers available
        available_names = [info['name'] for info in available.values() if info['available']]
        if not available_names:
            raise RuntimeError("No debuggers are available. Please install GDB or LLDB.")
        
        raise RuntimeError("Internal error: debuggers available but none selected")
    
    @staticmethod
    def create_tools(debugger_type: Optional[str] = None) -> Tuple[DebuggerTools, str]:
        """
        Create debugger tools.
        
        Args:
            debugger_type: 'gdb', 'lldb', or None for auto-detection
            
        Returns:
            Tuple of (tools, actual_debugger_type)
        """
        session_manager, actual_type = DebuggerFactory.create_session_manager(debugger_type)
        
        if actual_type == 'gdb':
            return GDBTools(session_manager), 'gdb'
        elif actual_type == 'lldb':
            return LLDBTools(session_manager), 'lldb'
        
        raise RuntimeError(f"Unknown debugger type: {actual_type}")
    
    @staticmethod
    def list_debuggers() -> str:
        """Get a formatted list of available debuggers."""
        available = DebuggerFactory.get_available_debuggers()
        
        lines = ["Available debuggers:"]
        for debugger_type, info in available.items():
            status = "✓ Available" if info['available'] else "✗ Not available"
            lines.append(f"  • {debugger_type.upper()}: {info['name']} - {status}")
            if info['description']:
                lines.append(f"    {info['description']}")
        
        return "\n".join(lines)
