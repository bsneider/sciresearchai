"""
Integration tests for complete search workflow
"""

import pytest
import asyncio
from agents.paper_search import SearchAgent


@pytest.mark.asyncio
class TestSearchWorkflow:
    """Test end-to-end search workflow"""

    async def test_complete_search_workflow(self):
        """Test complete workflow from query to ranked results"""
        # Initialize agent with API keys
        agent = SearchAgent({
            "semantic_scholar": "test_key",
            "pubmed": "test@example.com"
        })

        # Execute complete search workflow
        query = "machine learning in healthcare"

        # Step 1: Search across databases
        results = await agent.search_all_databases(query)
        assert len(results) > 0

        # Step 2: Remove duplicates
        unique_results = agent.remove_duplicates(results)
        assert len(unique_results) <= len(results)

        # Step 3: Score by relevance
        ranked_results = await agent.score_relevance(unique_results, query)
        assert len(ranked_results) == len(unique_results)

        # Verify ranking order (higher scores first)
        for i in range(1, len(ranked_results)):
            assert ranked_results[i-1]["relevance_score"] >= ranked_results[i]["relevance_score"]

        print(f"✅ Workflow complete: {len(ranked_results)} unique papers found and ranked")

    async def test_query_optimization(self):
        """Test query optimization improves search results"""
        agent = SearchAgent()

        original_query = "ml healthcare"
        optimized_query = await agent.optimize_query(original_query)

        # Optimized query should be longer (more terms)
        assert len(optimized_query) > len(original_query)
        assert "ml*" in optimized_query or "healthcare*" in optimized_query
        print(f"✅ Query optimized: '{original_query}' → '{optimized_query}'")

    async def test_rate_limiting_protection(self):
        """Test rate limiting prevents API abuse"""
        agent = SearchAgent()

        # Test multiple rapid calls
        start_time = asyncio.get_event_loop().time()

        # Make multiple API calls rapidly
        tasks = []
        for i in range(3):
            task = agent._make_api_call("test_api", {"query": f"test_{i}"})
            tasks.append(task)

        # Wait for all to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time

        # Should take some time due to rate limiting
        assert elapsed > 1.0, "Rate limiting should enforce delays"
        print(f"✅ Rate limiting active: {elapsed:.2f}s for 3 calls")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])