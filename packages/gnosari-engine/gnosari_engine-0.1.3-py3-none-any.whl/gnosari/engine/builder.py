"""
Team Builder - Uses OpenAI Agents SDK to build teams from YAML configuration.
"""

import yaml
import logging
import traceback
from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseModel
from agents import Agent, handoff, RunContextWrapper
from agents.agent import ModelSettings
from agents.mcp import (
    MCPServerStreamableHttp, MCPServerStreamableHttpParams,
    MCPServerSse, MCPServerSseParams,
    MCPServerStdio, MCPServerStdioParams,
)
from ..prompts import build_orchestrator_system_prompt, build_specialized_agent_system_prompt
from ..knowledge import KnowledgeManager
from ..providers import setup_provider_for_model
from ..tools import (
    DelegateAgentTool, KnowledgeQueryTool, APIRequestTool,
    ToolManager, set_team_dependencies
)
from ..core.team import Team
from .runner import TeamRunner


class HandoffEscalationData(BaseModel):
    """Data model for handoff escalation events."""
    reason: str
    from_agent: str
    to_agent: str
    context: Optional[str] = None
    conversation_history: Optional[str] = None


async def on_handoff_escalation(ctx: RunContextWrapper[None], input_data: HandoffEscalationData):
    """Callback function for handoff escalation events."""
    logger = logging.getLogger(__name__)
    logger.info(f"🤝 HANDOFF ESCALATION: {input_data.from_agent} → {input_data.to_agent}")
    logger.info(f"📋 Reason: {input_data.reason}")
    if input_data.context:
        logger.info(f"📝 Context: {input_data.context}")
        # Context is now handled through the input_data itself
        input_data.conversation_history = input_data.context


