"""
Team execution runner
"""

import asyncio
from typing import Optional, AsyncGenerator, Dict, Any
from agents import Runner
from ..event_handlers import StreamEventHandler, ErrorHandler, MCPServerManager
from .base_runner import BaseRunner

class TeamRunner(BaseRunner):
    """Runner for executing team workflows."""
    
    async def run_team_async(self, message: str, debug: bool = False, 
                            session_id: Optional[str] = None, 
                            session_context: Optional[Dict[str, Any]] = None, 
                            max_turns: Optional[int] = None) -> Dict[str, Any]:
        """Run team asynchronously using OpenAI Agents SDK Runner.
        
        Args:
            message: User message
            debug: Whether to show debug info
            session_id: Session ID for conversation persistence
            session_context: Session context data
            max_turns: Maximum number of turns
            
        Returns:
            Dict with outputs and completion status
        """
        if debug:
            self.logger.info(f"Contacting {self.team.orchestrator.name}")
        
        # Initialize MCP manager and connect servers
        mcp_manager = MCPServerManager()
        all_agents = [self.team.orchestrator] + list(self.team.workers.values())
        await mcp_manager.connect_servers(all_agents)

        session = None
        try:
            run_config = self._create_run_config()
            session = self._get_session(session_id, session_context)
            self._log_session_info(session, session_id, "team")
            
            # Only include max_turns if it's not None
            effective_max_turns = self._get_effective_max_turns(max_turns)
            if effective_max_turns is not None:
                result = await Runner.run(
                    self.team.orchestrator,
                    input=message,
                    run_config=run_config,
                    session=session,
                    max_turns=effective_max_turns
                )
            else:
                result = await Runner.run(
                    self.team.orchestrator,
                    input=message,
                    run_config=run_config,
                    session=session
                )
            
            # Convert result to our expected format
            return {
                "outputs": [{"type": "completion", "content": result.final_output}],
                "agent_name": self.team.orchestrator.name,
                "is_done": True
            }
        finally:
            await self.cleanup_manager.cleanup_all(session, mcp_manager, all_agents)
    
    def run_team(self, message: str, debug: bool = False, 
                session_id: Optional[str] = None, 
                max_turns: Optional[int] = None) -> Dict[str, Any]:
        """Run team synchronously."""
        return asyncio.run(self.run_team_async(message, debug, session_id, max_turns=max_turns))
    
    async def run_team_stream(self, message: str, debug: bool = False, 
                             session_id: Optional[str] = None, 
                             session_context: Optional[Dict[str, Any]] = None, 
                             max_turns: Optional[int] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Run team with streaming outputs using OpenAI Agents SDK.
        
        Args:
            message: User message
            debug: Whether to show debug info
            session_id: Session ID for conversation persistence
            session_context: Session context data
            max_turns: Maximum number of turns
            
        Yields:
            Dict: Stream outputs (response chunks, tool calls, handoffs, etc.)
        """
        self.logger.info(f"Contacting {self.team.orchestrator.name}")
        
        # Initialize handlers
        current_agent = self.team.orchestrator.name
        event_handler = StreamEventHandler(current_agent)
        error_handler = ErrorHandler(current_agent)
        mcp_manager = MCPServerManager()
        
        # Connect MCP servers before running
        all_agents = [self.team.orchestrator] + list(self.team.workers.values())
        await mcp_manager.connect_servers(all_agents)

        session = None
        try:
            run_config = self._create_run_config()
            session = self._get_session(session_id, session_context)
            self._log_session_info(session, session_id, "team stream")
            
            # Only include max_turns if it's not None
            effective_max_turns = self._get_effective_max_turns(max_turns)
            if effective_max_turns is not None:
                result = Runner.run_streamed(
                    self.team.orchestrator,
                    input=message,
                    run_config=run_config,
                    session=session,
                    max_turns=effective_max_turns
                )
            else:
                result = Runner.run_streamed(
                    self.team.orchestrator,
                    input=message,
                    run_config=run_config,
                    session=session
                )
            
            self.logger.info("Starting to process streaming events...")
            
            async for event in result.stream_events():
                self.logger.debug(f"Received event: {event.type}. Item: {event}")
                
                # Use event handler to process events
                async for response in event_handler.handle_event(event):
                    # Update current agent if changed
                    if response.get('type') == 'agent_updated':
                        current_agent = response.get('agent_name', current_agent)
                        event_handler.current_agent = current_agent
                    yield response

            # Yield final completion
            yield {
                "type": "completion",
                "content": result.final_output,
                "output": result.final_output,
                "agent_name": current_agent,
                "is_done": True
            }
            
        except Exception as e:
            # Use simplified error handler
            error_response = error_handler.handle_error(e)
            yield error_response
            raise e
        finally:
            await self.cleanup_manager.cleanup_all(session, mcp_manager, all_agents)