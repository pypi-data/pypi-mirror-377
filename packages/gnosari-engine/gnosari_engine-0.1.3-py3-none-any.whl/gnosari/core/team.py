"""
Team Models - Shared models for team management using OpenAI Agents SDK integration.
"""

from typing import Dict, List, Optional
from agents import Agent


class Team:
    """Team object containing orchestrator and worker agents using OpenAI Agents SDK."""
    
    def __init__(self, orchestrator: Agent, workers: Dict[str, Agent], name: Optional[str] = None, max_turns: Optional[int] = None):
        """Initialize the team.
        
        Args:
            orchestrator: The orchestrator/leader agent using OpenAI Agents SDK
            workers: Dictionary of worker agents using OpenAI Agents SDK
            name: Optional team name
            max_turns: Optional maximum turns for team execution
        """
        self.orchestrator = orchestrator
        self.workers = workers
        self.name = name
        self.max_turns = max_turns
        self.all_agents = {**workers, orchestrator.name: orchestrator}

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent instance or None if not found
        """
        return self.all_agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all agent names in the team.
        
        Returns:
            List of agent names
        """
        return list(self.all_agents.keys())