"""
Unit tests for scientific database API integrations
Tests T-SEARCH-002: Build Scientific Database API Integrations
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import time
from datetime import datetime

from agents.paper_search.api_integrations import (
    SemanticScholarAPI,
    ArxivAPI,
    PubmedAPI,
    APIIntegrationManager
)


class TestSemanticScholarAPI:
    """Test Semantic Scholar API integration"""

    @pytest.fixture
    def api(self):
        return SemanticScholarAPI(api_key="test_key")

    @pytest.fixture
    def api_no_key(self):
        return SemanticScholarAPI()

    @pytest.mark.asyncio
    async def test_semantic_scholar_search_success(self, api):
        """Test successful Semantic Scholar search"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "data": [
                    {
                        "paperId": "test123",
                        "title": "Machine Learning in Healthcare",
                        "abstract": "This paper explores ML applications...",
                        "year": 2023,
                        "citationCount": 150,
                        "authors": [{"name": "Test Author"}],
                        "venue": {"name": "Nature Medicine"}
                    }
                ],
                "total": 1
            }
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await api.search("machine learning healthcare")

            assert len(result) == 1
            assert result[0]["paperId"] == "test123"
            assert result[0]["title"] == "Machine Learning in Healthcare"
            assert result[0]["citationCount"] == 150

    @pytest.mark.asyncio
    async def test_semantic_scholar_rate_limiting(self, api):
        """Test rate limiting for Semantic Scholar API"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"data": []}
            mock_get.return_value.__aenter__.return_value = mock_response

            start_time = time.time()

            # Make multiple rapid calls
            tasks = []
            for i in range(3):
                task = api.search(f"test query {i}")
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)

            elapsed = time.time() - start_time
            # Should take at least 2 seconds due to rate limiting (1 call per second)
            assert elapsed >= 2.0

    @pytest.mark.asyncio
    async def test_semantic_scholar_error_handling(self, api):
        """Test error handling for Semantic Scholar API"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock rate limit response
            mock_response = AsyncMock()
            mock_response.status = 429
            mock_response.headers = {"Retry-After": "2"}
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await api.search("test query")
            assert result == []

    @pytest.mark.asyncio
    async def test_semantic_scholar_no_api_key(self, api_no_key):
        """Test behavior without API key"""
        result = await api_no_key.search("test query")
        assert result == []


