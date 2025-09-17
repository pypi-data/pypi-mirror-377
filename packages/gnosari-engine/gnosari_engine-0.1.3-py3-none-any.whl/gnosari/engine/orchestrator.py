"""
Orchestrator - Core orchestration logic for managing agent interactions and workflows.
"""

import logging
from typing import Any, Dict, List, Optional, AsyncGenerator
from ..core.team import Team
from ..core.exceptions import AgentError, ConfigurationError


class TeamOrchestrator:
    """
    Orchestrates the execution of multi-agent teams.
    
    This class handles the high-level coordination of agent interactions,
    workflow management, and team-level decision making.
    """
    
    def __init__(self, team: Team):
        """
        Initialize the orchestrator with a team.
        
        Args:
            team: The team to orchestrate
        """
        self.team = team
        self.logger = logging.getLogger(__name__)
        self._execution_state = {}
        
    async def execute_workflow(
        self,
        initial_message: str,
        context: Optional[Dict[str, Any]] = None,
        max_iterations: Optional[int] = None
    ) -> Any:
        """
        Execute a workflow starting with the orchestrator agent.
        
        Args:
            initial_message: The initial message to send to the orchestrator
            context: Optional context to pass to agents
            max_iterations: Maximum number of agent interactions
            
        Returns:
            The final result from the workflow execution
        """
        if not self.team.orchestrator:
            raise ConfigurationError("Team must have an orchestrator agent")
        
        self.logger.info(f"Starting workflow execution with message: {initial_message[:100]}...")
        
        try:
            # Initialize execution state
            self._execution_state = {
                'iteration': 0,
                'current_agent': self.team.orchestrator.name,
                'context': context or {}
            }
            
            # Start with the orchestrator
            result = await self.team.orchestrator.run(initial_message, context)
            
            self.logger.info("Workflow execution completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise AgentError(f"Workflow execution failed: {e}")
    
    async def execute_streaming_workflow(
        self,
        initial_message: str,
        context: Optional[Dict[str, Any]] = None,
        max_iterations: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a workflow with streaming results.
        
        Args:
            initial_message: The initial message to send to the orchestrator
            context: Optional context to pass to agents
            max_iterations: Maximum number of agent interactions
            
        Yields:
            Streaming results from the workflow execution
        """
        if not self.team.orchestrator:
            raise ConfigurationError("Team must have an orchestrator agent")
        
        self.logger.info(f"Starting streaming workflow execution with message: {initial_message[:100]}...")
        
        try:
            # Initialize execution state
            self._execution_state = {
                'iteration': 0,
                'current_agent': self.team.orchestrator.name,
                'context': context or {}
            }
            
            # Yield initial state
            yield {
                'type': 'workflow_start',
                'agent': self.team.orchestrator.name,
                'message': initial_message
            }
            
            # Start with the orchestrator
            result = await self.team.orchestrator.run(initial_message, context)
            
            # Yield final result
            yield {
                'type': 'workflow_complete',
                'result': result
            }
            
            self.logger.info("Streaming workflow execution completed successfully")
            
        except Exception as e:
            self.logger.error(f"Streaming workflow execution failed: {e}")
            yield {
                'type': 'workflow_error',
                'error': str(e)
            }
            raise AgentError(f"Streaming workflow execution failed: {e}")
    
    def get_execution_state(self) -> Dict[str, Any]:
        """
        Get the current execution state.
        
        Returns:
            Current execution state dictionary
        """
        return self._execution_state.copy()
    
    def get_team_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the team configuration.
        
        Returns:
            Team summary including agent names and capabilities
        """
        return {
            'name': self.team.name,
            'orchestrator': self.team.orchestrator.name,
            'workers': list(self.team.workers.keys()),
            'total_agents': len(self.team.all_agents),
            'max_turns': self.team.max_turns
        }


class WorkflowContext:
    """
    Context manager for workflow execution state and data sharing.
    """
    
    def __init__(self):
        self._data = {}
        self._history = []
        
    def set(self, key: str, value: Any) -> None:
        """Set a context value."""
        self._data[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value."""
        return self._data.get(key, default)
        
    def add_to_history(self, event: Dict[str, Any]) -> None:
        """Add an event to the execution history."""
        self._history.append(event)
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the execution history."""
        return self._history.copy()
        
    def clear(self) -> None:
        """Clear the context."""
        self._data.clear()
        self._history.clear()