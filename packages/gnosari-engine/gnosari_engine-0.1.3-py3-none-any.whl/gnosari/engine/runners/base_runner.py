"""
Base runner with common functionality
"""

import logging
from typing import Optional, Dict, Any
from agents import RunConfig
from ..team import Team
from .session_manager import SessionManager
from .cleanup_manager import CleanupManager

logger = logging.getLogger(__name__)


class BaseRunner:
    """Base class for all runners with common functionality."""
    
    def __init__(self, team: Team):
        self.team = team
        self.logger = logging.getLogger(__name__)
        self.session_manager = SessionManager()
        self.cleanup_manager = CleanupManager()
    
    def set_custom_session_provider(self, provider_factory):
        """Set a custom session provider factory function.
        
        Args:
            provider_factory: Function that takes session_id and returns a session provider
        """
        self.session_manager.set_custom_session_provider(provider_factory)
    
    def _create_run_config(self, workflow_name: Optional[str] = None) -> RunConfig:
        """Create a run configuration.
        
        Args:
            workflow_name: Name for the workflow
            
        Returns:
            RunConfig instance
        """
        return RunConfig(
            workflow_name=workflow_name or self.team.name or "Unknown Team"
        )
    
    def _get_session(self, session_id: Optional[str] = None, session_context: Optional[Dict[str, Any]] = None):
        """Get session for persistence.
        
        Args:
            session_id: Session identifier
            session_context: Session context data
            
        Returns:
            Session instance or None
        """
        return self.session_manager.get_session(session_id, session_context)
    
    def _log_session_info(self, session, session_id: Optional[str], context: str = ""):
        """Log session information.
        
        Args:
            session: Session instance
            session_id: Session identifier
            context: Additional context for logging
        """
        if session:
            self.logger.info(f"Running {context} with persistent session: {session_id}")
        else:
            self.logger.info(f"Running {context} without session persistence")
    
    def _get_effective_max_turns(self, max_turns: Optional[int]) -> Optional[int]:
        """Get effective max turns value.
        
        Args:
            max_turns: Requested max turns
            
        Returns:
            Effective max turns value (None if no limit should be applied)
        """
        # Return the provided max_turns if it's not None
        if max_turns is not None:
            return max_turns
        
        # Return team's max_turns if it's not None
        if self.team.max_turns is not None:
            return self.team.max_turns
        
        # Return None if no max_turns is configured (no limit)
        return None