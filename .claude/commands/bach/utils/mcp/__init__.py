"""
Bach MCP Utils Package
Model Context Protocol integrations for research operations using existing MCP servers
"""

from .mcp_client import (
    ResearchMCPClient,
    MCPConnectionManager,
    ArxivMCP,
    BraveSearchMCP,
    GitHubMCP,
    create_research_mcp_client,
    get_installation_commands,
    get_required_env_vars
)

__all__ = [
    'ResearchMCPClient',
    'MCPConnectionManager', 
    'ArxivMCP',
    'BraveSearchMCP', 
    'GitHubMCP',
    'create_research_mcp_client',
    'get_installation_commands',
    'get_required_env_vars'
]