"""
Shared schemas and base classes for the Gnosari framework.

This package contains comprehensive schema definitions for all aspects
of the Gnosari AI Teams system, organized by domain.
"""

from .base import BaseIOSchema, BaseToolConfig, BaseTool

# Legacy schemas for backward compatibility
from typing import Dict, List, Optional, Any
from pydantic import Field, field_validator


class ActionSchema(BaseIOSchema):
    """Schema for defining the next step action."""
    type: str = Field(
        default="execute_tool",
        description="The type of action to take next (must be 'execute_tool')"
    )
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        # During streaming, we might get partial values like "execut"
        # Allow partial matches that could be building towards "execute_tool"
        if v and v not in ["execute_tool", "execut", "execute", "execute_", "execute_t", "execute_to", "execute_too"]:
            if not "execute_tool".startswith(v):
                raise ValueError("type must be 'execute_tool'")
        return v or "execute_tool"
    tool_name: Optional[str] = Field(
        default=None,
        description = "The tool name to execute, if any."
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="The parameters for the next action"
    )


class NextStepSchema(BaseIOSchema):
    """Schema for defining the next step in agent execution."""
    
    action: Optional[ActionSchema] = Field(
        default=None,
        description="Next action to execute."
    )
    message: Optional[str] = Field(
        default=None, 
        description="Message to send to the target agent or tool"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional context or parameters for the action"
    )


class TeamAgentInputSchema(BaseIOSchema):
    """Input schema for team agents - always a string message."""

    message: str = Field(..., description="The message to process.")
    tool_results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Results from previous tool executions")
    iteration: Optional[int] = Field(default=1, description="Current iteration number")
    original_request: Optional[str] = Field(default=None, description="Original user request")


class TeamAgentOutputSchema(BaseIOSchema):
    """Output schema for team agents - includes reasoning and final response."""

    reasoning: str = Field(..., description="The reasoning process leading to the final response")
    response: str = Field(..., description="The final response to the message.")
    is_done: Optional[bool] = Field(default=False, description="Whether the agent has completed its task")
    next_step: Optional[NextStepSchema] = Field(default=None, description="Next step to execute with detailed action information")
    agent_name: Optional[str] = Field(default=None, description="Name of the agent generating this response")


# Import domain-specific schemas
from .agent import (
    AgentCreateRequest, AgentResponse, AgentExecutionRequest, 
    AgentExecutionResponse, AgentHandoffRequest, AgentStatus,
    AgentMetrics, AgentConfigUpdate
)

from .team import (
    KnowledgeBaseConfig, ToolConfig, TeamCreateRequest, TeamResponse,
    TeamExecutionRequest, TeamExecutionResponse, TeamStatus, 
    TeamMetrics, TeamConfigUpdate, HandoffEvent, ExecutionEvent
)

from .tool import (
    ToolDefinition, ToolExecutionRequest, ToolExecutionResponse,
    ToolRegistrationRequest, ToolInfo, MCPServerConfig, MCPToolInfo,
    ToolUsageMetrics, ToolRegistry, ToolSearchRequest, ToolSearchResponse,
    BulkToolExecutionRequest, BulkToolExecutionResponse
)

from .config import (
    LogLevel, ProviderType, ConnectionType, GlobalConfig, ProviderConfig,
    KnowledgeConfig, ToolConfigSchema, AgentConfigSchema, TeamConfigSchema,
    ConfigValidationResult, ConfigUpdateRequest, ConfigBackup, ConfigMigration
)

__all__ = [
    # Base classes
    "BaseIOSchema",
    "BaseToolConfig", 
    "BaseTool",
    
    # Legacy schemas (backward compatibility)
    "ActionSchema",
    "NextStepSchema",
    "TeamAgentInputSchema",
    "TeamAgentOutputSchema",
    
    # Agent schemas
    "AgentCreateRequest",
    "AgentResponse", 
    "AgentExecutionRequest",
    "AgentExecutionResponse",
    "AgentHandoffRequest",
    "AgentStatus",
    "AgentMetrics",
    "AgentConfigUpdate",
    
    # Team schemas
    "KnowledgeBaseConfig",
    "ToolConfig", 
    "TeamCreateRequest",
    "TeamResponse",
    "TeamExecutionRequest",
    "TeamExecutionResponse", 
    "TeamStatus",
    "TeamMetrics",
    "TeamConfigUpdate",
    "HandoffEvent",
    "ExecutionEvent",
    
    # Tool schemas
    "ToolDefinition",
    "ToolExecutionRequest",
    "ToolExecutionResponse",
    "ToolRegistrationRequest",
    "ToolInfo",
    "MCPServerConfig",
    "MCPToolInfo", 
    "ToolUsageMetrics",
    "ToolRegistry",
    "ToolSearchRequest",
    "ToolSearchResponse",
    "BulkToolExecutionRequest",
    "BulkToolExecutionResponse",
    
    # Config schemas
    "LogLevel",
    "ProviderType",
    "ConnectionType", 
    "GlobalConfig",
    "ProviderConfig",
    "KnowledgeConfig",
    "ToolConfigSchema",
    "AgentConfigSchema", 
    "TeamConfigSchema",
    "ConfigValidationResult",
    "ConfigUpdateRequest",
    "ConfigBackup",
    "ConfigMigration"
]