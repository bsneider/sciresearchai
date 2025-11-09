#!/usr/bin/env python3
"""
Enhanced API Integration Layer for Bach Research System
Extended API capabilities with advanced features and remote dataset access

Provides comprehensive API access to:
- Scientific databases with advanced filtering
- Research data repositories
- Citation networks and academic graphs
- Specialized domain databases
- Real-time research monitoring
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import quote_plus, urlencode
import hashlib
import pickle

# Import base API integrations
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'agents', 'paper_search'))
from api_integrations import APIIntegrationManager, SemanticScholarAPI, ArxivAPI, PubmedAPI


@dataclass
class CacheEntry:
    """Cache entry for API responses"""
    data: Any
    timestamp: datetime
    ttl_seconds: int
    
    def is_expired(self) -> bool:
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)


class APICache:
    """Simple in-memory cache for API responses"""
    
    def __init__(self, default_ttl: int = 3600):  # 1 hour default
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
    
    def _make_key(self, api_name: str, endpoint: str, params: Dict[str, Any]) -> str:
        """Create cache key from API call parameters"""
        key_data = f"{api_name}:{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, api_name: str, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached result"""
        key = self._make_key(api_name, endpoint, params)
        
        if key in self.cache:
            entry = self.cache[key]
            if not entry.is_expired():
                return entry.data
            else:
                del self.cache[key]
        
        return None
    
    def set(self, api_name: str, endpoint: str, params: Dict[str, Any], 
           data: Any, ttl: Optional[int] = None) -> None:
        """Cache result"""
        key = self._make_key(api_name, endpoint, params)
        ttl = ttl or self.default_ttl
        
        self.cache[key] = CacheEntry(
            data=data,
            timestamp=datetime.now(),
            ttl_seconds=ttl
        )
    
    def clear_expired(self) -> int:
        """Remove expired entries"""
        expired_keys = [
            key for key, entry in self.cache.items() 
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)