class TeamBuilder:
    """Team builder for creating multi-agent teams from YAML configuration using OpenAI Agents SDK."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o", temperature: float = 1):
        """Initialize the team builder.
        
        Args:
            api_key: OpenAI API key (optional, will use environment variable if not provided)
            model: Default model to use for agents
            temperature: Default temperature for agents
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.team_config: Dict[str, Any] = {}
        self.knowledge_descriptions: Dict[str, str] = {}  # Store knowledge base descriptions
        self.knowledge_manager = None
        self.tool_manager = None
        self.mcp_tool_manager = None
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
    
    def _ensure_knowledge_manager(self):
        """Ensure knowledge manager is initialized."""
        if self.knowledge_manager is None:
            try:
                self.knowledge_manager = KnowledgeManager()
            except ImportError as e:
                self.logger.warning(f"Knowledge manager not available: {e}")
    
    def _ensure_tool_manager(self):
        """Ensure tool manager is initialized."""
        if self.tool_manager is None:
            self._ensure_knowledge_manager()
            self.tool_manager = ToolManager()
    
    def load_team_config(self, config_path: str) -> Dict[str, Any]:
        """Load team configuration from YAML file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Returns:
            Team configuration dictionary
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Team configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _load_knowledge_bases(self, knowledge_config: List[Dict[str, Any]]) -> None:
        """
        Load knowledge bases from configuration.
        
        Args:
            knowledge_config: List of knowledge base configurations from YAML
        """
        self._ensure_knowledge_manager()
        if self.knowledge_manager is None:
            self.logger.warning("Knowledge manager not available, skipping knowledge base loading")
            return
        
        for kb_config in knowledge_config:
            name = kb_config.get('name')
            kb_type = kb_config.get('type')
            
            if not name or not kb_type:
                self.logger.warning(f"Invalid knowledge base configuration: {kb_config}")
                continue
            
            # Store knowledge description if provided
            description = kb_config.get('description')
            if description:
                self.knowledge_descriptions[name] = description
                self.logger.info(f"Stored description for knowledge base '{name}': {description}")
            
            try:
                # Create knowledge base
                # Extract config if it exists
                embedchain_config = kb_config.get('config')
                self.knowledge_manager.create_knowledge_base(name, kb_type, config=embedchain_config)
                
                # Add data if specified
                data = kb_config.get('data')
                if data:
                    # Always treat data as a list for consistency
                    if isinstance(data, list):
                        data_list = data
                    else:
                        data_list = [data]
                    
                    # Add each data item to the knowledge base
                    for item in data_list:
                        self.knowledge_manager.add_data_to_knowledge_base(name, item)
                
                self.logger.info(f"Loaded knowledge base '{name}' of type '{kb_type}'")
                
            except Exception as e:
                self.logger.error(f"Failed to load knowledge base '{name}': {e}")
    
    async def _create_mcp_servers(self, tools_config: List[Dict[str, Any]]) -> List[Any]:
        """
        Create MCP servers using OpenAI Agents SDK native support.
        
        Args:
            tools_config: List of tool configurations from YAML
            
        Returns:
            List of MCP server instances
            
        Raises:
            RuntimeError: If MCP server connection fails during initialization
        """
        mcp_servers = []
        
        for tool_config in tools_config:
            tool_name = tool_config.get('name')
            tool_url = tool_config.get('url')
            tool_command = tool_config.get('command')
            
            if tool_url or tool_command:
                # This is an MCP server
                if tool_url:
                    self.logger.info(f"Creating MCP server for {tool_name} at {tool_url}")
                else:
                    self.logger.info(f"Creating MCP stdio server for {tool_name} with command {tool_command}")
                
                try:
                    # Determine connection type from config, default to 'sse' for backward compatibility
                    connection_type = tool_config.get('connection_type', 'sse').lower()
                    
                    if connection_type == 'sse':
                        # Create SSE MCP server
                        params = MCPServerSseParams(
                            url=tool_url,
                            headers=tool_config.get('headers', {}),
                            timeout=tool_config.get('timeout', 30),
                            sse_read_timeout=tool_config.get('sse_read_timeout', 30),
                        )
                        mcp_server = MCPServerSse(
                            params=params,
                            name=tool_name,
                            cache_tools_list=True,
                            client_session_timeout_seconds=tool_config.get('client_session_timeout_seconds', 30),
                        )
                        self.logger.debug(f"Creating SSE MCP server with params: {params}")
                        
                    elif connection_type == 'streamable_http':
                        # Create Streamable HTTP MCP server
                        params = MCPServerStreamableHttpParams(
                            url=tool_url,
                            headers=tool_config.get('headers', {}),
                            timeout=tool_config.get('timeout', 30),
                            sse_read_timeout=tool_config.get('sse_read_timeout', 30),
                            terminate_on_close=tool_config.get('terminate_on_close', True)
                        )
                        mcp_server = MCPServerStreamableHttp(
                            params=params,
                            name=tool_name,
                            client_session_timeout_seconds=tool_config.get('client_session_timeout_seconds', 30),
                        )
                        self.logger.debug(f"Creating Streamable HTTP MCP server with params: {params}")

                    elif connection_type == 'stdio':
                        # Create Stdio MCP server
                        params = MCPServerStdioParams(
                            command=tool_command,
                            args=tool_config.get('args', []),
                        )

                        mcp_server = MCPServerStdio(
                            params=params,
                            name=tool_name,
                            client_session_timeout_seconds=tool_config.get('client_session_timeout_seconds', 30),
                        )
                        self.logger.debug(f"Creating Stdio MCP server with params: {params}")
                        
                    else:
                        raise ValueError(f"Unsupported connection_type: {connection_type}. Supported types: 'sse', 'streamable_http', 'stdio'")
                    
                    # Create MCP server instance - the Agent class will handle the async context management

                    # Note: The Agent class will handle connection and cleanup automatically
                    # If you need to ensure connection is established, you can uncomment the following:
                    # try:
                    #     await mcp_server.connect()
                    #     self.logger.debug(f"Connected to MCP server: {tool_name}")
                    # except Exception as e:
                    #     self.logger.warning(f"Failed to connect to MCP server {tool_name}: {e}")
                    #     # Continue anyway - the Agent will retry connection when needed
                    
                    # Ensure the server has a name attribute
                    if not hasattr(mcp_server, 'name') or mcp_server.name is None:
                        mcp_server.name = tool_name
                    
                    # Debug logging to check server attributes
                    self.logger.debug(f"MCP server '{tool_name}' attributes: {dir(mcp_server)}")
                    self.logger.debug(f"MCP server '{tool_name}' name: {getattr(mcp_server, 'name', 'NOT_SET')}")
                    self.logger.debug(f"MCP server '{tool_name}' type: {type(mcp_server)}")
                    
                    mcp_servers.append(mcp_server)
                    self.logger.info(f"✅ Created MCP server for '{tool_name}'")
                        
                except Exception as e:
                    if tool_url:
                        error_msg = f"Failed to create MCP server '{tool_name}' at {tool_url}: {e}"
                    else:
                        error_msg = f"Failed to create MCP stdio server '{tool_name}' with command {tool_command}: {e}"
                    self.logger.error(error_msg)
                    self.logger.error(f"Full traceback: {traceback.format_exc()}")
                    print(f"ERROR: {error_msg}")
                    raise RuntimeError(error_msg)
        
        return mcp_servers
    
    def _get_mcp_server_names(self, mcp_servers: List[str], config: Dict[str, Any]) -> List[str]:
        """
        Get the names of MCP servers that should be included for an agent.
        
        Args:
            mcp_servers: List of MCP server names to include
            config: Team configuration
            
        Returns:
            List of MCP server names that exist in the configuration
        """
        if 'tools' not in config:
            return []
        
        available_servers = []
        for tool_config in config['tools']:
            tool_name = tool_config.get('name')
            tool_url = tool_config.get('url')
            tool_command = tool_config.get('command')
            
            if (tool_url or tool_command) and tool_name in mcp_servers:
                available_servers.append(tool_name)
        
        return available_servers
    
    def _add_knowledge_tools(self, agent_tools: List[str], knowledge_names: List[str]) -> List[str]:
        """
        Add knowledge query tools for specified knowledge bases to the agent's tool list.
        
        Args:
            agent_tools: Current list of agent tools
            knowledge_names: List of knowledge base names to add tools for
            
        Returns:
            Updated list of agent tools including knowledge query tools
        """
        self._ensure_knowledge_manager()
        if self.knowledge_manager is None:
            self.logger.warning("Knowledge manager not available, skipping knowledge tools")
            return agent_tools
        
        # Check if knowledge_query tool is already in the list
        if 'knowledge_query' not in agent_tools:
            agent_tools.append('knowledge_query')
            self.logger.info(f"Added knowledge_query tool to agent")
        
        return agent_tools
    
    def build_agent(self, name: str, instructions: str, is_orchestrator: bool = False, team_config: Dict[str, Any] = None, agent_tools: List[str] = None, agent_config: Dict[str, Any] = None, token_callback: Optional[callable] = None, mcp_servers: List[Any] = None) -> Agent:
        """Build a single agent with the given configuration using OpenAI Agents SDK.
        
        Args:
            name: Agent name
            instructions: Agent instructions
            is_orchestrator: Whether this agent is an orchestrator
            team_config: Team configuration for orchestrator context
            agent_tools: List of tool names to inject into this agent
            agent_config: Agent-specific configuration from YAML
            
        Returns:
            Built OpenAI Agent
        """
        # Get agent-specific model configuration, fallback to global default
        agent_model = agent_config.get('model', self.model) if agent_config else self.model
        agent_temperature = agent_config.get('temperature', self.temperature) if agent_config else self.temperature
        
        # Create system prompt based on agent type
        self._ensure_tool_manager()
        if is_orchestrator:
            prompt_components = build_orchestrator_system_prompt(name, instructions, team_config, agent_tools, self.tool_manager, agent_config, self.knowledge_descriptions)
        else:
            prompt_components = build_specialized_agent_system_prompt(name, instructions, agent_tools, self.tool_manager, agent_config, self.knowledge_descriptions)
        
        background = prompt_components["background"]
        steps = prompt_components["steps"]
        output_instructions = prompt_components["output_instructions"]

        # Combine all prompt components
        system_prompt = f"{background}\n\n{steps}\n\n{output_instructions}"
        
        # Set up provider for the model (this handles API keys and base URLs)
        setup_provider_for_model(agent_model)
        
        # Create model settings
        model_settings = ModelSettings(
            temperature=agent_temperature,
            # timeout=300.0,
            # api_key=api_key,
            # base_url=base_url
        )
        
        # Build list of OpenAI native tools
        openai_tools = []
        
        # Add the knowledge query tool only if this agent has knowledge bases configured
        if agent_config and agent_config.get('knowledge') and hasattr(self, 'knowledge_manager') and self.knowledge_manager:
            knowledge_tool = KnowledgeQueryTool(knowledge_manager=self.knowledge_manager)
            openai_tools.append(knowledge_tool.get_tool())
            self.logger.debug(f"Added knowledge_query tool to agent '{name}' with knowledge bases: {agent_config.get('knowledge')}")
        
        # Handle delegate_agent tool specially if delegation is configured
        delegate_tool_instance = None
        has_delegation = agent_config and agent_config.get('delegation')
        delegate_in_tools = agent_tools and "delegate_agent" in agent_tools
        
        if has_delegation or delegate_in_tools:
            delegate_tool_instance = DelegateAgentTool()
            openai_tools.append(delegate_tool_instance.get_tool())
            # Store for team dependency setup
            if not hasattr(self, '_delegate_tools'):
                self._delegate_tools = {}
            self._delegate_tools[name] = delegate_tool_instance
            self.logger.info(f"Added delegate_agent tool to agent '{name}' (delegation: {has_delegation}, explicit: {delegate_in_tools})")
            # Remove from tools list to avoid duplicate processing
            if delegate_in_tools:
                agent_tools = [tool for tool in agent_tools if tool != "delegate_agent"]
        
        # Handle tools defined in YAML using dynamic loading
        if agent_tools:
            self.logger.debug(f"Processing {len(agent_tools)} tools for agent '{name}': {agent_tools}")
            self.logger.debug(f"Available tools in tool_manager: {list(self.tool_manager.list_available_tools().keys())}")
            for tool_name in agent_tools:
                try:
                    # Get tool configuration from tool_manager
                    tool_config = self.tool_manager.list_available_tools().get(tool_name, {})
                    if not tool_config:
                        self.logger.warning(f"Tool '{tool_name}' not found in available tools for agent '{name}'")
                        self.logger.debug(f"Available tools: {list(self.tool_manager.list_available_tools().keys())}")
                        continue
                    
                    module_name = tool_config.get('module', '')
                    class_name = tool_config.get('class', '')
                    args = tool_config.get('args', {})
                    
                    self.logger.debug(f"Found tool config for '{tool_name}': module={module_name}, class={class_name}, args={args}")
                    
                    # Dynamically import and create the tool instance
                    try:
                        self.logger.debug(f"Importing module '{module_name}' for tool '{tool_name}'")
                        module = __import__(module_name, fromlist=[class_name])
                        tool_class = getattr(module, class_name)
                        self.logger.debug(f"Successfully imported {class_name} from {module_name}")
                        
                        # Create tool instance with args
                        if args and args != "pass":
                            tool_instance = tool_class(**args)
                        else:
                            tool_instance = tool_class()
                        
                        # Check if this is a Gnosari tool (has get_tool method) or OpenAI SDK tool (is already a tool)
                        if hasattr(tool_instance, 'get_tool'):
                            # Gnosari custom tool - get the FunctionTool
                            openai_tools.append(tool_instance.get_tool())
                            self.logger.debug(f"Added Gnosari-style tool '{tool_name}' via get_tool() method")
                        else:
                            # OpenAI SDK tool - use directly
                            openai_tools.append(tool_instance)
                            self.logger.debug(f"Added OpenAI SDK tool '{tool_name}' directly")
                        self.logger.info(f"Added OpenAI-compatible tool '{tool_name}' to agent '{name}'")
                        
                        # Store delegate tools for team dependency setup
                        if class_name == "DelegateAgentTool":
                            if not hasattr(self, '_delegate_tools'):
                                self._delegate_tools = {}
                            self._delegate_tools[name] = tool_instance
                        
                    except (ImportError, AttributeError) as e:
                        self.logger.error(f"Failed to import tool class {class_name} from {module_name}: {e}")
                        continue
                        
                except Exception as e:
                    self.logger.warning(f"Failed to create tool '{tool_name}' for agent '{name}': {e}")
        
        # Create the OpenAI Agent
        agent = Agent(
            name=name,
            instructions=system_prompt,
            model=agent_model,
            model_settings=model_settings,
            tools=openai_tools,
            mcp_servers=mcp_servers or [],
        )
        
        # Add knowledge manager to the agent's context if available
        if hasattr(self, 'knowledge_manager') and self.knowledge_manager:
            agent.context = {"knowledge_manager": self.knowledge_manager}
        
        return agent
    
    async def build_team(self, config_path: str, debug: bool = False, token_callback: Optional[callable] = None) -> Team:
        """Build a complete team from YAML configuration using OpenAI Agents SDK.
        
        Args:
            config_path: Path to the YAML configuration file
            debug: Whether to show debug information
            token_callback: Optional callback function to report token usage
            
        Returns:
            Team object containing orchestrator and worker agents
        """
        config = self.load_team_config(config_path)
        
        if 'agents' not in config:
            raise ValueError("Team configuration must contain 'agents' section")
        
        # Store team config for later use
        self.team_config = config
        
        # Load knowledge bases first
        if 'knowledge' in config:
            self._load_knowledge_bases(config['knowledge'])
        
        # Load tools and register knowledge tools
        self._ensure_tool_manager()
        if 'tools' in config:
            self.logger.debug(f"Loading tools from config: {[tool.get('name') for tool in config['tools']]}")
            self.tool_manager.load_tools_from_config(config)
            self.logger.debug(f"Available tools after loading: {list(self.tool_manager.list_available_tools().keys())}")
        else:
            self.logger.debug("No tools section found in config")
        
        # Create MCP servers using OpenAI Agents SDK native support
        mcp_servers = []
        if 'tools' in config:
            mcp_servers = await self._create_mcp_servers(config['tools'])
            # Store MCP servers in the builder instance for later use
            self.mcp_servers = mcp_servers
        
        # Register knowledge_query tool if knowledge bases are defined (regardless of other tools)
        if 'knowledge' in config and self.knowledge_manager is not None:
            # Use the new OpenAI-compatible knowledge query tool
            
            # Knowledge manager is already available in self.knowledge_manager
            self.logger.debug("Registered OpenAI-compatible knowledge_query tool")
        
        # Register delegate_agent tool if any agent has delegate_agent in its tools list
        has_delegation = any(
            "delegate_agent" in agent_config.get('tools', [])
            for agent_config in config['agents']
        )
        if has_delegation:
            # We'll set the team dependencies after the team is created
            self.logger.debug("Will register OpenAI-compatible delegate_agent tool")
        
        orchestrator = None
        workers = {}
        all_agents = {}  # Store all agents for handoff setup
        
        # First pass: build all agents
        for agent_config in config['agents']:
            name = agent_config['name']
            instructions = agent_config['instructions']
            is_orchestrator = agent_config.get('orchestrator', False)
            agent_tools = agent_config.get('tools', [])
            mcp_servers = agent_config.get('mcp_servers', [])
            knowledge_names = agent_config.get('knowledge', [])
            self.logger.debug(f"Building agent '{name}' with tools: {agent_tools}")
            
            # Get MCP servers for this agent
            agent_mcp_servers = []
            if mcp_servers and hasattr(self, 'mcp_servers') and self.mcp_servers:
                # Get the names of MCP servers this agent should have access to
                agent_mcp_server_names = self._get_mcp_server_names(mcp_servers, config)
                # Filter the actual MCP server objects based on the names
                if agent_mcp_server_names:
                    agent_mcp_servers = [server for server in self.mcp_servers if server.name in agent_mcp_server_names]
                    self.logger.debug(f"Agent '{name}' gets MCP servers: {[server.name for server in agent_mcp_servers]}")
            
            # Add knowledge query tools if agent has knowledge bases
            if knowledge_names:
                agent_tools = self._add_knowledge_tools(agent_tools, knowledge_names)
            
            # Note: delegate_agent tool will be auto-added in build_agent() if delegation is configured
            
            # Build the OpenAI Agent
            agent = self.build_agent(name, instructions, is_orchestrator, config, agent_tools, agent_config, token_callback, agent_mcp_servers)
            
            # Store agent config for handoff setup
            all_agents[name] = {
                'agent': agent,
                'config': agent_config,
                'is_orchestrator': is_orchestrator
            }
            
            if is_orchestrator:
                orchestrator = agent
            else:
                workers[name] = agent
        
        # If no orchestrator was found, use the first agent as orchestrator
        if orchestrator is None and workers:
            first_agent_name = list(workers.keys())[0]
            orchestrator = workers.pop(first_agent_name)
            if debug:
                self.logger.warning(f"No orchestrator found, using '{first_agent_name}' as orchestrator")
        
        if orchestrator is None:
            raise ValueError("No agents found in team configuration")
        
        # Set up handoffs based on can_transfer_to configuration
        for agent_name, agent_info in all_agents.items():
            agent = agent_info['agent']
            agent_config = agent_info['config']
            can_transfer_to = agent_config.get('can_transfer_to', [])
            
            if can_transfer_to:
                handoffs_list = []
                handoff_targets = []
                
                # Handle both old format (list of strings) and new format (list of objects)
                for transfer_config in can_transfer_to:
                    if isinstance(transfer_config, str):
                        # Old format: just agent name
                        target_agent_name = transfer_config
                        transfer_instructions = None
                    elif isinstance(transfer_config, dict):
                        # New format: object with agent and instructions
                        target_agent_name = transfer_config.get('agent')
                        transfer_instructions = transfer_config.get('instructions')
                    else:
                        self.logger.warning(f"Invalid can_transfer_to configuration for agent '{agent_name}': {transfer_config}")
                        continue
                    
                    if target_agent_name in all_agents:
                        target_agent = all_agents[target_agent_name]['agent']
                        
                        # Create handoff with escalation callback
                        handoff_obj = handoff(
                            agent=target_agent,
                            on_handoff=on_handoff_escalation,
                            input_type=HandoffEscalationData
                        )
                        handoffs_list.append(handoff_obj)
                        handoff_targets.append(target_agent_name)
                        
                        if transfer_instructions:
                            self.logger.info(f"🔗 Set up handoff from '{agent_name}' to '{target_agent_name}' with instructions: {transfer_instructions}")
                        else:
                            self.logger.info(f"🔗 Set up handoff from '{agent_name}' to '{target_agent_name}'")
                    else:
                        self.logger.warning(f"⚠️  Agent '{agent_name}' configured to transfer to '{target_agent_name}', but that agent doesn't exist")
                
                # Set handoffs for this agent
                agent.handoffs = handoffs_list
                
                if agent_info['is_orchestrator']:
                    self.logger.info(f"🎯 Set up handoffs for orchestrator '{agent_name}': {handoff_targets}")
                else:
                    self.logger.info(f"🤝 Set up handoffs for worker '{agent_name}': {handoff_targets}")
        
        # Create the team object
        max_turns = config.get('config', {}).get('max_turns')
        team = Team(orchestrator, workers, name=config.get('name'), max_turns=max_turns)
        
        # Set up team dependencies for delegate_agent tools if needed
        if has_delegation or hasattr(self, '_delegate_tools'):
            # Create a team runner for the delegate_agent tool
            team_runner = TeamRunner(team)
            
            # Set up individual delegate tool instances
            if hasattr(self, '_delegate_tools'):
                for agent_name, delegate_tool in self._delegate_tools.items():
                    delegate_tool.set_team_dependencies(team, team_runner)
                    self.logger.debug(f"Set up team dependencies for delegate tool in agent '{agent_name}'")
            
            # Also set global dependencies for backward compatibility
            set_team_dependencies(team, team_runner)
            self.logger.debug("Set up team dependencies for OpenAI-compatible delegate_agent tool")
        
        return team
    
    async def cleanup_mcp_servers(self):
        """Clean up MCP server connections."""
        if hasattr(self, 'mcp_servers') and self.mcp_servers:
            self.logger.info("Cleaning up MCP server connections...")
            for server in self.mcp_servers:
                try:
                    if hasattr(server, 'cleanup'):
                        await server.cleanup()
                        self.logger.debug(f"Cleaned up MCP server: {server.name}")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up MCP server {server.name}: {e}")
            self.logger.info("MCP server cleanup completed")