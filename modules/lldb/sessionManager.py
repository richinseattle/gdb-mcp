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
    
    # Try Homebrew LLDB first (works with modern Python)
    homebrew_lldb = '/opt/homebrew/opt/llvm/bin/lldb'
    if os.path.exists(homebrew_lldb):
        try:
            result = subprocess.run([homebrew_lldb, '-P'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                path = result.stdout.strip()
                if os.path.exists(path):
                    return path
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            pass
    
    return None

LLDB_AVAILABLE = False
lldb = None

try:
    import sys
    import os
    
    lldb_path = _get_lldb_python_path()
    if lldb_path and lldb_path not in sys.path:
        sys.path.insert(0, lldb_path)
    
    import lldb
    LLDB_AVAILABLE = True
    logger.info("LLDB Python module loaded successfully")
except ImportError as e:
    LLDB_AVAILABLE = False
    lldb = None
    logger.warning(f"LLDB Python module not available: {e}. LLDB functionality will be disabled.")

def is_lldb_available() -> bool:
    """Check if LLDB is available."""
    return LLDB_AVAILABLE


class LLDBSessionManager(DebuggerSessionManager):
    
    def __init__(self):
        self.sessions: Dict[str, Any] = {}
    
    def create_session(self, debugger_path: Optional[str] = None) -> str:
        if not LLDB_AVAILABLE:
            raise RuntimeError("LLDB Python module not available")
        
        session_id = str(uuid.uuid4())
        try:
            debugger = lldb.SBDebugger.Create()
            if not debugger.IsValid():
                raise RuntimeError("Failed to create LLDB debugger instance")
            
            debugger.SetAsync(False)
            self.sessions[session_id] = debugger
            logger.info(f"Started LLDB session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start LLDB session: {e}")
            raise
    
    def get_session(self, session_id: str) -> Any:
        if not LLDB_AVAILABLE:
            raise RuntimeError("LLDB Python module not available")
        
        if session_id not in self.sessions:
            raise ValueError(f"LLDB session '{session_id}' not found. Use lldb_list_sessions to see active sessions.")
        return self.sessions[session_id]
    
    def terminate_session(self, session_id: str) -> bool:
        if not LLDB_AVAILABLE:
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
        return LLDB_AVAILABLE
