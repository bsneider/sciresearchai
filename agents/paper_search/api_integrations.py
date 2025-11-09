"""
Scientific Database API Integrations
Implements T-SEARCH-002: Build Scientific Database API Integrations

Provides official API connectors for:
- Semantic Scholar API with rate limiting
- arXiv API connector with proper attribution
- PubMed/NCBI E-utilities integration via BioPython
"""

import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any
from datetime import datetime
import time
import logging
from urllib.parse import quote_plus

# Import BioPython for PubMed integration
try:
    from Bio import Entrez
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False
    logging.warning("BioPython not available. PubMed integration disabled.")


class RateLimiter:
    """Configurable rate limiter for API calls"""

    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    async def acquire(self):
        """Acquire rate limit token"""
        now = time.time()

        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

        # Wait if too many calls
        if len(self.calls) >= self.max_calls:
            sleep_time = self.time_window - (now - self.calls[0]) + 0.1
            await asyncio.sleep(sleep_time)
            await self.acquire()

        self.calls.append(now)


class SemanticScholarAPI:
    """Semantic Scholar API integration with rate limiting"""

    def __init__(self, api_key: Optional[str] = None, max_calls: int = 1, time_window: int = 1):
        self.api_key = api_key
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.rate_limiter = RateLimiter(max_calls, time_window)
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None:
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    def _format_query(self, query: str) -> str:
        """Format query for Semantic Scholar API"""
        # Simple query formatting - could be enhanced
        return query.strip()

    async def search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search Semantic Scholar database"""
        if not self.api_key:
            logging.warning("Semantic Scholar API key not provided")
            return []

        try:
            await self.rate_limiter.acquire()

            session = await self._get_session()
            formatted_query = self._format_query(query)

            # Search for papers
            search_url = f"{self.base_url}/paper/search"
            params = {
                "query": formatted_query,
                "limit": min(limit, 100),  # API limit
                "fields": "paperId,title,abstract,year,citationCount,authors,venue,url,openAccessPdf"
            }

            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    papers = data.get("data", [])

                    # Add source and normalize format
                    for paper in papers:
                        paper["source"] = "semantic_scholar"
                        paper["retrieved_at"] = datetime.now().isoformat()

                    return papers
                elif response.status == 429:
                    retry_after = response.headers.get("Retry-After", "2")
                    await asyncio.sleep(float(retry_after))
                    return []
                else:
                    logging.error(f"Semantic Scholar API error: {response.status}")
                    return []

        except Exception as e:
            logging.error(f"Semantic Scholar search error: {e}")
            return []

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()


class ArxivAPI:
    """arXiv API connector with proper attribution"""

    def __init__(self, max_calls: int = 1, time_window: int = 3):
        self.base_url = "http://export.arxiv.org/api/query"
        self.rate_limiter = RateLimiter(max_calls, time_window)
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None:
            # Include user agent for proper attribution
            headers = {
                "User-Agent": "SciResearchAI/0.1 (mailto:your-email@example.com)"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    def _format_query(self, query: str) -> str:
        """Format query for arXiv API"""
        # Convert to arXiv query format
        # Add "all:" prefix for general search
        formatted = query.strip()
        if not formatted.startswith(("ti:", "au:", "abs:", "all:")):
            # URL encode the query
            encoded_query = quote_plus(formatted)
            formatted = f"all:{encoded_query}"
        return formatted

    def _parse_arxiv_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse arXiv XML response"""
        papers = []

        try:
            # Parse XML
            root = ET.fromstring(xml_text)

            # Handle XML namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }

            # Extract entries
            for entry in root.findall('atom:entry', namespaces):
                paper = {}

                # Basic metadata
                paper['id'] = entry.find('atom:id', namespaces).text.split('/')[-1]
                paper['title'] = entry.find('atom:title', namespaces).text.strip()
                paper['summary'] = entry.find('atom:summary', namespaces).text.strip()

                # Publication date
                published = entry.find('atom:published', namespaces)
                if published is not None:
                    paper['published'] = published.text
                    # Extract year
                    paper['year'] = int(published.text[:4])

                # Authors
                authors = []
                for author in entry.findall('atom:author', namespaces):
                    name_elem = author.find('atom:name', namespaces)
                    if name_elem is not None:
                        authors.append({'name': name_elem.text})
                paper['authors'] = authors

                # Categories
                categories = []
                for category in entry.findall('atom:category', namespaces):
                    term = category.get('term')
                    if term:
                        categories.append(term)
                paper['categories'] = categories

                # PDF link
                pdf_links = entry.findall(".//atom:link[@type='application/pdf']", namespaces)
                if pdf_links:
                    paper['pdf_url'] = pdf_links[0].get('href')

                # Add source and retrieval info
                paper['source'] = 'arxiv'
                paper['retrieved_at'] = datetime.now().isoformat()

                papers.append(paper)

        except Exception as e:
            logging.error(f"Error parsing arXiv XML: {e}")

        return papers

    async def search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search arXiv database"""
        try:
            await self.rate_limiter.acquire()

            session = await self._get_session()
            formatted_query = self._format_query(query)

            params = {
                'search_query': formatted_query,
                'start': 0,
                'max_results': min(limit, 1000),  # arXiv limit
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }

            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    xml_text = await response.text()
                    papers = self._parse_arxiv_xml(xml_text)
                    return papers
                else:
                    logging.error(f"arXiv API error: {response.status}")
                    return []

        except Exception as e:
            logging.error(f"arXiv search error: {e}")
            return []

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()


class PubmedAPI:
    """PubMed/NCBI E-utilities integration via BioPython"""

    def __init__(self, email: str, api_key: Optional[str] = None, max_calls: int = 3, time_window: int = 1):
        if not BIOPYTHON_AVAILABLE:
            raise ImportError("BioPython is required for PubMed integration")

        self.email = email
        self.api_key = api_key
        self.rate_limiter = RateLimiter(max_calls, time_window)

        # Configure BioPython Entrez
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key

    def _format_query(self, query: str) -> str:
        """Format query for PubMed search"""
        # Convert to PubMed query format
        # Could be enhanced with MeSH terms, field tags, etc.
        formatted = query.strip()
        return formatted

    async def search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search PubMed database"""
        try:
            await self.rate_limiter.acquire()

            formatted_query = self._format_query(query)

            # Search for article IDs
            search_handle = Entrez.esearch(
                db="pubmed",
                term=formatted_query,
                retmax=min(limit, 1000),
                usehistory="y"
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()

            id_list = search_results.get("IdList", [])
            if not id_list:
                return []

            # Fetch detailed records
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=id_list,
                rettype="xml",
                retmode="xml"
            )
            xml_text = fetch_handle.read()
            fetch_handle.close()

            # Parse PubMed XML
            papers = self._parse_pubmed_xml(xml_text)

            return papers

        except Exception as e:
            logging.error(f"PubMed search error: {e}")
            return []

    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML response"""
        papers = []

        try:
            root = ET.fromstring(xml_text)

            # PubMedArticle elements
            for article in root.findall('.//PubmedArticle'):
                paper = {}

                # PMID
                pmid_elem = article.find('.//PMID')
                if pmid_elem is not None:
                    paper['pmid'] = pmid_elem.text

                # Title
                title_elem = article.find('.//ArticleTitle')
                if title_elem is not None:
                    paper['title'] = title_elem.text or ''
                else:
                    paper['title'] = ''

                # Abstract
                abstract_text = []
                abstract_elem = article.find('.//Abstract')
                if abstract_elem is not None:
                    for abs_text in abstract_elem.findall('.//AbstractText'):
                        if abs_text.text:
                            abstract_text.append(abs_text.text)
                paper['abstract'] = ' '.join(abstract_text)

                # Publication date
                date_elem = article.find('.//DateCreated')
                if date_elem is not None:
                    year = date_elem.find('.//Year')
                    if year is not None:
                        paper['year'] = int(year.text)
                        paper['publication_date'] = f"{year.text}-01-01"

                # Authors
                authors = []
                for author in article.findall('.//Author'):
                    last_name = author.find('.//LastName')
                    fore_name = author.find('.//ForeName')
                    if last_name is not None and fore_name is not None:
                        authors.append({
                            'name': f"{fore_name.text} {last_name.text}"
                        })
                    elif last_name is not None:
                        authors.append({
                            'name': last_name.text
                        })
                paper['authors'] = authors

                # Journal
                journal_elem = article.find('.//Journal/Title')
                if journal_elem is not None:
                    paper['journal'] = journal_elem.text

                # Add source and retrieval info
                paper['source'] = 'pubmed'
                paper['retrieved_at'] = datetime.now().isoformat()

                papers.append(paper)

        except Exception as e:
            logging.error(f"Error parsing PubMed XML: {e}")

        return papers


class APIIntegrationManager:
    """Unified management of all API integrations"""

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}

        # Initialize API clients
        self.semantic_scholar = SemanticScholarAPI(
            api_key=self.api_keys.get("semantic_scholar")
        )

        self.arxiv = ArxivAPI()  # Always available

        # Initialize PubMed if email provided
        if self.api_keys.get("pubmed"):
            try:
                self.pubmed = PubmedAPI(email=self.api_keys.get("pubmed"))
            except ImportError:
                logging.warning("BioPython not available for PubMed integration")
                self.pubmed = None
        else:
            self.pubmed = None

    def is_available(self, api_name: str) -> bool:
        """Check if an API is available for use"""
        if api_name == "semantic_scholar":
            return bool(self.api_keys.get("semantic_scholar"))
        elif api_name == "arxiv":
            return True  # Always available
        elif api_name == "pubmed":
            return self.pubmed is not None
        return False

    async def search(self, api_name: str, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search using a specific API"""
        if not self.is_available(api_name):
            logging.warning(f"API {api_name} not available")
            return []

        try:
            results = []
            if api_name == "semantic_scholar":
                results = await self.semantic_scholar.search(query, limit)
            elif api_name == "arxiv":
                results = await self.arxiv.search(query, limit)
            elif api_name == "pubmed":
                results = await self.pubmed.search(query, limit)
            else:
                raise ValueError(f"Unknown API: {api_name}")

            # Ensure source is properly tagged
            for result in results:
                if "source" not in result:
                    result["source"] = api_name

            return results
        except Exception as e:
            logging.error(f"Error searching {api_name}: {e}")
            return []

    async def search_all(self, query: str, limit_per_api: int = 50) -> List[Dict[str, Any]]:
        """Search across all available APIs in parallel"""
        search_tasks = []

        if self.is_available("semantic_scholar"):
            search_tasks.append(self.search("semantic_scholar", query, limit_per_api))

        # arXiv is always available
        search_tasks.append(self.search("arxiv", query, limit_per_api))

        if self.is_available("pubmed"):
            search_tasks.append(self.search("pubmed", query, limit_per_api))

        # Execute searches in parallel
        results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Combine results
        all_papers = []
        for result in results:
            if isinstance(result, list):
                all_papers.extend(result)
            elif isinstance(result, Exception):
                logging.error(f"Search failed: {result}")

        return all_papers

    async def _search_without_error_handling(self, api_name: str, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Internal search method that allows exceptions to propagate"""
        if not self.is_available(api_name):
            raise ValueError(f"API {api_name} not available")

        results = []
        if api_name == "semantic_scholar":
            results = await self.semantic_scholar.search(query, limit)
        elif api_name == "arxiv":
            results = await self.arxiv.search(query, limit)
        elif api_name == "pubmed":
            results = await self.pubmed.search(query, limit)
        else:
            raise ValueError(f"Unknown API: {api_name}")

        # Ensure source is properly tagged
        for result in results:
            if "source" not in result:
                result["source"] = api_name

        return results

    async def search_with_retry(self, api_name: str, query: str, max_retries: int = 3,
                              base_delay: float = 0.25) -> List[Dict[str, Any]]:
        """Search with exponential backoff retry logic"""
        for attempt in range(max_retries + 1):
            try:
                result = await self._search_without_error_handling(api_name, query)
                if result:  # Success if we get non-empty result
                    return result
            except Exception as e:
                if attempt == max_retries:
                    logging.error(f"Search {api_name} failed after {max_retries} retries: {e}")
                    return []

                delay = base_delay * (2 ** attempt)
                logging.warning(f"Search {api_name} failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)

        return []  # Return empty list if all retries fail

    async def check_api_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health status of all APIs"""
        health_status = {}

        test_query = "machine learning"

        for api_name in ["semantic_scholar", "arxiv", "pubmed"]:
            try:
                start_time = time.time()
                results = await self.search(api_name, test_query, limit=1)
                response_time = time.time() - start_time

                health_status[api_name] = {
                    "healthy": True,
                    "response_time": response_time,
                    "available": self.is_available(api_name),
                    "results_count": len(results)
                }
            except Exception as e:
                health_status[api_name] = {
                    "healthy": False,
                    "error": str(e),
                    "available": self.is_available(api_name),
                    "results_count": 0
                }

        return health_status

    async def close(self):
        """Close all API sessions"""
        await self.semantic_scholar.close()
        await self.arxiv.close()
        # PubMed doesn't maintain persistent sessions