"""GDB session management module."""

import logging
import uuid
from typing import Dict
from pygdbmi.gdbcontroller import GdbController

logger = logging.getLogger(__name__)

class GDBSessionManager:
    """Manages GDB debugging sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, GdbController] = {}
    
    def create_session(self, gdb_path: str = "gdb") -> str:
        """Create a new GDB session and return its ID."""
        session_id = str(uuid.uuid4())
        try:
            # GdbController expects a command list, not a gdb_path parameter
            gdb_controller = GdbController(command=[gdb_path])
            self.sessions[session_id] = gdb_controller
            logger.info(f"Started GDB session: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Failed to start GDB session: {e}")
            raise
    
    def get_session(self, session_id: str) -> GdbController:
        """Get a GDB session by ID."""
        if session_id not in self.sessions:
            raise ValueError(f"GDB session '{session_id}' not found. Use gdb_list_sessions to see active sessions.")
        return self.sessions[session_id]
    
    def terminate_session(self, session_id: str) -> bool:
        """Terminate a GDB session."""
        if session_id not in self.sessions:
            return False
        
        try:
            gdb = self.sessions[session_id]
            gdb.exit()
            del self.sessions[session_id]
            logger.info(f"Terminated GDB session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to terminate GDB session: {e}")
            return False
    
    def list_sessions(self) -> list:
        """List all active session IDs."""
        return list(self.sessions.keys())
    
    def has_session(self, session_id: str) -> bool:
        """Check if a session exists."""
        return session_id in self.sessions