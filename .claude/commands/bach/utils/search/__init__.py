"""
Bach Search Utils Package
Comprehensive search utilities with MCP integration and API capabilities
"""

from .search_manager import (
    BachSearchManager,
    SearchConfig, 
    SearchStrategy,
    SearchResult,
    search_literature,
    search_with_config
)

from .mcp_client import (
    ResearchMCPClient,
    SemanticScholarMCP,
    ArxivMCP,
    PubmedMCP,
    create_research_mcp_client
)

from .enhanced_api import (
    EnhancedAPIManager,
    enhanced_search,
    search_with_datasets
)

from .remote_datasets import (
    RemoteDatasetManager,
    DatasetInfo,
    DatasetType,
    search_remote_datasets,
    get_dataset_repositories
)

from .search_integration import (
    BachSearchOrchestrator,
    UnifiedSearchConfig,
    unified_search,
    quick_paper_search,
    comprehensive_research_search
)

__all__ = [
    # Main orchestrator
    'BachSearchOrchestrator',
    'UnifiedSearchConfig',
    
    # Search managers
    'BachSearchManager',
    'ResearchMCPClient', 
    'EnhancedAPIManager',
    'RemoteDatasetManager',
    
    # Configuration classes
    'SearchConfig',
    'SearchStrategy',
    'SearchResult',
    'DatasetInfo',
    'DatasetType',
    
    # Convenience functions
    'unified_search',
    'quick_paper_search',
    'comprehensive_research_search',
    'search_literature',
    'enhanced_search',
    'search_remote_datasets',
    
    # MCP specific
    'SemanticScholarMCP',
    'ArxivMCP', 
    'PubmedMCP',
    'create_research_mcp_client',
    
    # Utility functions
    'search_with_config',
    'search_with_datasets',
    'get_dataset_repositories'
]