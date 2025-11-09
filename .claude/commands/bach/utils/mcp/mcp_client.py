#!/usr/bin/env python3
"""
MCP Client Integrations for Bach Research System
Implements MCP clients for various scientific databases and research tools

Provides MCP connections to:
- Scientific database MCP servers
- Research tool MCP servers  
- Data analysis MCP servers
- Custom research MCP implementations
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

# MCP Client imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP library not available")


@dataclass
class MCPServerConfig:
    """Configuration for MCP server connection"""
    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    description: str = ""
    capabilities: List[str] = None


class MCPConnectionManager:
    """Manages connections to multiple MCP servers"""
    
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.server_configs: Dict[str, MCPServerConfig] = {}
        self.available = MCP_AVAILABLE
    
    async def register_server(self, config: MCPServerConfig) -> bool:
        """Register and connect to an MCP server"""
        if not self.available:
            logging.error("MCP not available")
            return False
        
        try:
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env or {}
            )
            
            # Create client session
            session = await stdio_client(server_params)
            
            # Initialize the session
            await session.initialize()
            
            self.sessions[config.name] = session
            self.server_configs[config.name] = config
            
            logging.info(f"Connected to MCP server: {config.name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to connect to MCP server {config.name}: {e}")
            return False
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on an MCP server"""
        if server_name not in self.sessions:
            raise ValueError(f"MCP server {server_name} not connected")
        
        session = self.sessions[server_name]
        
        try:
            result = await session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logging.error(f"MCP tool call failed {server_name}.{tool_name}: {e}")
            raise
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools on an MCP server"""
        if server_name not in self.sessions:
            raise ValueError(f"MCP server {server_name} not connected")
        
        session = self.sessions[server_name]
        
        try:
            tools = await session.list_tools()
            return tools
        except Exception as e:
            logging.error(f"Failed to list tools for {server_name}: {e}")
            return []
    
    async def get_server_info(self, server_name: str) -> Dict[str, Any]:
        """Get information about an MCP server"""
        if server_name not in self.sessions:
            return {"connected": False, "error": "Not connected"}
        
        try:
            tools = await self.list_tools(server_name)
            config = self.server_configs[server_name]
            
            return {
                "connected": True,
                "name": config.name,
                "description": config.description,
                "capabilities": config.capabilities or [],
                "tools": [tool.get("name", "unknown") for tool in tools],
                "tool_count": len(tools)
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    async def close_all(self):
        """Close all MCP connections"""
        for name, session in self.sessions.items():
            try:
                await session.close()
                logging.info(f"Closed MCP connection: {name}")
            except Exception as e:
                logging.error(f"Error closing MCP connection {name}: {e}")
        
        self.sessions.clear()


class ResearchMCPClient:
    """High-level client for research-focused MCP operations"""
    
    def __init__(self):
        self.connection_manager = MCPConnectionManager()
        self.initialized = False
        
        # Define available research MCP servers (using existing implementations)
        self.research_servers = {
            "arxiv_mcp": MCPServerConfig(
                name="arxiv_mcp", 
                command="uv",
                args=["tool", "run", "arxiv-mcp-server", "--storage-path", os.path.expanduser("~/.arxiv-mcp-server/papers")],
                env={"TRANSPORT": "stdio"},
                description="arXiv preprint database access via existing MCP server",
                capabilities=["preprint_search", "paper_download", "fulltext_access", "metadata_extraction"]
            ),
            "brave_search_mcp": MCPServerConfig(
                name="brave_search_mcp",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-brave-search"],
                env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")},
                description="Brave Search for academic web content",
                capabilities=["web_search", "academic_content", "real_time_search"]
            ),
            "github_mcp": MCPServerConfig(
                name="github_mcp",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN", "")},
                description="GitHub repository search for research code and datasets",
                capabilities=["repository_search", "code_search", "dataset_discovery"]
            ),
            "filesystem_mcp": MCPServerConfig(
                name="filesystem_mcp",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "--allowed-directory", os.getcwd()],
                description="Local filesystem access for research data management",
                capabilities=["file_operations", "local_data_access", "result_storage"]
            ),
            "postgres_mcp": MCPServerConfig(
                name="postgres_mcp",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-postgres"],
                env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_CONNECTION_STRING", "")},
                description="PostgreSQL database for research data storage",
                capabilities=["data_storage", "query_execution", "result_persistence"]
            )
        }
    
    async def initialize(self, enable_servers: Optional[List[str]] = None) -> Dict[str, bool]:
        """Initialize MCP connections for research servers"""
        if not self.connection_manager.available:
            logging.warning("MCP not available, skipping initialization")
            return {}
        
        if enable_servers is None:
            # Default to commonly available MCP servers
            enable_servers = ["arxiv_mcp", "brave_search_mcp", "filesystem_mcp"]
        
        connection_results = {}
        
        for server_name in enable_servers:
            if server_name in self.research_servers:
                config = self.research_servers[server_name]
                
                # Check if required environment variables are set
                if server_name == "brave_search_mcp" and not os.getenv("BRAVE_API_KEY"):
                    logging.warning(f"BRAVE_API_KEY not set, skipping {server_name}")
                    connection_results[server_name] = False
                    continue
                elif server_name == "github_mcp" and not os.getenv("GITHUB_TOKEN"):
                    logging.warning(f"GITHUB_TOKEN not set, skipping {server_name}")
                    connection_results[server_name] = False
                    continue
                elif server_name == "postgres_mcp" and not os.getenv("POSTGRES_CONNECTION_STRING"):
                    logging.warning(f"POSTGRES_CONNECTION_STRING not set, skipping {server_name}")
                    connection_results[server_name] = False
                    continue
                
                success = await self.connection_manager.register_server(config)
                connection_results[server_name] = success
            else:
                logging.warning(f"Unknown research MCP server: {server_name}")
                connection_results[server_name] = False
        
        self.initialized = True
        return connection_results
    
    async def search_papers(self, server_name: str, query: str, limit: int = 100, 
                          filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for papers using MCP server"""
        if not self.initialized:
            await self.initialize()
        
        arguments = {
            "query": query,
            "limit": limit
        }
        
        if filters:
            arguments.update(filters)
        
        try:
            result = await self.connection_manager.call_tool(server_name, "search_papers", arguments)
            
            # Standardize result format
            if isinstance(result, dict) and "papers" in result:
                return result["papers"]
            elif isinstance(result, list):
                return result
            else:
                logging.warning(f"Unexpected result format from {server_name}")
                return []
                
        except Exception as e:
            logging.error(f"Paper search failed on {server_name}: {e}")
            return []
    
    async def analyze_paper(self, server_name: str, paper_id: str, 
                          analysis_type: str = "full") -> Dict[str, Any]:
        """Analyze a paper using MCP research tools"""
        if not self.initialized:
            await self.initialize()
        
        arguments = {
            "paper_id": paper_id,
            "analysis_type": analysis_type
        }
        
        try:
            result = await self.connection_manager.call_tool(server_name, "analyze_paper", arguments)
            return result
        except Exception as e:
            logging.error(f"Paper analysis failed on {server_name}: {e}")
            return {}
    
    async def extract_citations(self, server_name: str, text: str) -> List[Dict[str, Any]]:
        """Extract citations from text using MCP tools"""
        if not self.initialized:
            await self.initialize()
        
        arguments = {"text": text}
        
        try:
            result = await self.connection_manager.call_tool(server_name, "extract_citations", arguments)
            
            if isinstance(result, dict) and "citations" in result:
                return result["citations"]
            elif isinstance(result, list):
                return result
            else:
                return []
                
        except Exception as e:
            logging.error(f"Citation extraction failed on {server_name}: {e}")
            return []
    
    async def assess_quality(self, server_name: str, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess paper quality using MCP research tools"""
        if not self.initialized:
            await self.initialize()
        
        arguments = {"paper_data": paper_data}
        
        try:
            result = await self.connection_manager.call_tool(server_name, "assess_quality", arguments)
            return result
        except Exception as e:
            logging.error(f"Quality assessment failed on {server_name}: {e}")
            return {}
    
    async def perform_statistical_analysis(self, server_name: str, data: Dict[str, Any], 
                                         analysis_type: str) -> Dict[str, Any]:
        """Perform statistical analysis using MCP data analysis tools"""
        if not self.initialized:
            await self.initialize()
        
        arguments = {
            "data": data,
            "analysis_type": analysis_type
        }
        
        try:
            result = await self.connection_manager.call_tool(server_name, "statistical_analysis", arguments)
            return result
        except Exception as e:
            logging.error(f"Statistical analysis failed on {server_name}: {e}")
            return {}
    
    async def get_available_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities of all connected MCP servers"""
        capabilities = {}
        
        for server_name in self.research_servers.keys():
            server_info = await self.connection_manager.get_server_info(server_name)
            capabilities[server_name] = server_info
        
        return capabilities
    
    async def health_check(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all MCP connections"""
        health_status = {}
        
        for server_name in self.research_servers.keys():
            try:
                # Try a simple operation to test connectivity
                tools = await self.connection_manager.list_tools(server_name)
                health_status[server_name] = {
                    "healthy": True,
                    "connected": True,
                    "tool_count": len(tools),
                    "last_check": datetime.now().isoformat()
                }
            except Exception as e:
                health_status[server_name] = {
                    "healthy": False,
                    "connected": False,
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
        
        return health_status
    
    async def close(self):
        """Close all MCP connections"""
        await self.connection_manager.close_all()


# Specific MCP database clients
class SemanticScholarMCP:
    """Semantic Scholar specific MCP client"""
    
    def __init__(self, client: ResearchMCPClient):
        self.client = client
        self.server_name = "semantic_scholar_mcp"
    
    async def search(self, query: str, limit: int = 100, 
                   year_range: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Search Semantic Scholar via MCP"""
        filters = {}
        if year_range:
            filters["year_min"] = year_range[0]
            filters["year_max"] = year_range[1]
        
        return await self.client.search_papers(self.server_name, query, limit, filters)
    
    async def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """Get detailed paper information"""
        return await self.client.analyze_paper(self.server_name, paper_id, "detailed")
    
    async def get_citations(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get paper citations"""
        result = await self.client.connection_manager.call_tool(
            self.server_name, "get_citations", {"paper_id": paper_id}
        )
        return result.get("citations", [])


class ArxivMCP:
    """arXiv specific MCP client using existing arxiv-mcp-server"""
    
    def __init__(self, client: ResearchMCPClient):
        self.client = client
        self.server_name = "arxiv_mcp"
    
    async def search(self, query: str, limit: int = 100, 
                   categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search arXiv via existing MCP server"""
        # Use the search_papers tool from arxiv-mcp-server
        arguments = {
            "query": query,
            "max_results": limit
        }
        
        if categories:
            arguments["categories"] = categories
        
        return await self.client.search_papers(self.server_name, query, limit, arguments)
    
    async def get_paper(self, arxiv_id: str) -> Dict[str, Any]:
        """Get paper details using arxiv-mcp-server"""
        try:
            result = await self.client.connection_manager.call_tool(
                self.server_name, "get_paper", {"arxiv_id": arxiv_id}
            )
            return result
        except Exception as e:
            logging.error(f"Failed to get arXiv paper {arxiv_id}: {e}")
            return {}
    
    async def download_paper(self, arxiv_id: str, storage_path: Optional[str] = None) -> str:
        """Download paper PDF using arxiv-mcp-server"""
        try:
            arguments = {"arxiv_id": arxiv_id}
            if storage_path:
                arguments["storage_path"] = storage_path
            
            result = await self.client.connection_manager.call_tool(
                self.server_name, "download_paper", arguments
            )
            return result.get("file_path", "")
        except Exception as e:
            logging.error(f"Failed to download arXiv paper {arxiv_id}: {e}")
            return ""


class BraveSearchMCP:
    """Brave Search MCP client for academic web content"""
    
    def __init__(self, client: ResearchMCPClient):
        self.client = client
        self.server_name = "brave_search_mcp"
    
    async def search_academic(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for academic content using Brave Search"""
        try:
            # Add academic-specific query modifiers
            academic_query = f"{query} site:arxiv.org OR site:pubmed.ncbi.nlm.nih.gov OR site:scholar.google.com OR filetype:pdf"
            
            result = await self.client.connection_manager.call_tool(
                self.server_name, "search", {
                    "query": academic_query,
                    "count": limit
                }
            )
            
            return result.get("results", [])
        except Exception as e:
            logging.error(f"Brave search failed: {e}")
            return []


class GitHubMCP:
    """GitHub MCP client for research code and datasets"""
    
    def __init__(self, client: ResearchMCPClient):
        self.client = client
        self.server_name = "github_mcp"
    
    async def search_repositories(self, query: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search GitHub repositories for research-related code"""
        try:
            search_query = f"{query} research OR dataset OR analysis"
            if language:
                search_query += f" language:{language}"
            
            result = await self.client.connection_manager.call_tool(
                self.server_name, "search_repositories", {
                    "query": search_query,
                    "per_page": 30
                }
            )
            
            return result.get("items", [])
        except Exception as e:
            logging.error(f"GitHub search failed: {e}")
            return []
    
    async def get_repository_content(self, owner: str, repo: str, path: str = "") -> Dict[str, Any]:
        """Get repository content for research datasets"""
        try:
            result = await self.client.connection_manager.call_tool(
                self.server_name, "get_contents", {
                    "owner": owner,
                    "repo": repo,
                    "path": path
                }
            )
            
            return result
        except Exception as e:
            logging.error(f"Failed to get GitHub content {owner}/{repo}/{path}: {e}")
            return {}


class PubmedMCP:
    """PubMed specific MCP client"""
    
    def __init__(self, client: ResearchMCPClient):
        self.client = client
        self.server_name = "pubmed_mcp"
    
    async def search(self, query: str, limit: int = 100, 
                   mesh_terms: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search PubMed via MCP"""
        filters = {}
        if mesh_terms:
            filters["mesh_terms"] = mesh_terms
        
        return await self.client.search_papers(self.server_name, query, limit, filters)
    
    async def get_mesh_terms(self, pmid: str) -> List[str]:
        """Get MeSH terms for a paper"""
        result = await self.client.connection_manager.call_tool(
            self.server_name, "get_mesh_terms", {"pmid": pmid}
        )
        return result.get("mesh_terms", [])


# Convenience factory function
async def create_research_mcp_client(enable_servers: Optional[List[str]] = None) -> ResearchMCPClient:
    """Factory function to create and initialize research MCP client with existing servers"""
    if enable_servers is None:
        # Default to commonly available servers
        enable_servers = [
            "arxiv_mcp",        # arxiv-mcp-server via uv
            "brave_search_mcp", # @modelcontextprotocol/server-brave-search 
            "filesystem_mcp"    # @modelcontextprotocol/server-filesystem
        ]
    
    client = ResearchMCPClient()
    connection_results = await client.initialize(enable_servers)
    
    # Log connection status
    for server, connected in connection_results.items():
        if connected:
            logging.info(f"✓ Connected to {server}")
        else:
            logging.warning(f"✗ Failed to connect to {server}")
    
    return client


def get_installation_commands() -> Dict[str, str]:
    """Get installation commands for available MCP servers"""
    return {
        "arxiv_mcp": "uv tool install arxiv-mcp-server",
        "brave_search_mcp": "npm install -g @modelcontextprotocol/server-brave-search",
        "github_mcp": "npm install -g @modelcontextprotocol/server-github", 
        "filesystem_mcp": "npm install -g @modelcontextprotocol/server-filesystem",
        "postgres_mcp": "npm install -g @modelcontextprotocol/server-postgres"
    }


def get_required_env_vars() -> Dict[str, List[str]]:
    """Get required environment variables for each MCP server"""
    return {
        "arxiv_mcp": ["ARXIV_STORAGE_PATH (optional)"],
        "brave_search_mcp": ["BRAVE_API_KEY (required)"],
        "github_mcp": ["GITHUB_TOKEN (required)"],
        "filesystem_mcp": [],
        "postgres_mcp": ["POSTGRES_CONNECTION_STRING (required)"]
    }


# Example usage
if __name__ == "__main__":
    async def main():
        print("Available MCP servers for Bach research:")
        print("\nInstallation commands:")
        for server, cmd in get_installation_commands().items():
            print(f"  {server}: {cmd}")
        
        print("\nRequired environment variables:")
        for server, vars in get_required_env_vars().items():
            print(f"  {server}: {', '.join(vars) if vars else 'None required'}")
        
        # Create and initialize MCP client with existing servers
        client = await create_research_mcp_client([
            "arxiv_mcp",
            "filesystem_mcp"  # These don't require API keys
        ])
        
        try:
            # Check health
            health = await client.health_check()
            print("\nMCP Health Status:")
            for server, status in health.items():
                print(f"  {server}: {'✓' if status['healthy'] else '✗'}")
            
            # Test arXiv search if available
            if health.get("arxiv_mcp", {}).get("healthy"):
                arxiv_client = ArxivMCP(client)
                papers = await arxiv_client.search("machine learning", limit=5)
                print(f"\nFound {len(papers)} arXiv papers")
                
        finally:
            await client.close()
    
    if MCP_AVAILABLE:
        asyncio.run(main())
    else:
        print("MCP not available. Install with: pip install mcp")