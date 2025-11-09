#!/usr/bin/env python3
"""
Bach Utils Main Package
Comprehensive research utilities for the Bach system

Provides unified access to:
- Search management with MCP and API integration
- Research task execution and CLI tools
- Remote dataset access capabilities
- Enhanced API integrations
"""

from .search_integration import (
    BachSearchOrchestrator,
    UnifiedSearchConfig,
    unified_search,
    quick_paper_search,
    comprehensive_research_search
)

from .research_executor_cli import ResearchExecutorCLI

# Import subpackages
from . import search
from . import mcp  
from . import apis

__version__ = "1.0.0"

__all__ = [
    # Main search orchestration
    'BachSearchOrchestrator',
    'UnifiedSearchConfig',
    'unified_search',
    'quick_paper_search', 
    'comprehensive_research_search',
    
    # Research execution
    'ResearchExecutorCLI',
    
    # Subpackages
    'search',
    'mcp',
    'apis'
]

# Convenience imports for common operations
def create_search_orchestrator(api_keys=None):
    """Create a Bach search orchestrator with API keys"""
    return BachSearchOrchestrator(api_keys)

def get_available_databases():
    """Get list of available database sources"""
    return [
        "semantic_scholar",
        "arxiv", 
        "pubmed",
        "crossref",
        "openalex",
        "ncbi_genomes",
        "ncbi_sra",
        "ebi_pride",
        "ebi_arrayexpress", 
        "ebi_ena",
        "ebi_chembl",
        "data_gov",
        "eu_data"
    ]