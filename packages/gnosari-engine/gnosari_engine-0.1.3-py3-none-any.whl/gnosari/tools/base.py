"""
Base tool classes and interfaces for Gnosari AI Teams.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar, Optional
from pydantic import BaseModel
from agents import FunctionTool

InputSchema = TypeVar('InputSchema', bound=BaseModel)
OutputSchema = TypeVar('OutputSchema', bound=BaseModel)


class BaseTool(ABC, Generic[InputSchema, OutputSchema]):
    """
    Base class for all Gnosari tools.
    
    This class provides a standard interface for creating tools that can be
    used with both the OpenAI Agents SDK and custom Gnosari functionality.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: type[InputSchema],
        output_schema: Optional[type[OutputSchema]] = None
    ):
        """
        Initialize the base tool.
        
        Args:
            name: Tool name
            description: Tool description
            input_schema: Pydantic model for input validation
            output_schema: Optional Pydantic model for output validation
        """
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema
        
    @abstractmethod
    async def run(self, input_data: InputSchema) -> Any:
        """
        Execute the tool with the given input.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Tool execution result
        """
        pass
    
    def get_tool(self) -> FunctionTool:
        """
        Get an OpenAI Agents SDK compatible FunctionTool.
        
        Returns:
            FunctionTool instance for use with OpenAI Agents SDK
        """
        from agents import RunContextWrapper
        
        async def invoke_wrapper(ctx: RunContextWrapper[Any], args: str) -> str:
            """Wrapper function for OpenAI Agents SDK integration."""
            import json
            
            # Parse the arguments
            args_dict = json.loads(args)
            
            # Validate input using Pydantic schema
            input_data = self.input_schema(**args_dict)
            
            # Execute the tool
            result = await self.run(input_data)
            
            # Return result as string (OpenAI Agents SDK requirement)
            if isinstance(result, str):
                return result
            elif isinstance(result, dict):
                return json.dumps(result)
            else:
                return str(result)
        
        return FunctionTool(
            name=self.name,
            description=self.description,
            params_json_schema=self.input_schema.model_json_schema(),
            on_invoke_tool=invoke_wrapper
        )


class SimpleStringTool(BaseTool[BaseModel, str]):
    """
    Simplified base class for tools that take string input and return string output.
    """
    
    def __init__(self, name: str, description: str):
        # Create a simple string input schema
        class StringInput(BaseModel):
            input: str
            
        super().__init__(name, description, StringInput)
    
    @abstractmethod
    async def run_simple(self, input_str: str) -> str:
        """
        Execute the tool with string input.
        
        Args:
            input_str: Input string
            
        Returns:
            Output string
        """
        pass
    
    async def run(self, input_data: BaseModel) -> str:
        """Implementation of base run method."""
        return await self.run_simple(input_data.input)


class ToolRegistry:
    """
    Registry for managing available tools.
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_configs: Dict[str, Dict[str, Any]] = {}
    
    def register(self, tool: BaseTool, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool instance to register
            config: Optional configuration for the tool
        """
        self._tools[tool.name] = tool
        if config:
            self._tool_configs[tool.name] = config
    
    def get(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)
    
    def get_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get tool configuration by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool configuration or None if not found
        """
        return self._tool_configs.get(name)
    
    def list_tools(self) -> Dict[str, str]:
        """
        List all registered tools.
        
        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {name: tool.description for name, tool in self._tools.items()}
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            name: Tool name to unregister
            
        Returns:
            True if tool was found and removed, False otherwise
        """
        if name in self._tools:
            del self._tools[name]
            self._tool_configs.pop(name, None)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self._tool_configs.clear()


# Global tool registry instance
tool_registry = ToolRegistry()