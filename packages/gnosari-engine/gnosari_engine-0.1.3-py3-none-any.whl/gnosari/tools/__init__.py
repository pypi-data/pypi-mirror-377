"""
Gnosari Tools - Modular tool system for AI agents.

This package provides a comprehensive tool system with:
- Base classes for creating new tools
- Built-in tools for common operations
- MCP (Model Context Protocol) integration
- Tool registry and discovery system
"""

from .base import BaseTool, SimpleStringTool, ToolRegistry, tool_registry
from .registry import ToolManager, ToolLoader, tool_manager

# Import builtin tools for backward compatibility
from .builtin import (
    DelegateAgentTool,
    APIRequestTool, 
    FileOperationsTool,
    KnowledgeQueryTool,
    BashOperationsTool
)

# Legacy compatibility imports
from .delegate_agent import set_team_dependencies

__all__ = [
    # Base classes
    "BaseTool",
    "SimpleStringTool", 
    "ToolRegistry",
    "ToolManager",
    "ToolLoader",
    
    # Global instances
    "tool_registry",
    "tool_manager",
    
    # Built-in tools
    "DelegateAgentTool",
    "APIRequestTool",
    "FileOperationsTool", 
    "KnowledgeQueryTool",
    "BashOperationsTool",
    
    # Legacy compatibility
    "set_team_dependencies",
]