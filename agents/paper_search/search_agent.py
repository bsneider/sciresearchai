"""
Paper Search Subagent Core Infrastructure
Implements comprehensive literature discovery and retrieval across multiple databases
"""

import asyncio
import hashlib
from typing import List, Dict, Optional

from .api_integrations import APIIntegrationManager
from .vector_search import VectorSearchEngine
from .search_workflow import SearchWorkflowOrchestrator


class RateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, max_calls: int = 1, time_window: int = 1):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    async def acquire(self):
        """Acquire rate limit token"""
        import time
        now = time.time()

        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

        # Wait if too many calls
        if len(self.calls) >= self.max_calls:
            sleep_time = self.time_window - (now - self.calls[0]) + 0.1
            await asyncio.sleep(sleep_time)
            await self.acquire()

        self.calls.append(now)


class SearchAgent:
    """Core Paper Search Agent for multi-database literature discovery"""

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        self.rate_limiter = RateLimiter(max_calls=1, time_window=1)

        # Initialize API integration manager
        self.api_manager = APIIntegrationManager(api_keys)

        # Initialize vector search engine
        try:
            self.vector_engine = VectorSearchEngine(collection_name="research_papers")
        except ImportError:
            logging.warning("Vector search not available - missing dependencies")
            self.vector_engine = None

        # Initialize search workflow orchestrator
        self.workflow_orchestrator = SearchWorkflowOrchestrator(self)

    async def optimize_query(self, query: str) -> str:
        """Optimize search query for better results across databases"""
        # Simple optimization - in production would use more sophisticated techniques
        query_terms = query.lower().split()

        # Add common scientific search operators
        optimized_terms = []
        for term in query_terms:
            optimized_terms.append(term)
            # Add variations for broader coverage
            if len(term) > 3:
                optimized_terms.append(f"{term}*")

        return " ".join(optimized_terms)

    async def score_relevance(self, papers: List[Dict], query: str) -> List[Dict]:
        """Score papers by relevance to query"""
        query_terms = set(query.lower().split())

        for paper in papers:
            score = 0

            # Title matching
            title = paper.get("title", "").lower()
            title_match = len(query_terms.intersection(set(title.split())))
            score += title_match * 3

            # Abstract matching
            abstract = paper.get("abstract", "").lower()
            abstract_match = len(query_terms.intersection(set(abstract.split())))
            score += abstract_match * 1

            # Recent papers get bonus
            year = paper.get("year", 0)
            if year >= 2020:
                score += 1

            # Citation count bonus
            citations = paper.get("citationCount", paper.get("citations", 0))
            if citations > 50:
                score += 1

            paper["relevance_score"] = score

        # Sort by relevance score (descending)
        return sorted(papers, key=lambda x: x["relevance_score"], reverse=True)

    def remove_duplicates(self, papers: List[Dict]) -> List[Dict]:
        """Remove duplicate papers based on DOI or similar titles"""
        seen_dois = set()
        seen_titles = set()
        unique_papers = []

        for paper in papers:
            doi = paper.get("doi", "")
            title = paper.get("title", "").lower().strip()

            # Check DOI first (most reliable)
            if doi and doi in seen_dois:
                continue

            # Check title similarity if no DOI
            if not doi:
                # Simple title-based deduplication
                title_hash = hashlib.md5(title.encode()).hexdigest()
                if title_hash in seen_titles:
                    continue
                seen_titles.add(title_hash)

            if doi:
                seen_dois.add(doi)

            unique_papers.append(paper)

        return unique_papers

    async def _make_api_call(self, api_name: str, params: Dict) -> Dict:
        """Make rate-limited API call with error handling"""
        await self.rate_limiter.acquire()

        # For testing and development, return mock data
        mock_responses = {
            "semantic_scholar": {
                "data": [
                    {
                        "paperId": "ss_test_1",
                        "title": "Machine Learning in Healthcare Applications",
                        "abstract": "This paper explores ML applications...",
                        "year": 2023,
                        "citationCount": 150
                    },
                    {
                        "paperId": "ss_test_2",
                        "title": "Deep Learning for Medical Imaging",
                        "abstract": "Medical imaging analysis...",
                        "year": 2022,
                        "citationCount": 89
                    }
                ]
            },
            "arxiv": {
                "data": [
                    {
                        "id": "arxiv_test_1",
                        "title": "Neural Networks for Healthcare Data Analysis",
                        "summary": "Analysis of healthcare datasets using neural networks",
                        "published": "2023-05-15"
                    }
                ]
            },
            "pubmed": {
                "data": [
                    {
                        "pmid": "12345678",
                        "title": "Machine Learning in Clinical Practice",
                        "abstract": "Clinical applications of machine learning algorithms...",
                        "publication_date": "2023"
                    }
                ]
            }
        }

        return mock_responses.get(api_name, {"data": []})

    async def search_semantic_scholar(self, query: str) -> List[Dict]:
        """Search Semantic Scholar database"""
        return await self.api_manager.search("semantic_scholar", query)

    async def search_arxiv(self, query: str) -> List[Dict]:
        """Search arXiv database"""
        return await self.api_manager.search("arxiv", query)

    async def search_pubmed(self, query: str) -> List[Dict]:
        """Search PubMed/NCBI database"""
        return await self.api_manager.search("pubmed", query)

    async def search_all_databases(self, query: str) -> List[Dict]:
        """Search across all configured databases"""
        return await self.api_manager.search_all(query)

    async def vector_search(self, query: str, top_k: int = 10, search_type: str = "hybrid") -> List[Dict]:
        """Perform vector search on stored papers"""
        if not self.vector_engine:
            logging.warning("Vector search not available")
            return []

        try:
            if search_type == "semantic":
                return await self.vector_engine.semantic_search(query, top_k)
            elif search_type == "hybrid":
                return await self.vector_engine.hybrid_search(query, top_k)
            else:
                raise ValueError(f"Unknown search type: {search_type}")
        except Exception as e:
            logging.error(f"Vector search error: {e}")
            return []

    async def add_papers_to_vector_store(self, papers: List[Dict]) -> None:
        """Add papers to vector search database"""
        if not self.vector_engine:
            logging.warning("Vector search not available")
            return

        try:
            await self.vector_engine.add_documents(papers)
        except Exception as e:
            logging.error(f"Error adding papers to vector store: {e}")

    async def search_with_vector_enhancement(self, query: str, top_k: int = 20) -> List[Dict]:
        """Enhanced search combining API results with vector search"""
        # Get results from APIs
        api_results = await self.search_all_databases(query)

        # Add papers to vector store for future searches
        if api_results:
            await self.add_papers_to_vector_store(api_results)

        # Get vector search results
        vector_results = await self.vector_search(query, top_k // 2, "hybrid")

        # Combine and deduplicate results
        all_results = api_results + vector_results
        unique_results = self.remove_duplicates(all_results)

        # Re-rank combined results
        ranked_results = await self.score_relevance(unique_results, query)

        return ranked_results[:top_k]

    async def execute_search_workflow(self, query: str, max_results: int = 100) -> List[Dict]:
        """Execute complete search workflow with orchestration"""
        return await self.workflow_orchestrator.execute_search_workflow(query, max_results)

    async def execute_enhanced_search_workflow(self, query: str, max_results: int = 50) -> List[Dict]:
        """Execute enhanced search workflow with vector search"""
        return await self.workflow_orchestrator.execute_enhanced_search_workflow(query, max_results)

    async def analyze_search_coverage(self, results: List[Dict], query: str) -> Dict:
        """Analyze coverage and provide insights"""
        return self.workflow_orchestrator.analyze_search_performance(results, query)

    def get_workflow_status(self) -> Dict:
        """Get current workflow execution status"""
        return self.workflow_orchestrator.get_workflow_status()

    def _get_source_name(self, index: int) -> str:
        """Get database source name from index"""
        sources = ["semantic_scholar", "arxiv", "pubmed"]
        return sources[index] if index < len(sources) else "unknown"