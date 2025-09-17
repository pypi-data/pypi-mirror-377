"""
Tool registration and discovery system for Gnosari AI Teams.
"""

import importlib
import logging
from typing import Any, Dict, List, Optional, Type
from pathlib import Path

from .base import BaseTool, tool_registry
from ..core.exceptions import ToolError


class ToolLoader:
    """
    Tool loader for discovering and loading tools from various sources.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._loaded_modules = set()
    
    def load_builtin_tools(self) -> None:
        """Load all built-in tools from the builtin package."""
        # Tools are now loaded dynamically from YAML configuration
        # No need to hardcode them here since each tool is explicitly 
        # referenced in the team configuration with module/class info
        self.logger.debug("Builtin tools will be loaded dynamically from team configuration")
    
    def _load_builtin_tool(self, tool_name: str) -> None:
        """Load a specific builtin tool."""
        module_path = f"gnosari.tools.builtin.{tool_name}"
        
        if module_path in self._loaded_modules:
            return
            
        try:
            module = importlib.import_module(module_path)
            self._loaded_modules.add(module_path)
            self.logger.debug(f"Loaded builtin tool module: {module_path}")
        except ImportError as e:
            self.logger.warning(f"Could not import builtin tool module {module_path}: {e}")
    
    def load_tool_from_config(self, tool_config: Dict[str, Any]) -> Optional[BaseTool]:
        """
        Load a tool from configuration.
        
        Args:
            tool_config: Tool configuration dictionary
            
        Returns:
            Loaded tool instance or None if loading failed
        """
        tool_name = tool_config.get('name')
        module_name = tool_config.get('module')
        class_name = tool_config.get('class')
        args = tool_config.get('args', {})
        
        if not all([tool_name, module_name, class_name]):
            self.logger.error(f"Invalid tool config: {tool_config}")
            return None
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Get the tool class
            tool_class = getattr(module, class_name)
            
            # Create tool instance
            if args and args != "pass":
                tool_instance = tool_class(**args)
            else:
                tool_instance = tool_class()
            
            # If it's not a BaseTool, try to adapt it
            if not isinstance(tool_instance, BaseTool):
                tool_instance = self._adapt_legacy_tool(tool_instance, tool_name)
            
            return tool_instance
            
        except Exception as e:
            self.logger.error(f"Failed to load tool '{tool_name}' from {module_name}.{class_name}: {e}")
            return None
    
    def _adapt_legacy_tool(self, tool_instance: Any, tool_name: str) -> Optional[BaseTool]:
        """
        Adapt a legacy tool to the BaseTool interface.
        
        Args:
            tool_instance: Legacy tool instance
            tool_name: Tool name
            
        Returns:
            Adapted BaseTool instance or None if adaptation failed
        """
        # This is a compatibility layer for existing tools
        if hasattr(tool_instance, 'get_tool'):
            # It's a Gnosari-style tool, create a wrapper
            return LegacyToolAdapter(tool_instance, tool_name)
        
        self.logger.warning(f"Cannot adapt tool '{tool_name}' - no known interface")
        return None
    
    def discover_tools_in_directory(self, directory: Path) -> List[str]:
        """
        Discover available tools in a directory.
        
        Args:
            directory: Directory to search for tools
            
        Returns:
            List of discovered tool module names
        """
        discovered = []
        
        if not directory.exists():
            return discovered
        
        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
                
            module_name = file_path.stem
            discovered.append(module_name)
        
        return discovered


class LegacyToolAdapter(BaseTool):
    """
    Adapter for legacy tools that don't inherit from BaseTool.
    """
    
    def __init__(self, legacy_tool: Any, name: str):
        from pydantic import BaseModel
        
        class AnyInput(BaseModel):
            pass
            
        super().__init__(
            name=name,
            description=getattr(legacy_tool, 'description', f"Legacy tool: {name}"),
            input_schema=AnyInput
        )
        self.legacy_tool = legacy_tool
    
    async def run(self, input_data: Any) -> Any:
        """Run the legacy tool."""
        if hasattr(self.legacy_tool, 'run'):
            return await self.legacy_tool.run(input_data)
        elif hasattr(self.legacy_tool, '__call__'):
            return await self.legacy_tool(input_data)
        else:
            raise ToolError(f"Legacy tool {self.name} has no callable interface")
    
    def get_tool(self):
        """Get the legacy tool's OpenAI function if available."""
        if hasattr(self.legacy_tool, 'get_tool'):
            return self.legacy_tool.get_tool()
        else:
            return super().get_tool()


class ToolManager:
    """
    High-level tool manager that combines loading and registry functionality.
    """
    
    def __init__(self):
        self.loader = ToolLoader()
        self.registry = tool_registry
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> None:
        """Initialize the tool manager."""
        # Tools are loaded dynamically from team configuration
        self.logger.info("Tool manager initialized - tools will be loaded from configuration")
    
    def load_tools_from_config(self, config: Dict[str, Any]) -> None:
        """
        Load tools from team configuration.
        
        Args:
            config: Team configuration dictionary
        """
        tools_config = config.get('tools', [])
        
        for tool_config in tools_config:
            # Skip MCP servers (they have 'url' or 'command')
            if tool_config.get('url') or tool_config.get('command'):
                continue
                
            tool = self.loader.load_tool_from_config(tool_config)
            if tool:
                self.registry.register(tool, tool_config)
                self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.registry.get(name)
    
    def list_available_tools(self) -> Dict[str, str]:
        """List all available tools."""
        return self.registry.list_tools()
    
    def get_openai_tools(self, tool_names: List[str]) -> List[Any]:
        """
        Get OpenAI Agents SDK compatible tools.
        
        Args:
            tool_names: List of tool names to get
            
        Returns:
            List of OpenAI compatible tool instances
        """
        openai_tools = []
        
        for tool_name in tool_names:
            tool = self.registry.get(tool_name)
            if tool:
                try:
                    openai_tool = tool.get_tool()
                    openai_tools.append(openai_tool)
                except Exception as e:
                    self.logger.error(f"Failed to get OpenAI tool for '{tool_name}': {e}")
            else:
                self.logger.warning(f"Tool '{tool_name}' not found in registry")
        
        return openai_tools


# Global tool manager instance
tool_manager = ToolManager()