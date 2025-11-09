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
        
        # Define available research MCP servers
        self.research_servers = {
            "semantic_scholar_mcp": MCPServerConfig(
                name="semantic_scholar_mcp",
                command="semantic-scholar-mcp-server",
                args=[],
                description="Semantic Scholar database access via MCP",
                capabilities=["paper_search", "citation_analysis", "author_lookup"]
            ),
            "arxiv_mcp": MCPServerConfig(
                name="arxiv_mcp", 
                command="arxiv-mcp-server",
                args=[],
                description="arXiv preprint database access via MCP",
                capabilities=["preprint_search", "category_filtering", "fulltext_access"]
            ),
            "pubmed_mcp": MCPServerConfig(
                name="pubmed_mcp",
                command="pubmed-mcp-server", 
                args=[],
                description="PubMed biomedical database access via MCP",
                capabilities=["biomedical_search", "mesh_terms", "clinical_trials"]
            ),
            "research_tools_mcp": MCPServerConfig(
                name="research_tools_mcp",
                command="research-tools-mcp-server",
                args=[],
                description="Research analysis tools via MCP",
                capabilities=["text_analysis", "citation_extraction", "quality_assessment"]
            ),
            "data_analysis_mcp": MCPServerConfig(
                name="data_analysis_mcp",
                command="data-analysis-mcp-server",
                args=[],
                description="Data analysis and visualization tools",
                capabilities=["statistical_analysis", "plotting", "data_processing"]
            )
        }
    
    async def initialize(self, enable_servers: Optional[List[str]] = None) -> Dict[str, bool]:
        """Initialize MCP connections for research servers"""
        if not self.connection_manager.available:
            logging.warning("MCP not available, skipping initialization")
            return {}
        
        if enable_servers is None:
            enable_servers = list(self.research_servers.keys())
        
        connection_results = {}
        
        for server_name in enable_servers:
            if server_name in self.research_servers:
                config = self.research_servers[server_name]
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
    """arXiv specific MCP client"""
    
    def __init__(self, client: ResearchMCPClient):
        self.client = client
        self.server_name = "arxiv_mcp"
    
    async def search(self, query: str, limit: int = 100, 
                   categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search arXiv via MCP"""
        filters = {}
        if categories:
            filters["categories"] = categories
        
        return await self.client.search_papers(self.server_name, query, limit, filters)
    
    async def get_fulltext(self, arxiv_id: str) -> str:
        """Get full text of arXiv paper"""
        result = await self.client.connection_manager.call_tool(
            self.server_name, "get_fulltext", {"arxiv_id": arxiv_id}
        )
        return result.get("fulltext", "")


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
    """Factory function to create and initialize research MCP client"""
    client = ResearchMCPClient()
    await client.initialize(enable_servers)
    return client


# Example usage
if __name__ == "__main__":
    async def main():
        # Create and initialize MCP client
        client = await create_research_mcp_client([
            "semantic_scholar_mcp",
            "arxiv_mcp",
            "research_tools_mcp"
        ])
        
        try:
            # Check health
            health = await client.health_check()
            print("MCP Health Status:")
            for server, status in health.items():
                print(f"  {server}: {'✓' if status['healthy'] else '✗'}")
            
            # Search for papers
            papers = await client.search_papers(
                "semantic_scholar_mcp",
                "machine learning in healthcare",
                limit=10
            )
            
            print(f"\nFound {len(papers)} papers")
            
            # Analyze first paper if available
            if papers:
                analysis = await client.analyze_paper(
                    "research_tools_mcp",
                    papers[0].get("id", ""),
                    "quality"
                )
                print(f"Analysis result: {analysis}")
                
        finally:
            await client.close()
    
    if MCP_AVAILABLE:
        asyncio.run(main())
    else:
        print("MCP not available, skipping example")