#!/usr/bin/env python3
"""
Bach Research Search Manager
Comprehensive search coordination with MCP integration and direct API calls

Provides unified interface for:
- MCP-based search where available and efficient
- Direct API calls where MCP adds overhead
- Multi-database coordination and deduplication
- Search strategy optimization
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

# Import MCP client capabilities
try:
    import mcp_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP client not available, using direct API calls only")

# Import our API integrations
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'agents', 'paper_search'))
from api_integrations import APIIntegrationManager


class SearchStrategy(Enum):
    """Search execution strategy"""
    MCP_FIRST = "mcp_first"      # Try MCP first, fallback to API
    API_ONLY = "api_only"        # Direct API calls only
    MCP_ONLY = "mcp_only"        # MCP only (fail if unavailable)
    HYBRID = "hybrid"            # Use both in parallel, merge results


@dataclass
class SearchConfig:
    """Search configuration parameters"""
    databases: List[str]
    max_results_per_db: int = 100
    total_max_results: int = 500
    strategy: SearchStrategy = SearchStrategy.MCP_FIRST
    enable_deduplication: bool = True
    quality_threshold: float = 0.0
    date_range: Optional[Dict[str, str]] = None  # {"start": "2020-01-01", "end": "2024-12-31"}
    search_timeout: int = 60  # seconds


@dataclass
class SearchResult:
    """Standardized search result structure"""
    id: str
    title: str
    abstract: str
    authors: List[Dict[str, str]]
    year: Optional[int]
    source: str
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    doi: Optional[str] = None
    citation_count: Optional[int] = None
    venue: Optional[str] = None
    quality_score: Optional[float] = None
    retrieved_at: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if not self.retrieved_at:
            self.retrieved_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class MCPSearchProvider:
    """MCP-based search provider for scientific databases"""
    
    def __init__(self):
        self.available = MCP_AVAILABLE
        self.clients = {}
        
    async def initialize(self):
        """Initialize MCP clients for available databases"""
        if not self.available:
            return False
            
        try:
            # Initialize Semantic Scholar MCP client
            if await self._init_semantic_scholar_mcp():
                logging.info("Semantic Scholar MCP client initialized")
                
            # Initialize arXiv MCP client
            if await self._init_arxiv_mcp():
                logging.info("arXiv MCP client initialized")
                
            # Initialize PubMed MCP client
            if await self._init_pubmed_mcp():
                logging.info("PubMed MCP client initialized")
                
            return len(self.clients) > 0
            
        except Exception as e:
            logging.error(f"MCP initialization failed: {e}")
            return False
    
    async def _init_semantic_scholar_mcp(self) -> bool:
        """Initialize Semantic Scholar MCP client"""
        try:
            # This would connect to a Semantic Scholar MCP server
            # Implementation depends on available MCP servers
            self.clients['semantic_scholar'] = None  # Placeholder
            return False  # Not implemented yet
        except Exception:
            return False
    
    async def _init_arxiv_mcp(self) -> bool:
        """Initialize arXiv MCP client"""
        try:
            # This would connect to an arXiv MCP server
            self.clients['arxiv'] = None  # Placeholder
            return False  # Not implemented yet
        except Exception:
            return False
    
    async def _init_pubmed_mcp(self) -> bool:
        """Initialize PubMed MCP client"""
        try:
            # This would connect to a PubMed MCP server
            self.clients['pubmed'] = None  # Placeholder
            return False  # Not implemented yet
        except Exception:
            return False
    
    def is_available(self, database: str) -> bool:
        """Check if MCP client is available for database"""
        return database in self.clients and self.clients[database] is not None
    
    async def search(self, database: str, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search via MCP client"""
        if not self.is_available(database):
            raise ValueError(f"MCP client for {database} not available")
        
        try:
            client = self.clients[database]
            # MCP search call would go here
            # This is a placeholder implementation
            results = []
            
            # Convert to standardized format
            standardized = []
            for result in results:
                standardized.append(self._standardize_result(result, database))
            
            return standardized
            
        except Exception as e:
            logging.error(f"MCP search error for {database}: {e}")
            raise
    
    def _standardize_result(self, result: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Standardize MCP result to common format"""
        # Convert MCP result format to our standardized format
        # Implementation depends on MCP server response format
        return {
            "id": result.get("id", ""),
            "title": result.get("title", ""),
            "abstract": result.get("abstract", ""),
            "authors": result.get("authors", []),
            "year": result.get("year"),
            "source": source,
            "url": result.get("url"),
            "pdf_url": result.get("pdf_url"),
            "retrieved_via": "mcp"
        }


class BachSearchManager:
    """Main search manager coordinating MCP and API strategies"""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_manager = APIIntegrationManager(api_keys)
        self.mcp_provider = MCPSearchProvider()
        self.initialized = False
        
    async def initialize(self):
        """Initialize search providers"""
        if self.initialized:
            return
            
        # Initialize MCP provider
        mcp_success = await self.mcp_provider.initialize()
        logging.info(f"MCP initialization: {'success' if mcp_success else 'failed'}")
        
        self.initialized = True
    
    async def search(self, query: str, config: SearchConfig) -> List[SearchResult]:
        """Execute search with specified configuration"""
        if not self.initialized:
            await self.initialize()
        
        results = []
        
        if config.strategy == SearchStrategy.MCP_FIRST:
            results = await self._search_mcp_first(query, config)
        elif config.strategy == SearchStrategy.API_ONLY:
            results = await self._search_api_only(query, config)
        elif config.strategy == SearchStrategy.MCP_ONLY:
            results = await self._search_mcp_only(query, config)
        elif config.strategy == SearchStrategy.HYBRID:
            results = await self._search_hybrid(query, config)
        
        # Post-process results
        if config.enable_deduplication:
            results = self._deduplicate_results(results)
        
        # Apply quality filtering
        if config.quality_threshold > 0:
            results = [r for r in results if (r.quality_score or 0) >= config.quality_threshold]
        
        # Apply date filtering
        if config.date_range:
            results = self._filter_by_date(results, config.date_range)
        
        # Limit total results
        if len(results) > config.total_max_results:
            results = results[:config.total_max_results]
        
        return results
    
    async def _search_mcp_first(self, query: str, config: SearchConfig) -> List[SearchResult]:
        """Try MCP first, fallback to API"""
        results = []
        
        for db in config.databases:
            try:
                # Try MCP first
                if self.mcp_provider.is_available(db):
                    mcp_results = await self.mcp_provider.search(db, query, config.max_results_per_db)
                    results.extend([self._dict_to_search_result(r) for r in mcp_results])
                    logging.info(f"Used MCP for {db}: {len(mcp_results)} results")
                else:
                    # Fallback to API
                    api_results = await self.api_manager.search(db, query, config.max_results_per_db)
                    results.extend([self._dict_to_search_result(r) for r in api_results])
                    logging.info(f"Used API for {db}: {len(api_results)} results")
                    
            except Exception as e:
                logging.error(f"Search failed for {db}: {e}")
                continue
        
        return results
    
    async def _search_api_only(self, query: str, config: SearchConfig) -> List[SearchResult]:
        """Use API calls only"""
        results = []
        
        for db in config.databases:
            try:
                api_results = await self.api_manager.search(db, query, config.max_results_per_db)
                results.extend([self._dict_to_search_result(r) for r in api_results])
                logging.info(f"API search {db}: {len(api_results)} results")
            except Exception as e:
                logging.error(f"API search failed for {db}: {e}")
                continue
        
        return results
    
    async def _search_mcp_only(self, query: str, config: SearchConfig) -> List[SearchResult]:
        """Use MCP only, fail if unavailable"""
        results = []
        
        for db in config.databases:
            if not self.mcp_provider.is_available(db):
                raise ValueError(f"MCP not available for {db}")
            
            try:
                mcp_results = await self.mcp_provider.search(db, query, config.max_results_per_db)
                results.extend([self._dict_to_search_result(r) for r in mcp_results])
                logging.info(f"MCP search {db}: {len(mcp_results)} results")
            except Exception as e:
                logging.error(f"MCP search failed for {db}: {e}")
                raise
        
        return results
    
    async def _search_hybrid(self, query: str, config: SearchConfig) -> List[SearchResult]:
        """Use both MCP and API in parallel, merge results"""
        all_tasks = []
        
        for db in config.databases:
            # Add MCP task if available
            if self.mcp_provider.is_available(db):
                task = asyncio.create_task(
                    self._search_single_mcp(db, query, config.max_results_per_db)
                )
                all_tasks.append(task)
            
            # Add API task
            task = asyncio.create_task(
                self._search_single_api(db, query, config.max_results_per_db)
            )
            all_tasks.append(task)
        
        # Execute all searches in parallel
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # Combine successful results
        combined = []
        for result in results:
            if isinstance(result, list):
                combined.extend(result)
            elif isinstance(result, Exception):
                logging.error(f"Hybrid search task failed: {result}")
        
        return combined
    
    async def _search_single_mcp(self, db: str, query: str, limit: int) -> List[SearchResult]:
        """Single MCP search task"""
        try:
            mcp_results = await self.mcp_provider.search(db, query, limit)
            return [self._dict_to_search_result(r) for r in mcp_results]
        except Exception as e:
            logging.error(f"MCP search failed for {db}: {e}")
            return []
    
    async def _search_single_api(self, db: str, query: str, limit: int) -> List[SearchResult]:
        """Single API search task"""
        try:
            api_results = await self.api_manager.search(db, query, limit)
            return [self._dict_to_search_result(r) for r in api_results]
        except Exception as e:
            logging.error(f"API search failed for {db}: {e}")
            return []
    
    def _dict_to_search_result(self, data: Dict[str, Any]) -> SearchResult:
        """Convert dict to SearchResult object"""
        return SearchResult(
            id=data.get("id", data.get("paperId", "")),
            title=data.get("title", ""),
            abstract=data.get("abstract", data.get("summary", "")),
            authors=data.get("authors", []),
            year=data.get("year"),
            source=data.get("source", "unknown"),
            url=data.get("url"),
            pdf_url=data.get("pdf_url", data.get("openAccessPdf", {}).get("url") if isinstance(data.get("openAccessPdf"), dict) else None),
            doi=data.get("doi"),
            citation_count=data.get("citationCount"),
            venue=data.get("venue", data.get("journal")),
            quality_score=data.get("quality_score"),
            retrieved_at=data.get("retrieved_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {})
        )
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate papers based on title similarity and DOI"""
        seen_titles = set()
        seen_dois = set()
        unique_results = []
        
        for result in results:
            # Check DOI first (most reliable)
            if result.doi and result.doi in seen_dois:
                continue
            
            # Check title similarity (basic implementation)
            title_normalized = result.title.lower().strip()
            if title_normalized in seen_titles:
                continue
            
            # Add to unique results
            unique_results.append(result)
            if result.doi:
                seen_dois.add(result.doi)
            seen_titles.add(title_normalized)
        
        logging.info(f"Deduplication: {len(results)} -> {len(unique_results)} results")
        return unique_results
    
    def _filter_by_date(self, results: List[SearchResult], date_range: Dict[str, str]) -> List[SearchResult]:
        """Filter results by publication date range"""
        start_year = int(date_range.get("start", "1900")[:4])
        end_year = int(date_range.get("end", "2030")[:4])
        
        filtered = []
        for result in results:
            if result.year and start_year <= result.year <= end_year:
                filtered.append(result)
            elif not result.year:  # Include papers without year info
                filtered.append(result)
        
        logging.info(f"Date filtering: {len(results)} -> {len(filtered)} results")
        return filtered
    
    async def get_search_capabilities(self) -> Dict[str, Dict[str, bool]]:
        """Get capabilities of each search provider"""
        capabilities = {}
        
        # Check API capabilities
        api_health = await self.api_manager.check_api_health()
        capabilities["api"] = {
            db: status["healthy"] and status["available"] 
            for db, status in api_health.items()
        }
        
        # Check MCP capabilities
        capabilities["mcp"] = {
            "semantic_scholar": self.mcp_provider.is_available("semantic_scholar"),
            "arxiv": self.mcp_provider.is_available("arxiv"),
            "pubmed": self.mcp_provider.is_available("pubmed")
        }
        
        return capabilities
    
    async def optimize_search_strategy(self, query: str, target_databases: List[str]) -> SearchStrategy:
        """Automatically select optimal search strategy"""
        capabilities = await self.get_search_capabilities()
        
        # Count available providers
        mcp_available = sum(capabilities["mcp"].values())
        api_available = sum(capabilities["api"].values())
        
        # Decision logic
        if mcp_available == 0:
            return SearchStrategy.API_ONLY
        elif api_available == 0:
            return SearchStrategy.MCP_ONLY
        elif mcp_available >= len(target_databases) // 2:
            return SearchStrategy.MCP_FIRST
        else:
            return SearchStrategy.HYBRID
    
    async def close(self):
        """Close all connections"""
        await self.api_manager.close()


# Convenience functions for Bach commands
async def search_literature(query: str, databases: Optional[List[str]] = None, 
                          max_results: int = 200, api_keys: Optional[Dict[str, str]] = None) -> List[SearchResult]:
    """Convenience function for literature search"""
    if databases is None:
        databases = ["semantic_scholar", "arxiv", "pubmed"]
    
    config = SearchConfig(
        databases=databases,
        max_results_per_db=max_results // len(databases),
        total_max_results=max_results,
        strategy=SearchStrategy.MCP_FIRST,
        enable_deduplication=True
    )
    
    manager = BachSearchManager(api_keys)
    try:
        results = await manager.search(query, config)
        return results
    finally:
        await manager.close()


async def search_with_config(query: str, config_dict: Dict[str, Any], 
                           api_keys: Optional[Dict[str, str]] = None) -> List[SearchResult]:
    """Search with custom configuration"""
    config = SearchConfig(**config_dict)
    
    manager = BachSearchManager(api_keys)
    try:
        results = await manager.search(query, config)
        return results
    finally:
        await manager.close()


if __name__ == "__main__":
    # Example usage
    async def main():
        api_keys = {
            "semantic_scholar": os.getenv("SEMANTIC_SCHOLAR_API_KEY"),
            "pubmed": os.getenv("PUBMED_EMAIL")
        }
        
        results = await search_literature(
            "machine learning in healthcare",
            databases=["semantic_scholar", "arxiv"],
            max_results=50,
            api_keys=api_keys
        )
        
        print(f"Found {len(results)} papers")
        for result in results[:5]:
            print(f"- {result.title} ({result.year}) - {result.source}")
    
    asyncio.run(main())