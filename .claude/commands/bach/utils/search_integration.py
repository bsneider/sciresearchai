#!/usr/bin/env python3
"""
Bach Search Integration Layer
Unified interface combining MCP and API capabilities for efficient research search

Automatically chooses between MCP and API based on:
- Performance characteristics
- Data freshness requirements  
- Available capabilities
- Resource efficiency
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

# Import all search components
from .search_manager import BachSearchManager, SearchConfig, SearchStrategy, SearchResult
from .mcp_client import ResearchMCPClient
from .enhanced_api import EnhancedAPIManager
from .remote_datasets import RemoteDatasetManager, DatasetInfo, DatasetType


@dataclass
class UnifiedSearchConfig:
    """Unified search configuration"""
    # Search parameters
    query: str
    max_results: int = 200
    include_papers: bool = True
    include_datasets: bool = False
    
    # Source selection
    paper_sources: Optional[List[str]] = None  # ["semantic_scholar", "arxiv", "pubmed", "crossref", "openalex"]
    dataset_sources: Optional[List[str]] = None  # ["ncbi_genomes", "ebi_pride", "data_gov", etc.]
    
    # Strategy preferences
    prefer_mcp: bool = True
    fallback_to_api: bool = True
    enable_caching: bool = True
    
    # Filtering
    date_range: Optional[Dict[str, str]] = None
    dataset_types: Optional[List[str]] = None
    quality_threshold: float = 0.0
    
    # Performance
    timeout_seconds: int = 120
    parallel_execution: bool = True


class BachSearchOrchestrator:
    """Main orchestrator for all Bach search operations"""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        
        # Initialize search managers
        self.paper_manager = BachSearchManager(api_keys)
        self.enhanced_api = EnhancedAPIManager(api_keys)
        self.dataset_manager = RemoteDatasetManager()
        self.mcp_client = ResearchMCPClient()
        
        # Performance tracking
        self.search_metrics = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize all search components"""
        if self.initialized:
            return
        
        try:
            # Initialize paper search manager
            await self.paper_manager.initialize()
            
            # Initialize MCP client with existing servers
            await self.mcp_client.initialize([
                "arxiv_mcp",        # arxiv-mcp-server
                "brave_search_mcp", # Brave search MCP
                "filesystem_mcp"    # Filesystem MCP for storage
            ])
            
            self.initialized = True
            logging.info("Bach Search Orchestrator initialized successfully")
            
        except Exception as e:
            logging.error(f"Initialization failed: {e}")
            raise
    
    async def search(self, config: UnifiedSearchConfig) -> Dict[str, Any]:
        """Execute unified search across papers and datasets"""
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        results = {
            "query": config.query,
            "search_timestamp": datetime.now().isoformat(),
            "papers": [],
            "datasets": [],
            "metrics": {},
            "errors": []
        }
        
        search_tasks = []
        
        # Paper search
        if config.include_papers:
            paper_task = asyncio.create_task(
                self._search_papers(config)
            )
            search_tasks.append(("papers", paper_task))
        
        # Dataset search
        if config.include_datasets:
            dataset_task = asyncio.create_task(
                self._search_datasets(config)
            )
            search_tasks.append(("datasets", dataset_task))
        
        # Execute searches
        if config.parallel_execution:
            # Parallel execution
            for search_type, task in search_tasks:
                try:
                    search_results = await asyncio.wait_for(task, timeout=config.timeout_seconds)
                    results[search_type] = search_results
                except asyncio.TimeoutError:
                    results["errors"].append(f"{search_type} search timed out")
                    results[search_type] = []
                except Exception as e:
                    results["errors"].append(f"{search_type} search failed: {str(e)}")
                    results[search_type] = []
        else:
            # Sequential execution
            for search_type, task in search_tasks:
                try:
                    search_results = await task
                    results[search_type] = search_results
                except Exception as e:
                    results["errors"].append(f"{search_type} search failed: {str(e)}")
                    results[search_type] = []
        
        # Add performance metrics
        total_time = time.time() - start_time
        results["metrics"] = {
            "total_search_time": total_time,
            "papers_found": len(results["papers"]),
            "datasets_found": len(results["datasets"]),
            "total_results": len(results["papers"]) + len(results["datasets"]),
            "search_efficiency": (len(results["papers"]) + len(results["datasets"])) / total_time if total_time > 0 else 0
        }
        
        return results
    
    async def _search_papers(self, config: UnifiedSearchConfig) -> List[Dict[str, Any]]:
        """Search for papers using optimal strategy"""
        
        # Determine search strategy
        strategy = await self._determine_paper_strategy(config)
        
        try:
            if strategy == "mcp_primary" and config.prefer_mcp:
                return await self._search_papers_mcp_primary(config)
            elif strategy == "api_primary" or not config.prefer_mcp:
                return await self._search_papers_api_primary(config)
            elif strategy == "hybrid":
                return await self._search_papers_hybrid(config)
            else:
                return await self._search_papers_fallback(config)
                
        except Exception as e:
            if config.fallback_to_api:
                logging.warning(f"Primary paper search failed, falling back: {e}")
                return await self._search_papers_fallback(config)
            else:
                raise
    
    async def _search_datasets(self, config: UnifiedSearchConfig) -> List[Dict[str, Any]]:
        """Search for datasets"""
        try:
            # Convert string types to enum
            dataset_types = None
            if config.dataset_types:
                dataset_types = [DatasetType(dt) for dt in config.dataset_types if dt in [e.value for e in DatasetType]]
            
            # Execute dataset search
            results = await self.dataset_manager.search_all_datasets(
                config.query,
                dataset_types=dataset_types,
                repositories=config.dataset_sources,
                limit_per_repo=config.max_results // 4
            )
            
            # Flatten and convert to dict format
            all_datasets = []
            for repo, datasets in results.items():
                for dataset in datasets:
                    all_datasets.append({
                        "id": dataset.id,
                        "title": dataset.title,
                        "description": dataset.description,
                        "authors": dataset.authors,
                        "repository": dataset.repository,
                        "dataset_type": dataset.dataset_type.value,
                        "size_mb": dataset.size_mb,
                        "format": dataset.format,
                        "license": dataset.license,
                        "access_url": dataset.access_url,
                        "doi": dataset.doi,
                        "keywords": dataset.keywords,
                        "last_updated": dataset.last_updated.isoformat() if dataset.last_updated else None,
                        "download_count": dataset.download_count,
                        "citation_count": dataset.citation_count,
                        "metadata": dataset.metadata
                    })
            
            # Apply result limit
            if len(all_datasets) > config.max_results:
                all_datasets = all_datasets[:config.max_results]
            
            return all_datasets
            
        except Exception as e:
            logging.error(f"Dataset search failed: {e}")
            return []
    
    async def _determine_paper_strategy(self, config: UnifiedSearchConfig) -> str:
        """Determine optimal search strategy for papers"""
        
        # Check MCP availability
        mcp_health = await self.mcp_client.health_check()
        mcp_healthy_count = sum(1 for status in mcp_health.values() if status.get("healthy", False))
        
        # Check API availability  
        api_capabilities = await self.paper_manager.get_search_capabilities()
        api_healthy_count = sum(1 for status in api_capabilities.get("api", {}).values() if status)
        
        # Decision logic
        if config.prefer_mcp and mcp_healthy_count >= 2:
            return "mcp_primary"
        elif api_healthy_count >= 2:
            return "api_primary"
        elif mcp_healthy_count > 0 and api_healthy_count > 0:
            return "hybrid"
        else:
            return "fallback"
    
    async def _search_papers_mcp_primary(self, config: UnifiedSearchConfig) -> List[Dict[str, Any]]:
        """Search papers primarily via MCP"""
        sources = config.paper_sources or ["semantic_scholar", "arxiv", "pubmed"]
        mcp_results = []
        
        for source in sources:
            try:
                if source == "semantic_scholar":
                    results = await self.mcp_client.search_papers(
                        "semantic_scholar_mcp",
                        config.query,
                        config.max_results // len(sources)
                    )
                elif source == "arxiv":
                    results = await self.mcp_client.search_papers(
                        "arxiv_mcp", 
                        config.query,
                        config.max_results // len(sources)
                    )
                else:
                    # Fallback to API for unsupported MCP sources
                    results = await self.enhanced_api.api_manager.search(
                        source, config.query, config.max_results // len(sources)
                    )
                
                mcp_results.extend(results)
                
            except Exception as e:
                logging.warning(f"MCP search failed for {source}: {e}")
                # Fallback to API for this source
                try:
                    results = await self.enhanced_api.api_manager.search(
                        source, config.query, config.max_results // len(sources)
                    )
                    mcp_results.extend(results)
                except Exception as api_e:
                    logging.error(f"API fallback also failed for {source}: {api_e}")
        
        return mcp_results
    
    async def _search_papers_api_primary(self, config: UnifiedSearchConfig) -> List[Dict[str, Any]]:
        """Search papers primarily via API"""
        sources = config.paper_sources or ["semantic_scholar", "arxiv", "pubmed", "crossref", "openalex"]
        
        # Use enhanced API for comprehensive search
        filters = {}
        if config.date_range:
            filters["year_range"] = (
                int(config.date_range.get("start", "1900")[:4]),
                int(config.date_range.get("end", "2030")[:4])
            )
        
        results = await self.enhanced_api.search_comprehensive(
            config.query,
            sources,
            config.max_results // len(sources),
            filters
        )
        
        # Flatten results
        all_papers = []
        for source, papers in results.items():
            all_papers.extend(papers)
        
        return all_papers
    
    async def _search_papers_hybrid(self, config: UnifiedSearchConfig) -> List[Dict[str, Any]]:
        """Hybrid search using both MCP and API"""
        
        # Execute both strategies in parallel
        mcp_task = asyncio.create_task(self._search_papers_mcp_primary(config))
        api_task = asyncio.create_task(self._search_papers_api_primary(config))
        
        try:
            mcp_results, api_results = await asyncio.gather(mcp_task, api_task, return_exceptions=True)
            
            # Combine results
            combined_results = []
            
            if isinstance(mcp_results, list):
                combined_results.extend(mcp_results)
            else:
                logging.error(f"MCP search failed: {mcp_results}")
            
            if isinstance(api_results, list):
                combined_results.extend(api_results)
            else:
                logging.error(f"API search failed: {api_results}")
            
            # Deduplicate based on title and DOI
            seen_titles = set()
            seen_dois = set()
            unique_results = []
            
            for paper in combined_results:
                title = paper.get("title", "").lower().strip()
                doi = paper.get("doi", "")
                
                if doi and doi in seen_dois:
                    continue
                if title in seen_titles:
                    continue
                
                unique_results.append(paper)
                if doi:
                    seen_dois.add(doi)
                seen_titles.add(title)
            
            return unique_results[:config.max_results]
            
        except Exception as e:
            logging.error(f"Hybrid search failed: {e}")
            return await self._search_papers_fallback(config)
    
    async def _search_papers_fallback(self, config: UnifiedSearchConfig) -> List[Dict[str, Any]]:
        """Fallback search strategy"""
        try:
            # Use basic paper manager
            paper_config = SearchConfig(
                databases=config.paper_sources or ["semantic_scholar", "arxiv"],
                max_results_per_db=config.max_results // 2,
                total_max_results=config.max_results,
                strategy=SearchStrategy.API_ONLY,
                enable_deduplication=True
            )
            
            results = await self.paper_manager.search(config.query, paper_config)
            
            # Convert SearchResult objects to dict
            return [
                {
                    "id": r.id,
                    "title": r.title,
                    "abstract": r.abstract,
                    "authors": r.authors,
                    "year": r.year,
                    "source": r.source,
                    "url": r.url,
                    "pdf_url": r.pdf_url,
                    "doi": r.doi,
                    "citation_count": r.citation_count,
                    "venue": r.venue,
                    "quality_score": r.quality_score,
                    "retrieved_at": r.retrieved_at,
                    "metadata": r.metadata or {}
                }
                for r in results
            ]
            
        except Exception as e:
            logging.error(f"Fallback search also failed: {e}")
            return []
    
    async def get_search_status(self) -> Dict[str, Any]:
        """Get current search system status"""
        status = {
            "initialized": self.initialized,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.initialized:
            # Check component health
            try:
                mcp_health = await self.mcp_client.health_check()
                api_capabilities = await self.paper_manager.get_search_capabilities()
                
                status.update({
                    "mcp_status": mcp_health,
                    "api_status": api_capabilities,
                    "components": {
                        "paper_manager": "healthy",
                        "enhanced_api": "healthy", 
                        "dataset_manager": "healthy",
                        "mcp_client": "healthy" if any(s.get("healthy") for s in mcp_health.values()) else "degraded"
                    }
                })
                
            except Exception as e:
                status["error"] = f"Status check failed: {e}"
        
        return status
    
    async def optimize_search_for_query(self, query: str) -> Dict[str, Any]:
        """Provide search optimization recommendations for a query"""
        recommendations = {
            "query": query,
            "suggested_sources": [],
            "suggested_strategy": "api_primary",
            "estimated_results": 0,
            "estimated_time": 0
        }
        
        try:
            # Analyze query characteristics
            query_lower = query.lower()
            
            # Suggest sources based on query content
            if any(term in query_lower for term in ["gene", "protein", "dna", "genome", "sequencing"]):
                recommendations["suggested_sources"] = ["pubmed", "ncbi_genomes", "ebi_ena"]
                recommendations["include_datasets"] = True
                recommendations["dataset_types"] = ["genomic"]
            elif any(term in query_lower for term in ["machine learning", "ai", "computer science"]):
                recommendations["suggested_sources"] = ["semantic_scholar", "arxiv"]
                recommendations["include_datasets"] = False
            elif any(term in query_lower for term in ["clinical", "trial", "patient", "medical"]):
                recommendations["suggested_sources"] = ["pubmed", "semantic_scholar", "data_gov"]
                recommendations["include_datasets"] = True
                recommendations["dataset_types"] = ["clinical"]
            else:
                recommendations["suggested_sources"] = ["semantic_scholar", "arxiv", "pubmed"]
                recommendations["include_datasets"] = False
            
            # Check system capabilities
            status = await self.get_search_status()
            if status.get("mcp_status", {}) and any(s.get("healthy") for s in status["mcp_status"].values()):
                recommendations["suggested_strategy"] = "mcp_primary"
                recommendations["estimated_time"] = 15
            else:
                recommendations["suggested_strategy"] = "api_primary"
                recommendations["estimated_time"] = 30
            
            # Estimate results based on source availability
            available_sources = len(recommendations["suggested_sources"])
            recommendations["estimated_results"] = available_sources * 50
            
        except Exception as e:
            logging.error(f"Search optimization failed: {e}")
            recommendations["error"] = str(e)
        
        return recommendations
    
    async def close(self):
        """Close all connections"""
        await self.paper_manager.close()
        await self.enhanced_api.close()
        await self.dataset_manager.close()
        await self.mcp_client.close()


# Convenience functions for Bach commands
async def unified_search(query: str, 
                        include_papers: bool = True,
                        include_datasets: bool = False,
                        max_results: int = 200,
                        api_keys: Optional[Dict[str, str]] = None,
                        **kwargs) -> Dict[str, Any]:
    """Simplified unified search interface"""
    
    config = UnifiedSearchConfig(
        query=query,
        max_results=max_results,
        include_papers=include_papers,
        include_datasets=include_datasets,
        **kwargs
    )
    
    orchestrator = BachSearchOrchestrator(api_keys)
    try:
        return await orchestrator.search(config)
    finally:
        await orchestrator.close()


async def quick_paper_search(query: str, max_results: int = 100, 
                           api_keys: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """Quick paper search with optimal defaults"""
    
    result = await unified_search(
        query=query,
        include_papers=True,
        include_datasets=False,
        max_results=max_results,
        api_keys=api_keys,
        prefer_mcp=True,
        fallback_to_api=True
    )
    
    return result.get("papers", [])


async def comprehensive_research_search(query: str, domain: Optional[str] = None,
                                      max_results: int = 300,
                                      api_keys: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Comprehensive search including papers and datasets"""
    
    # Domain-specific configuration
    dataset_types = None
    if domain:
        domain_map = {
            "genomics": ["genomic"],
            "clinical": ["clinical"],
            "chemistry": ["numerical"],
            "imaging": ["imaging"]
        }
        dataset_types = domain_map.get(domain.lower())
    
    return await unified_search(
        query=query,
        include_papers=True,
        include_datasets=True,
        max_results=max_results,
        dataset_types=dataset_types,
        api_keys=api_keys,
        prefer_mcp=True,
        parallel_execution=True
    )


if __name__ == "__main__":
    async def main():
        # Example usage
        api_keys = {
            "semantic_scholar": os.getenv("SEMANTIC_SCHOLAR_API_KEY"),
            "pubmed": os.getenv("PUBMED_EMAIL")
        }
        
        # Quick paper search
        papers = await quick_paper_search(
            "CRISPR gene editing",
            max_results=20,
            api_keys=api_keys
        )
        print(f"Found {len(papers)} papers")
        
        # Comprehensive search
        results = await comprehensive_research_search(
            "COVID-19 genomics",
            domain="genomics",
            max_results=50,
            api_keys=api_keys
        )
        
        print(f"Comprehensive search results:")
        print(f"  Papers: {len(results.get('papers', []))}")
        print(f"  Datasets: {len(results.get('datasets', []))}")
        print(f"  Search time: {results.get('metrics', {}).get('total_search_time', 0):.2f}s")
    
    asyncio.run(main())