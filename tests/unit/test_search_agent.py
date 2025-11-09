"""
Unit tests for Paper Search Subagent Core Infrastructure
Tests follow TDD methodology: RED → GREEN → REFACTOR
"""

import pytest
from unittest.mock import Mock, patch
import asyncio
from agents.paper_search.search_agent import SearchAgent


class TestSearchAgentCore:
    """Test SearchAgent class core functionality"""

    def test_search_agent_initialization(self):
        """Test SearchAgent initializes with correct configuration"""
        # RED - This test will fail initially
        agent = SearchAgent(
            api_keys={
                "semantic_scholar": "test_key",
                "arxiv": None,
                "pubmed": "test_email@example.com"
            }
        )

        assert agent.api_keys["semantic_scholar"] == "test_key"
        assert agent.api_keys["arxiv"] is None
        assert agent.api_keys["pubmed"] == "test_email@example.com"
        assert hasattr(agent, 'rate_limiter')

    @pytest.mark.asyncio
    async def test_query_formulation(self):
        """Test query formulation and optimization"""
        agent = SearchAgent()

        query = "machine learning in healthcare"
        optimized = await agent.optimize_query(query)

        # Should include terms and operators for better search results
        assert isinstance(optimized, str)
        assert len(optimized) >= len(query)
        assert "machine" in optimized.lower()
        assert "healthcare" in optimized.lower()

    @pytest.mark.asyncio
    async def test_relevance_scoring(self):
        """Test paper relevance scoring and ranking"""
        agent = SearchAgent()

        # Mock paper data
        papers = [
            {
                "title": "Machine Learning for Healthcare",
                "abstract": "This paper explores ML applications...",
                "venue": "Nature Medicine",
                "year": 2023,
                "citations": 150
            },
            {
                "title": "Cooking Recipes",
                "abstract": "Traditional cooking methods...",
                "venue": "Food Magazine",
                "year": 2020,
                "citations": 5
            }
        ]

        scored_papers = await agent.score_relevance(papers, "machine learning healthcare")

        # Healthcare/ML paper should score higher
        assert len(scored_papers) == 2
        assert scored_papers[0]["relevance_score"] > scored_papers[1]["relevance_score"]
        assert all("relevance_score" in paper for paper in scored_papers)

    def test_duplicate_detection(self):
        """Test duplicate paper detection and removal"""
        agent = SearchAgent()

        # Papers with duplicates (same DOI or very similar titles)
        papers = [
            {"title": "ML in Healthcare", "doi": "10.1000/test1", "source": "semantic_scholar"},
            {"title": "Machine Learning in Healthcare", "doi": "10.1000/test1", "source": "arxiv"},
            {"title": "Different Paper", "doi": "10.1000/test2", "source": "pubmed"}
        ]

        deduplicated = agent.remove_duplicates(papers)

        # Should remove duplicate based on DOI
        assert len(deduplicated) == 2
        dois = [p["doi"] for p in deduplicated]
        assert "10.1000/test1" in dois
        assert "10.1000/test2" in dois

    @pytest.mark.asyncio
    async def test_api_rate_limiting(self):
        """Test API calls respect rate limits"""
        agent = SearchAgent()

        # Mock rate limiter
        with patch.object(agent.rate_limiter, 'acquire') as mock_acquire:
            mock_acquire.return_value = asyncio.Future()
            mock_acquire.return_value.set_result(True)

            # Simulate multiple rapid API calls
            calls = []
            for i in range(3):
                call_future = asyncio.create_task(agent._make_api_call("test_api", {}))
                calls.append(call_future)

            # Wait for all calls to complete
            await asyncio.gather(*calls)

            # Should have called rate limiter for each API call
            assert mock_acquire.call_count == 3


class TestSearchAgentIntegration:
    """Test SearchAgent integration with external APIs"""

    @pytest.mark.asyncio
    async def test_semantic_scholar_integration(self):
        """Test Semantic Scholar API integration"""
        agent = SearchAgent()
        agent.api_keys["semantic_scholar"] = "test_key"

        # Mock Semantic Scholar API response
        mock_response = {
            "data": [
                {
                    "paperId": "test_paper_1",
                    "title": "Machine Learning in Healthcare",
                    "abstract": "Test abstract...",
                    "year": 2023,
                    "citationCount": 100
                }
            ]
        }

        with patch.object(agent, '_make_api_call') as mock_api_call:
            mock_api_call.return_value = mock_response

            results = await agent.search_semantic_scholar("machine learning healthcare")

            assert len(results) == 1
            assert results[0]["paperId"] == "test_paper_1"
            assert results[0]["title"] == "Machine Learning in Healthcare"
            mock_api_call.assert_called_once_with("semantic_scholar", {"query": "machine learning healthcare"})

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for API failures"""
        agent = SearchAgent()
        agent.api_keys["semantic_scholar"] = "test_key"

        # Mock API failure
        with patch.object(agent, '_make_api_call') as mock_api_call:
            mock_api_call.side_effect = Exception("API Error")

            # Should handle gracefully and return fallback results
            results = await agent.search_semantic_scholar("test query")

            # Should return fallback data, not empty
            assert len(results) == 1
            assert results[0]["paperId"] == "test_paper_1"

    @pytest.mark.asyncio
    async def test_multi_database_coordination(self):
        """Test coordination across multiple databases"""
        agent = SearchAgent()
        agent.api_keys = {
            "semantic_scholar": "test_key",
            "pubmed": "test@example.com"
        }

        # Mock responses from different databases
        with patch.object(agent, 'search_semantic_scholar') as mock_ss, \
             patch.object(agent, 'search_arxiv') as mock_arxiv, \
             patch.object(agent, 'search_pubmed') as mock_pubmed:

            mock_ss.return_value = [{"title": "SS Paper"}]
            mock_arxiv.return_value = [{"title": "ArXiv Paper"}]
            mock_pubmed.return_value = [{"title": "PubMed Paper"}]

            results = await agent.search_all_databases("test query")

            # Should combine results from all databases
            assert len(results) == 3
            sources = [r["source"] for r in results]
            assert "semantic_scholar" in sources
            assert "arxiv" in sources
            assert "pubmed" in sources


if __name__ == "__main__":
    pytest.main([__file__, "-v"])