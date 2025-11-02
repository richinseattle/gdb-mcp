"""LLDB session management module."""

import logging
import uuid
from typing import Dict, Optional, Any
from ..base.debuggerBase import DebuggerSessionManager

logger = logging.getLogger(__name__)

def _get_lldb_python_path():
    """Get LLDB Python path using lldb -P command."""
    import subprocess
    import os
    
    try:
        # Use lldb -P to get the correct Python path
        result = subprocess.run(['lldb', '-P'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            path = result.stdout.strip()
            if os.path.exists(path):
                return path
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    return None

# Setup LLDB path but don't import yet (lazy loading)
_lldb_path_setup = False
lldb = None

def _setup_lldb_import():
    """Setup LLDB import path and try to import."""
    global _lldb_path_setup, lldb
    
    if _lldb_path_setup:
        return lldb is not None
    
    _lldb_path_setup = True
    
    try:
        import sys
        import os
        
        # Get the correct LLDB Python path
        lldb_path = _get_lldb_python_path()
        if lldb_path and lldb_path not in sys.path:
            sys.path.insert(0, lldb_path)
            # Also set PYTHONPATH for subprocess calls
            current_pythonpath = os.environ.get('PYTHONPATH', '')
            if lldb_path not in current_pythonpath:
                os.environ['PYTHONPATH'] = f"{lldb_path}:{current_pythonpath}" if current_pythonpath else lldb_path
        
        import lldb as _lldb
        lldb = _lldb
        logger.info("LLDB Python module loaded successfully")
        return True
        
    except ImportError as e:
        import sys
        error_msg = str(e)
        
        if "cannot import name '_lldb'" in error_msg and "cpython-39" in error_msg:
            logger.warning(f"LLDB Python bindings are compiled for Python 3.9, but you're using Python {sys.version_info.major}.{sys.version_info.minor}. "
                         f"To use LLDB, either:\n"
                         f"1. Use system Python 3.9: PYTHONPATH=/Library/Developer/CommandLineTools/Library/PrivateFrameworks/LLDB.framework/Resources/Python /usr/bin/python3\n"
                         f"2. Or run the server with system Python instead of uv")
        else:
            logger.warning(f"LLDB Python module not available: {e}")
        
        logger.info("LLDB functionality will be disabled. GDB functionality remains available.")
        return False

def is_lldb_available() -> bool:
    """Check if LLDB is available."""
    return _setup_lldb_import()


class LLDBSessionManager(DebuggerSessionManager):
    
    def __init__(self):
        self.sessions: Dict[str, Any] = {}
    
    def create_session(self, debugger_path: Optional[str] = None) -> str:
        if not is_lldb_available():
            raise RuntimeError("LLDB Python module not available")
        
        session_id = str(uuid.uuid4())
        try:
            debugger = lldb.SBDebugger.Create()
            if not debugger.IsValid():
                raise RuntimeError("Failed to create LLDB debugger instance")
            
            debugger.SetAsync(False)
            
            # Debug logging
            # debugger.EnableLog("lldb", ["default"])
            
            self.sessions[session_id] = debugger
            logger.info(f"Started LLDB session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start LLDB session: {e}")
            raise
    
    def get_session(self, session_id: str) -> Any:
        if not is_lldb_available():
            raise RuntimeError("LLDB Python module not available")
        
        if session_id not in self.sessions:
            raise ValueError(f"LLDB session '{session_id}' not found. Use lldb_list_sessions to see active sessions.")
        return self.sessions[session_id]
    
    def terminate_session(self, session_id: str) -> bool:
        if not is_lldb_available():
            return False
            
        if session_id not in self.sessions:
            return False
        
        try:
            debugger = self.sessions[session_id]
            
            for i in range(debugger.GetNumTargets()):
                target = debugger.GetTargetAtIndex(i)
                if target.IsValid():
                    process = target.GetProcess()
                    if process.IsValid():
                        process.Kill()
            
            lldb.SBDebugger.Destroy(debugger)
            del self.sessions[session_id]
            logger.info(f"Terminated LLDB session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate LLDB session: {e}")
            return False
    
    def list_sessions(self) -> list:
        return list(self.sessions.keys())
    
    def has_session(self, session_id: str) -> bool:
        return session_id in self.sessions
    
    @staticmethod
    def is_available() -> bool:
        """Check if LLDB is available on this system."""
        return is_lldb_available()

# Export the availability check
LLDB_AVAILABLE = is_lldb_available