class TestArxivAPI:
    """Test arXiv API integration"""

    @pytest.fixture
    def api(self):
        return ArxivAPI()

    @pytest.mark.asyncio
    async def test_arxiv_search_success(self, api):
        """Test successful arXiv search"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock successful XML response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text.return_value = """<?xml version="1.0" encoding="UTF-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom">
              <entry>
                <id>http://arxiv.org/abs/2301.00001</id>
                <title>Machine Learning in Healthcare: A Survey</title>
                <summary>This paper provides a comprehensive survey...</summary>
                <published>2023-01-01T00:00:00Z</published>
                <author>
                  <name>Test Author</name>
                </author>
                <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
                <link href="http://arxiv.org/pdf/2301.00001.pdf" rel="alternate" type="application/pdf"/>
              </entry>
            </feed>"""
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await api.search("machine learning healthcare")

            assert len(result) == 1
            assert result[0]["id"] == "2301.00001"
            assert "Machine Learning in Healthcare" in result[0]["title"]
            assert result[0]["summary"] == "This paper provides a comprehensive survey..."

    @pytest.mark.asyncio
    async def test_arxiv_query_formatting(self, api):
        """Test arXiv-specific query formatting"""
        # Test simple query
        formatted = api._format_query("machine learning healthcare")
        assert "all:" in formatted
        assert "machine+learning+healthcare" in formatted

        # Test complex query with operators
        formatted = api._format_query("machine learning AND healthcare")
        assert "AND" in formatted

    @pytest.mark.asyncio
    async def test_arxiv_rate_limiting(self, api):
        """Test rate limiting for arXiv API"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text.return_value = """<?xml version="1.0" encoding="UTF-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom"></feed>"""
            mock_get.return_value.__aenter__.return_value = mock_response

            start_time = time.time()

            # Make multiple rapid calls
            tasks = []
            for i in range(2):
                task = api.search(f"test query {i}")
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)

            elapsed = time.time() - start_time
            # Should take at least 3 seconds due to rate limiting (1 call per 3 seconds)
            assert elapsed >= 3.0

    @pytest.mark.asyncio
    async def test_arxiv_attribution_included(self, api):
        """Test proper arXiv attribution in results"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text.return_value = """<?xml version="1.0" encoding="UTF-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom">
              <entry>
                <id>http://arxiv.org/abs/2301.00001</id>
                <title>Test Paper</title>
                <summary>Test summary</summary>
              </entry>
            </feed>"""
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await api.search("test")

            # Should include attribution information
            assert "source" in result[0]
            assert result[0]["source"] == "arxiv"


class TestPubmedAPI:
    """Test PubMed/NCBI API integration"""

    @pytest.fixture
    def api(self):
        return PubmedAPI(email="test@example.com")

    @pytest.mark.asyncio
    async def test_pubmed_search_success(self, api):
        """Test successful PubMed search"""
        with patch('Bio.Entrez.esearch') as mock_esearch, \
             patch('Bio.Entrez.efetch') as mock_efetch:

            # Mock search response
            mock_esearch.return_value = {
                "IdList": ["12345678"]
            }

            # Mock fetch response
            mock_fetch_handle = MagicMock()
            mock_fetch_handle.read.return_value = """<?xml version="1.0"?>
            <!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2019//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_190101.dtd">
            <PubmedArticleSet>
              <PubmedArticle>
                <MedlineCitation>
                  <PMID Version="1">12345678</PMID>
                  <DateCreated>
                    <Year>2023</Year>
                    <Month>01</Month>
                    <Day>01</Day>
                  </DateCreated>
                  <Article>
                    <ArticleTitle>Machine Learning in Clinical Practice</ArticleTitle>
                    <Abstract>
                      <AbstractText>Application of ML in clinical settings...</AbstractText>
                    </Abstract>
                    <Journal>
                      <Title>Journal of Medical AI</Title>
                    </Journal>
                  </Article>
                </MedlineCitation>
              </PubmedArticle>
            </PubmedArticleSet>"""
            mock_efetch.return_value = mock_fetch_handle

            result = await api.search("machine learning clinical")

            assert len(result) == 1
            assert result[0]["pmid"] == "12345678"
            assert result[0]["title"] == "Machine Learning in Clinical Practice"
            assert "Application of ML in clinical settings" in result[0]["abstract"]

    @pytest.mark.asyncio
    async def test_pubmed_no_results(self, api):
        """Test PubMed search with no results"""
        with patch('Bio.Entrez.esearch') as mock_esearch:
            mock_esearch.return_value = {"IdList": []}

            result = await api.search("nonexistent query")

            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_pubmed_rate_limiting(self, api):
        """Test rate limiting for PubMed API"""
        with patch('Bio.Entrez.esearch') as mock_esearch, \
             patch('Bio.Entrez.efetch') as mock_efetch:

            mock_esearch.return_value = {"IdList": ["12345678"]}
            mock_fetch_handle = MagicMock()
            mock_fetch_handle.read.return_value = "<PubmedArticleSet></PubmedArticleSet>"
            mock_efetch.return_value = mock_fetch_handle

            start_time = time.time()

            # Make multiple rapid calls
            tasks = []
            for i in range(2):
                task = api.search(f"test query {i}")
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)

            elapsed = time.time() - start_time
            # Should take at least 0.34 seconds due to NCBI rate limiting (3 requests per second)
            assert elapsed >= 0.34

    @pytest.mark.asyncio
    async def test_pubmed_error_handling(self, api):
        """Test error handling for PubMed API"""
        with patch('Bio.Entrez.esearch') as mock_esearch:
            # Mock error response
            mock_esearch.side_effect = Exception("Network error")

            result = await api.search("test query")
            assert result == []


class TestAPIIntegrationManager:
    """Test unified API integration management"""

    @pytest.fixture
    def manager(self):
        return APIIntegrationManager(
            api_keys={
                "semantic_scholar": "test_key",
                "pubmed": "test@example.com"
            }
        )

    @pytest.mark.asyncio
    async def test_unified_search_formatting(self, manager):
        """Test unified query formatting across APIs"""
        query = "machine learning in healthcare"

        # Test semantic scholar formatting
        ss_query = manager.semantic_scholar._format_query(query)
        assert isinstance(ss_query, str)
        assert len(ss_query) > 0

        # Test arXiv formatting
        arxiv_query = manager.arxiv._format_query(query)
        assert "all:" in arxiv_query

        # Test PubMed formatting
        pubmed_query = manager.pubmed._format_query(query)
        assert isinstance(pubmed_query, str)

    @pytest.mark.asyncio
    async def test_parallel_api_search(self, manager):
        """Test parallel search across all APIs"""
        with patch.object(manager.semantic_scholar, 'search', new_callable=AsyncMock) as mock_ss, \
             patch.object(manager.arxiv, 'search', new_callable=AsyncMock) as mock_arxiv, \
             patch.object(manager.pubmed, 'search', new_callable=AsyncMock) as mock_pubmed:

            # Mock responses
            mock_ss.return_value = [{"title": "SS Paper", "paperId": "ss123"}]
            mock_arxiv.return_value = [{"title": "ArXiv Paper", "id": "arxiv123"}]
            mock_pubmed.return_value = [{"title": "PubMed Paper", "pmid": "pub123"}]

            results = await manager.search_all(query="machine learning")

            # Should have results from all APIs
            assert len(results) == 3

            # Check source tagging
            sources = [r.get("source") for r in results]
            assert "semantic_scholar" in sources
            assert "arxiv" in sources
            assert "pubmed" in sources

    @pytest.mark.asyncio
    async def test_exponential_backoff_retry(self, manager):
        """Test exponential backoff retry logic"""
        with patch.object(manager.semantic_scholar, 'search', new_callable=AsyncMock) as mock_search, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:

            # Fail first 2 attempts, succeed on 3rd
            mock_search.side_effect = [
                Exception("Rate limit"),
                Exception("Rate limit"),
                [{"title": "Success", "paperId": "success123"}]
            ]

            result = await manager.search_with_retry("semantic_scholar", "test query", max_retries=3)

            # Should succeed after retries
            assert len(result) == 1
            assert result[0]["title"] == "Success"

            # Verify that sleep was called for retry delays
            assert mock_sleep.call_count == 2
            # Verify exponential backoff (0.25s and 0.5s)
            expected_delays = [0.25, 0.5]
            actual_delays = [call.args[0] for call in mock_sleep.call_args_list]
            assert actual_delays == expected_delays

    @pytest.mark.asyncio
    async def test_api_health_check(self, manager):
        """Test API health checking functionality"""
        with patch.object(manager.semantic_scholar, 'search', new_callable=AsyncMock) as mock_ss, \
             patch.object(manager.arxiv, 'search', new_callable=AsyncMock) as mock_arxiv, \
             patch.object(manager.pubmed, 'search', new_callable=AsyncMock) as mock_pubmed:

            mock_ss.return_value = []
            mock_arxiv.return_value = []
            mock_pubmed.return_value = []

            health_status = await manager.check_api_health()

            assert "semantic_scholar" in health_status
            assert "arxiv" in health_status
            assert "pubmed" in health_status
            assert all(status["healthy"] for status in health_status.values())

    def test_api_availability_check(self, manager):
        """Test API availability based on credentials"""
        # Test with all credentials
        assert manager.is_available("semantic_scholar") == True
        assert manager.is_available("arxiv") == True
        assert manager.is_available("pubmed") == True

        # Test without Semantic Scholar key
        manager_no_ss = APIIntegrationManager()
        assert manager_no_ss.is_available("semantic_scholar") == False
        assert manager_no_ss.is_available("arxiv") == True

    def test_rate_limit_configuration(self, manager):
        """Test rate limit configuration per API"""
        # Semantic Scholar: 1 call per second
        assert manager.semantic_scholar.rate_limiter.max_calls == 1
        assert manager.semantic_scholar.rate_limiter.time_window == 1

        # arXiv: 1 call per 3 seconds
        assert manager.arxiv.rate_limiter.max_calls == 1
        assert manager.arxiv.rate_limiter.time_window == 3

        # PubMed: 3 calls per second
        assert manager.pubmed.rate_limiter.max_calls == 3
        assert manager.pubmed.rate_limiter.time_window == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])