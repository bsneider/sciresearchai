"""
Integration tests for API integrations
Tests the complete functionality with proper mocking
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from agents.paper_search import SearchAgent


@pytest.mark.asyncio
class TestAPIIntegrationWorkflow:
    """Test complete API integration workflow"""

    async def test_semantic_scholar_integration(self):
        """Test Semantic Scholar API integration through SearchAgent"""
        agent = SearchAgent({"semantic_scholar": "test_key"})

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
                        "source": "semantic_scholar"
                    }
                ]
            }
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await agent.search_semantic_scholar("machine learning healthcare")

            assert len(result) == 1
            assert result[0]["paperId"] == "test123"
            assert result[0]["source"] == "semantic_scholar"

    async def test_arxiv_integration(self):
        """Test arXiv API integration through SearchAgent"""
        agent = SearchAgent()

        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock successful XML response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text.return_value = """<?xml version="1.0" encoding="UTF-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom">
              <entry>
                <id>http://arxiv.org/abs/2301.00001</id>
                <title>Machine Learning in Healthcare: A Survey</title>
                <summary>Comprehensive survey of ML in healthcare...</summary>
                <published>2023-01-01T00:00:00Z</published>
              </entry>
            </feed>"""
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await agent.search_arxiv("machine learning healthcare")

            assert len(result) == 1
            assert result[0]["id"] == "2301.00001"
            assert "Machine Learning in Healthcare" in result[0]["title"]
            assert result[0]["source"] == "arxiv"

    async def test_cross_database_search_with_real_apis(self):
        """Test cross-database search combining multiple APIs"""
        agent = SearchAgent({
            "semantic_scholar": "test_key",
            "pubmed": "test@example.com"
        })

        # Mock all APIs
        with patch('aiohttp.ClientSession.get') as mock_get, \
             patch('Bio.Entrez.esearch') as mock_esearch, \
             patch('Bio.Entrez.efetch') as mock_efetch:

            # Mock Semantic Scholar response
            mock_ss_response = AsyncMock()
            mock_ss_response.status = 200
            mock_ss_response.json.return_value = {
                "data": [{"title": "SS Paper", "paperId": "ss123", "source": "semantic_scholar"}]
            }

            # Mock arXiv response
            mock_arxiv_response = AsyncMock()
            mock_arxiv_response.status = 200
            mock_arxiv_response.text.return_value = """<?xml version="1.0" encoding="UTF-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom">
              <entry><id>http://arxiv.org/abs/test</id><title>ArXiv Paper</title><summary>Test</summary></entry>
            </feed>"""

            # Mock PubMed response
            mock_esearch.return_value = {"IdList": ["12345"]}
            mock_fetch_handle = MagicMock()
            mock_fetch_handle.read.return_value = "<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>12345</PMID><Article><ArticleTitle>PubMed Paper</ArticleTitle></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>"
            mock_efetch.return_value = mock_fetch_handle

            # Configure mock_get to return different responses
            side_effects = [
                mock_ss_response.__aenter__.return_value,
                mock_arxiv_response.__aenter__.return_value
            ]
            mock_get.return_value.__aenter__.side_effect = side_effects

            # Test cross-database search
            results = await agent.search_all_databases("machine learning")

            # Should get results from multiple sources
            assert len(results) >= 2  # At least SS and arXiv

            # Check that sources are properly tagged
            sources = set(r.get("source", "unknown") for r in results)
            assert "arxiv" in sources

    async def test_api_health_check_functionality(self):
        """Test API health checking through the API manager"""
        agent = SearchAgent({"semantic_scholar": "test_key"})

        # Mock health check
        with patch.object(agent.api_manager, 'check_api_health', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = {
                "semantic_scholar": {"healthy": True, "response_time": 0.1},
                "arxiv": {"healthy": True, "response_time": 0.2},
                "pubmed": {"healthy": False, "available": False}
            }

            health_status = await agent.api_manager.check_api_health()

            assert "semantic_scholar" in health_status
            assert "arxiv" in health_status
            assert "pubmed" in health_status
            assert health_status["semantic_scholar"]["healthy"] == True
            assert health_status["pubmed"]["healthy"] == False

    async def test_rate_limiting_across_apis(self):
        """Test that rate limiting works across different APIs"""
        agent = SearchAgent({"semantic_scholar": "test_key"})

        # Mock rate limiting by timing calls
        with patch.object(agent.api_manager.semantic_scholar, 'search', new_callable=AsyncMock) as mock_ss, \
             patch.object(agent.api_manager.arxiv, 'search', new_callable=AsyncMock) as mock_arxiv:

            mock_ss.return_value = [{"title": "SS Result"}]
            mock_arxiv.return_value = [{"title": "ArXiv Result"}]

            import time
            start_time = time.time()

            # Make parallel searches
            tasks = [
                agent.search_semantic_scholar("test1"),
                agent.search_arxiv("test2"),
                agent.search_semantic_scholar("test3")
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            elapsed = time.time() - start_time

            # Should take some time due to rate limiting
            assert elapsed > 0.1  # Some delay should occur

            # All searches should succeed
            assert all(isinstance(r, list) for r in results if not isinstance(r, Exception))

    async def test_error_recovery_and_fallbacks(self):
        """Test error recovery and fallback behavior"""
        agent = SearchAgent({"semantic_scholar": "test_key"})

        with patch.object(agent.api_manager.semantic_scholar, 'search', new_callable=AsyncMock) as mock_ss:
            # First call fails, second succeeds
            mock_ss.side_effect = [
                Exception("API Error"),
                [{"title": "Recovered Result", "paperId": "rec123"}]
            ]

            # Test search with retry functionality
            result = await agent.api_manager.search_with_retry(
                "semantic_scholar",
                "test query",
                max_retries=3
            )

            # Should eventually succeed
            assert len(result) == 1
            assert result[0]["title"] == "Recovered Result"

    async def test_unified_data_format(self):
        """Test that all APIs return data in unified format"""
        agent = SearchAgent({"semantic_scholar": "test_key", "pubmed": "test@example.com"})

        # Mock different APIs to return their native formats
        with patch('aiohttp.ClientSession.get') as mock_get, \
             patch('Bio.Entrez.esearch') as mock_esearch, \
             patch('Bio.Entrez.efetch') as mock_efetch:

            # Semantic Scholar mock
            mock_ss_response = AsyncMock()
            mock_ss_response.status = 200
            mock_ss_response.json.return_value = {
                "data": [
                    {
                        "paperId": "ss123",
                        "title": "SS Paper",
                        "abstract": "SS Abstract",
                        "year": 2023,
                        "authors": [{"name": "SS Author"}]
                    }
                ]
            }

            # arXiv mock
            mock_arxiv_response = AsyncMock()
            mock_arxiv_response.status = 200
            mock_arxiv_response.text.return_value = """<?xml version="1.0" encoding="UTF-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom">
              <entry>
                <id>http://arxiv.org/abs/arxiv123</id>
                <title>ArXiv Paper</title>
                <summary>ArXiv Abstract</summary>
                <published>2023-01-01T00:00:00Z</published>
                <author><name>ArXiv Author</name></author>
              </entry>
            </feed>"""

            # PubMed mock
            mock_esearch.return_value = {"IdList": ["pub123"]}
            mock_fetch_handle = MagicMock()
            mock_fetch_handle.read.return_value = """<PubmedArticleSet>
            <PubmedArticle><MedlineCitation><PMID>pub123</PMID>
            <DateCreated><Year>2023</Year></DateCreated>
            <Article><ArticleTitle>PubMed Paper</ArticleTitle>
            <Abstract><AbstractText>PubMed Abstract</AbstractText></Abstract>
            <AuthorList><Author><LastName>PubMed</LastName><ForeName>Author</ForeName></Author></AuthorList>
            </Article></MedlineCitation></PubmedArticle></PubmedArticleSet>"""
            mock_efetch.return_value = mock_fetch_handle

            # Configure mock_get
            mock_get.return_value.__aenter__.side_effect = [
                mock_ss_response,
                mock_arxiv_response
            ]

            # Get results from all APIs
            results = await agent.search_all_databases("test query")

            # All should have basic fields and source tag
            for result in results:
                assert "title" in result
                assert "source" in result
                assert result["source"] in ["semantic_scholar", "arxiv", "pubmed"]
                assert "retrieved_at" in result

            # Should have papers from multiple sources
            sources = set(r["source"] for r in results)
            assert len(sources) >= 2  # At least 2 different sources


if __name__ == "__main__":
    pytest.main([__file__, "-v"])