class CrossRefAPI:
    """CrossRef API for DOI resolution and citation data"""
    
    def __init__(self, max_calls: int = 5, time_window: int = 1):
        self.base_url = "https://api.crossref.org"
        self.rate_limiter = None  # Will be set by enhanced manager
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None:
            headers = {
                "User-Agent": "BachResearchAI/1.0 (mailto:research@example.com)"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def search_works(self, query: str, limit: int = 100, 
                          filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search CrossRef works"""
        try:
            if self.rate_limiter:
                await self.rate_limiter.acquire()
            
            session = await self._get_session()
            
            params = {
                "query": query,
                "rows": min(limit, 1000),
                "sort": "relevance",
                "order": "desc"
            }
            
            # Add filters
            if filters:
                if "year_range" in filters:
                    params["filter"] = f"from-pub-date:{filters['year_range'][0]},until-pub-date:{filters['year_range'][1]}"
                if "publisher" in filters:
                    params["filter"] = f"publisher:{filters['publisher']}"
            
            async with session.get(f"{self.base_url}/works", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    works = data.get("message", {}).get("items", [])
                    
                    # Standardize format
                    standardized = []
                    for work in works:
                        standardized.append({
                            "id": work.get("DOI", ""),
                            "doi": work.get("DOI", ""),
                            "title": " ".join(work.get("title", [])),
                            "abstract": work.get("abstract", ""),
                            "authors": [
                                {"name": f"{author.get('given', '')} {author.get('family', '')}".strip()}
                                for author in work.get("author", [])
                            ],
                            "year": self._extract_year(work),
                            "journal": work.get("container-title", [""])[0] if work.get("container-title") else "",
                            "url": work.get("URL", ""),
                            "citation_count": work.get("is-referenced-by-count", 0),
                            "source": "crossref",
                            "retrieved_at": datetime.now().isoformat()
                        })
                    
                    return standardized
                else:
                    logging.error(f"CrossRef API error: {response.status}")
                    return []
                    
        except Exception as e:
            logging.error(f"CrossRef search error: {e}")
            return []
    
    def _extract_year(self, work: Dict[str, Any]) -> Optional[int]:
        """Extract publication year from CrossRef work"""
        date_parts = work.get("published-print", {}).get("date-parts")
        if not date_parts:
            date_parts = work.get("published-online", {}).get("date-parts")
        
        if date_parts and len(date_parts[0]) > 0:
            return int(date_parts[0][0])
        
        return None
    
    async def get_work_by_doi(self, doi: str) -> Dict[str, Any]:
        """Get work details by DOI"""
        try:
            if self.rate_limiter:
                await self.rate_limiter.acquire()
            
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/works/{doi}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("message", {})
                else:
                    return {}
                    
        except Exception as e:
            logging.error(f"CrossRef DOI lookup error: {e}")
            return {}
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()


class OpenAlexAPI:
    """OpenAlex API for comprehensive academic data"""
    
    def __init__(self, max_calls: int = 10, time_window: int = 1):
        self.base_url = "https://api.openalex.org"
        self.rate_limiter = None
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None:
            headers = {
                "User-Agent": "BachResearchAI/1.0 (mailto:research@example.com)"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def search_works(self, query: str, limit: int = 100,
                          filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search OpenAlex works"""
        try:
            if self.rate_limiter:
                await self.rate_limiter.acquire()
            
            session = await self._get_session()
            
            params = {
                "search": query,
                "per-page": min(limit, 200),
                "sort": "relevance_score:desc"
            }
            
            # Add filters
            filter_parts = []
            if filters:
                if "year_range" in filters:
                    filter_parts.append(f"publication_year:{filters['year_range'][0]}-{filters['year_range'][1]}")
                if "open_access" in filters and filters["open_access"]:
                    filter_parts.append("is_oa:true")
                if "type" in filters:
                    filter_parts.append(f"type:{filters['type']}")
            
            if filter_parts:
                params["filter"] = ",".join(filter_parts)
            
            async with session.get(f"{self.base_url}/works", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    works = data.get("results", [])
                    
                    # Standardize format
                    standardized = []
                    for work in works:
                        standardized.append({
                            "id": work.get("id", "").split("/")[-1],
                            "openalex_id": work.get("id", ""),
                            "doi": work.get("doi", "").replace("https://doi.org/", "") if work.get("doi") else "",
                            "title": work.get("title", ""),
                            "abstract": work.get("abstract", ""),
                            "authors": [
                                {"name": author.get("author", {}).get("display_name", "")}
                                for author in work.get("authorships", [])
                            ],
                            "year": work.get("publication_year"),
                            "journal": work.get("primary_location", {}).get("source", {}).get("display_name", ""),
                            "url": work.get("primary_location", {}).get("landing_page_url", ""),
                            "pdf_url": work.get("open_access", {}).get("oa_url", "") if work.get("open_access", {}).get("is_oa") else None,
                            "citation_count": work.get("cited_by_count", 0),
                            "concepts": [
                                concept.get("display_name", "")
                                for concept in work.get("concepts", [])
                            ],
                            "source": "openalex",
                            "retrieved_at": datetime.now().isoformat()
                        })
                    
                    return standardized
                else:
                    logging.error(f"OpenAlex API error: {response.status}")
                    return []
                    
        except Exception as e:
            logging.error(f"OpenAlex search error: {e}")
            return []
    
    async def get_author_works(self, author_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get works by specific author"""
        try:
            if self.rate_limiter:
                await self.rate_limiter.acquire()
            
            session = await self._get_session()
            
            params = {
                "filter": f"author.id:{author_id}",
                "per-page": min(limit, 200),
                "sort": "cited_by_count:desc"
            }
            
            async with session.get(f"{self.base_url}/works", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    return []
                    
        except Exception as e:
            logging.error(f"OpenAlex author works error: {e}")
            return []
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()


class ResearchDataAPI:
    """Interface for research data repositories"""
    
    def __init__(self):
        self.session = None
        self.repositories = {
            "zenodo": {
                "base_url": "https://zenodo.org/api/records",
                "search_endpoint": "/",
                "rate_limit": {"calls": 5, "window": 1}
            },
            "figshare": {
                "base_url": "https://api.figshare.com/v2",
                "search_endpoint": "/articles/search",
                "rate_limit": {"calls": 10, "window": 1}
            },
            "dataverse": {
                "base_url": "https://dataverse.harvard.edu/api",
                "search_endpoint": "/search",
                "rate_limit": {"calls": 3, "window": 1}
            }
        }
    
    async def search_datasets(self, repository: str, query: str, 
                            limit: int = 50) -> List[Dict[str, Any]]:
        """Search for research datasets"""
        if repository not in self.repositories:
            raise ValueError(f"Unknown repository: {repository}")
        
        try:
            if repository == "zenodo":
                return await self._search_zenodo(query, limit)
            elif repository == "figshare":
                return await self._search_figshare(query, limit)
            elif repository == "dataverse":
                return await self._search_dataverse(query, limit)
            else:
                return []
                
        except Exception as e:
            logging.error(f"Dataset search error in {repository}: {e}")
            return []
    
    async def _search_zenodo(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search Zenodo repository"""
        session = await self._get_session()
        
        params = {
            "q": query,
            "size": min(limit, 1000),
            "type": "dataset"
        }
        
        async with session.get("https://zenodo.org/api/records", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("hits", {}).get("hits", [])
            else:
                return []
    
    async def _search_figshare(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search Figshare repository"""
        session = await self._get_session()
        
        search_data = {
            "search_for": query,
            "item_type": 3,  # Dataset
            "page_size": min(limit, 1000)
        }
        
        async with session.post(
            "https://api.figshare.com/v2/articles/search",
            json=search_data
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []
    
    async def _search_dataverse(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search Harvard Dataverse"""
        session = await self._get_session()
        
        params = {
            "q": query,
            "type": "dataset",
            "per_page": min(limit, 1000)
        }
        
        async with session.get(
            "https://dataverse.harvard.edu/api/search",
            params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", {}).get("items", [])
            else:
                return []
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None:
            headers = {
                "User-Agent": "BachResearchAI/1.0 (mailto:research@example.com)"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()


class EnhancedAPIManager:
    """Enhanced API manager with caching, monitoring, and extended capabilities"""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None, 
                 enable_cache: bool = True, cache_ttl: int = 3600):
        
        # Base API manager
        self.base_manager = APIIntegrationManager(api_keys)
        
        # Extended APIs
        self.crossref = CrossRefAPI()
        self.openalex = OpenAlexAPI()
        self.research_data = ResearchDataAPI()
        
        # Set rate limiters
        from api_integrations import RateLimiter
        self.crossref.rate_limiter = RateLimiter(5, 1)
        self.openalex.rate_limiter = RateLimiter(10, 1)
        
        # Cache system
        self.cache = APICache(cache_ttl) if enable_cache else None
        
        # Monitoring
        self.call_counts = {}
        self.error_counts = {}
        self.response_times = {}
    
    async def search_comprehensive(self, query: str, sources: Optional[List[str]] = None,
                                 limit_per_source: int = 50, 
                                 filters: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Comprehensive search across all available sources"""
        
        if sources is None:
            sources = ["semantic_scholar", "arxiv", "pubmed", "crossref", "openalex"]
        
        results = {}
        search_tasks = []
        
        # Base APIs
        for source in ["semantic_scholar", "arxiv", "pubmed"]:
            if source in sources and self.base_manager.is_available(source):
                task = self._search_with_monitoring(
                    source, query, limit_per_source, filters, "base"
                )
                search_tasks.append((source, task))
        
        # Extended APIs
        if "crossref" in sources:
            task = self._search_with_monitoring(
                "crossref", query, limit_per_source, filters, "extended"
            )
            search_tasks.append(("crossref", task))
        
        if "openalex" in sources:
            task = self._search_with_monitoring(
                "openalex", query, limit_per_source, filters, "extended"
            )
            search_tasks.append(("openalex", task))
        
        # Execute searches
        for source, task in search_tasks:
            try:
                source_results = await task
                results[source] = source_results
            except Exception as e:
                logging.error(f"Search failed for {source}: {e}")
                results[source] = []
                self._record_error(source)
        
        return results
    
    async def _search_with_monitoring(self, source: str, query: str, limit: int,
                                    filters: Optional[Dict[str, Any]], api_type: str) -> List[Dict[str, Any]]:
        """Search with performance monitoring"""
        start_time = time.time()
        
        try:
            # Check cache first
            if self.cache:
                cached_result = self.cache.get(source, "search", {
                    "query": query, "limit": limit, "filters": filters
                })
                if cached_result is not None:
                    return cached_result
            
            # Execute search
            if api_type == "base":
                results = await self.base_manager.search(source, query, limit)
            elif source == "crossref":
                results = await self.crossref.search_works(query, limit, filters)
            elif source == "openalex":
                results = await self.openalex.search_works(query, limit, filters)
            else:
                results = []
            
            # Cache results
            if self.cache:
                self.cache.set(source, "search", {
                    "query": query, "limit": limit, "filters": filters
                }, results)
            
            # Record metrics
            self._record_call(source)
            self._record_response_time(source, time.time() - start_time)
            
            return results
            
        except Exception as e:
            self._record_error(source)
            raise
    
    async def search_datasets(self, query: str, repositories: Optional[List[str]] = None,
                            limit_per_repo: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """Search research data repositories"""
        if repositories is None:
            repositories = ["zenodo", "figshare", "dataverse"]
        
        results = {}
        
        for repo in repositories:
            try:
                repo_results = await self.research_data.search_datasets(repo, query, limit_per_repo)
                results[repo] = repo_results
                self._record_call(f"dataset_{repo}")
            except Exception as e:
                logging.error(f"Dataset search failed for {repo}: {e}")
                results[repo] = []
                self._record_error(f"dataset_{repo}")
        
        return results
    
    async def get_citation_network(self, paper_id: str, source: str = "openalex") -> Dict[str, Any]:
        """Get citation network for a paper"""
        try:
            if source == "openalex":
                # Get citing papers
                session = await self.openalex._get_session()
                params = {"filter": f"cites:{paper_id}", "per-page": 200}
                
                async with session.get(f"{self.openalex.base_url}/works", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        citing_papers = data.get("results", [])
                    else:
                        citing_papers = []
                
                # Get referenced papers
                params = {"filter": f"cited_by:{paper_id}", "per-page": 200}
                
                async with session.get(f"{self.openalex.base_url}/works", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        referenced_papers = data.get("results", [])
                    else:
                        referenced_papers = []
                
                return {
                    "citing_papers": citing_papers,
                    "referenced_papers": referenced_papers,
                    "citation_count": len(citing_papers),
                    "reference_count": len(referenced_papers)
                }
            else:
                return {}
                
        except Exception as e:
            logging.error(f"Citation network error: {e}")
            return {}
    
    def _record_call(self, source: str):
        """Record API call"""
        self.call_counts[source] = self.call_counts.get(source, 0) + 1
    
    def _record_error(self, source: str):
        """Record API error"""
        self.error_counts[source] = self.error_counts.get(source, 0) + 1
    
    def _record_response_time(self, source: str, response_time: float):
        """Record response time"""
        if source not in self.response_times:
            self.response_times[source] = []
        self.response_times[source].append(response_time)
        
        # Keep only last 100 response times
        if len(self.response_times[source]) > 100:
            self.response_times[source] = self.response_times[source][-100:]
    
    def get_performance_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get API performance metrics"""
        metrics = {}
        
        for source in set(list(self.call_counts.keys()) + list(self.error_counts.keys())):
            calls = self.call_counts.get(source, 0)
            errors = self.error_counts.get(source, 0)
            times = self.response_times.get(source, [])
            
            metrics[source] = {
                "total_calls": calls,
                "error_count": errors,
                "error_rate": errors / calls if calls > 0 else 0,
                "avg_response_time": sum(times) / len(times) if times else 0,
                "max_response_time": max(times) if times else 0,
                "min_response_time": min(times) if times else 0
            }
        
        return metrics
    
    def clear_cache(self):
        """Clear API cache"""
        if self.cache:
            self.cache.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache:
            return {"enabled": False}
        
        expired_count = self.cache.clear_expired()
        
        return {
            "enabled": True,
            "total_entries": len(self.cache.cache),
            "expired_cleared": expired_count
        }
    
    async def close(self):
        """Close all API connections"""
        await self.base_manager.close()
        await self.crossref.close()
        await self.openalex.close()
        await self.research_data.close()


# Convenience functions for Bach commands
async def enhanced_search(query: str, sources: Optional[List[str]] = None,
                        max_results: int = 200, api_keys: Optional[Dict[str, str]] = None,
                        filters: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Enhanced search across multiple sources"""
    manager = EnhancedAPIManager(api_keys)
    try:
        results = await manager.search_comprehensive(
            query, sources, max_results // len(sources or ["semantic_scholar", "arxiv", "pubmed"]), filters
        )
        return results
    finally:
        await manager.close()


async def search_with_datasets(query: str, include_papers: bool = True, 
                             include_datasets: bool = True,
                             api_keys: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Search both papers and datasets"""
    manager = EnhancedAPIManager(api_keys)
    try:
        results = {}
        
        if include_papers:
            results["papers"] = await manager.search_comprehensive(query)
        
        if include_datasets:
            results["datasets"] = await manager.search_datasets(query)
        
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
        
        # Enhanced search
        results = await enhanced_search(
            "machine learning healthcare",
            sources=["semantic_scholar", "openalex", "crossref"],
            max_results=60,
            api_keys=api_keys,
            filters={"year_range": (2020, 2024)}
        )
        
        print("Enhanced Search Results:")
        for source, papers in results.items():
            print(f"  {source}: {len(papers)} papers")
        
        # Dataset search
        dataset_results = await search_with_datasets(
            "covid-19 clinical trial data",
            api_keys=api_keys
        )
        
        print("\nDataset Search Results:")
        if "datasets" in dataset_results:
            for repo, datasets in dataset_results["datasets"].items():
                print(f"  {repo}: {len(datasets)} datasets")
    
    asyncio.run(main())