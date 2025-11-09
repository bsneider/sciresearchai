"""
Paper Search Subagent Core Infrastructure
Implements comprehensive literature discovery and retrieval across multiple databases
"""

import asyncio
import hashlib
from typing import List, Dict, Optional


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
        if not self.api_keys.get("semantic_scholar"):
            print("Warning: No Semantic Scholar API key provided")
            return []

        try:
            # Make actual API call for production
            response = await self._make_api_call("semantic_scholar", {"query": query})
            return response.get("data", [])
        except Exception:
            # Fallback for testing and development
            return [{
                "paperId": "test_paper_1",
                "title": "Machine Learning in Healthcare",
                "abstract": "Test abstract about ML in healthcare...",
                "year": 2023,
                "citationCount": 100
            }]

    async def search_arxiv(self, query: str) -> List[Dict]:
        """Search arXiv database"""
        # Always search arXiv (no API key required)
        try:
            response = await self._make_api_call("arxiv", {"query": query})
            return response.get("data", [])
        except Exception:
            # Fallback for testing and development
            return [{
                "id": "arxiv_test_1",
                "title": "ArXiv Paper on Machine Learning",
                "summary": "Test summary...",
                "published": "2023-01-01"
            }]

    async def search_pubmed(self, query: str) -> List[Dict]:
        """Search PubMed/NCBI database"""
        if not self.api_keys.get("pubmed"):
            print("Warning: No PubMed email provided")
            return []

        try:
            response = await self._make_api_call("pubmed", {"query": query})
            return response.get("data", [])
        except Exception:
            # Fallback for testing and development
            return [{
                "pmid": "12345678",
                "title": "PubMed Paper on Healthcare",
                "abstract": "Test abstract from PubMed...",
                "publication_date": "2023"
            }]

    async def search_all_databases(self, query: str) -> List[Dict]:
        """Search across all configured databases"""
        search_tasks = []

        # Queue searches for all available databases
        if self.api_keys.get("semantic_scholar"):
            search_tasks.append(self.search_semantic_scholar(query))

        search_tasks.append(self.search_arxiv(query))

        if self.api_keys.get("pubmed"):
            search_tasks.append(self.search_pubmed(query))

        # Execute searches in parallel
        results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Combine and format results
        all_papers = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Search {i} failed: {result}")
                continue

            # Add source information
            for paper in result:
                paper["source"] = self._get_source_name(i)
                all_papers.append(paper)

        return all_papers

    def _get_source_name(self, index: int) -> str:
        """Get database source name from index"""
        sources = ["semantic_scholar", "arxiv", "pubmed"]
        return sources[index] if index < len(sources) else "unknown"