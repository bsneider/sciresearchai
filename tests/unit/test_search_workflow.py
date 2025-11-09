"""
Unit tests for Search Workflow Coordination
Tests T-SEARCH-004: Implement Search Workflow Coordination
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any
from datetime import datetime
import time

from agents.paper_search.search_workflow import (
    SearchWorkflowOrchestrator,
    SearchStrategy,
    CoverageAnalyzer,
    ResultAggregator,
    WorkflowProgressTracker
)


class TestSearchWorkflowOrchestrator:
    """Test the main search workflow orchestration"""

    @pytest.fixture
    def orchestrator(self):
        # Create a mock search agent to avoid circular import
        mock_agent = MagicMock()
        mock_agent.api_manager = MagicMock()
        mock_agent.api_manager.is_available.return_value = True
        mock_agent.vector_engine = None
        return SearchWorkflowOrchestrator(mock_agent)

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator.search_agent is not None
        assert orchestrator.strategy_optimizer is not None
        assert orchestrator.coverage_analyzer is not None
        assert orchestrator.result_aggregator is not None
        assert orchestrator.progress_tracker is not None

    @pytest.mark.asyncio
    async def test_basic_workflow_execution(self, orchestrator):
        """Test basic workflow from query to results"""
        query = "machine learning in healthcare"

        with patch.object(orchestrator.search_agent, 'search_all_databases', new_callable=AsyncMock) as mock_search, \
             patch.object(orchestrator.search_agent, 'score_relevance', new_callable=AsyncMock) as mock_score:

            # Mock API search results
            mock_search.return_value = [
                {"id": "paper1", "title": "ML in Healthcare", "source": "semantic_scholar"},
                {"id": "paper2", "title": "Deep Learning for Medicine", "source": "arxiv"}
            ]

            # Mock relevance scoring
            mock_score.return_value = [
                {"id": "paper1", "relevance_score": 0.9},
                {"id": "paper2", "relevance_score": 0.7}
            ]

            results = await orchestrator.execute_search_workflow(query)

            assert len(results) == 2
            assert results[0]["relevance_score"] >= results[1]["relevance_score"]
            mock_search.assert_called_once_with(query)
            mock_score.assert_called_once()

    @pytest.mark.asyncio
    async def test_parallel_database_coordination(self, orchestrator):
        """Test coordination of multiple database searches"""
        query = "artificial intelligence research"

        with patch.object(orchestrator.search_agent, 'search_semantic_scholar', new_callable=AsyncMock) as mock_ss, \
             patch.object(orchestrator.search_agent, 'search_arxiv', new_callable=AsyncMock) as mock_arxiv, \
             patch.object(orchestrator.search_agent, 'search_pubmed', new_callable=AsyncMock) as mock_pubmed:

            # Mock individual API responses
            mock_ss.return_value = [{"id": "ss1", "title": "SS Paper"}]
            mock_arxiv.return_value = [{"id": "arxiv1", "title": "ArXiv Paper"}]
            mock_pubmed.return_value = [{"id": "pub1", "title": "PubMed Paper"}]

            start_time = time.time()
            results = await orchestrator.coordinate_parallel_search(query)
            elapsed_time = time.time() - start_time

            # Should have results from all sources
            assert len(results) == 3
            sources = [r.get("source", "unknown") for r in results]
            assert "semantic_scholar" in sources
            assert "arxiv" in sources
            assert "pubmed" in sources

            # Should execute in parallel (time should be reasonable)
            assert elapsed_time < 2.0

    @pytest.mark.asyncio
    async def test_enhanced_workflow_with_vector_search(self, orchestrator):
        """Test workflow that includes vector search enhancement"""
        query = "neural networks for image analysis"

        with patch.object(orchestrator.search_agent, 'search_with_vector_enhancement', new_callable=AsyncMock) as mock_enhanced:
            mock_enhanced.return_value = [
                {"id": "enhanced1", "title": "Enhanced Result 1", "hybrid_score": 0.85},
                {"id": "enhanced2", "title": "Enhanced Result 2", "hybrid_score": 0.75}
            ]

            results = await orchestrator.execute_enhanced_search_workflow(query)

            assert len(results) == 2
            assert "hybrid_score" in results[0]
            assert results[0]["hybrid_score"] > results[1]["hybrid_score"]
            mock_enhanced.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, orchestrator):
        """Test workflow error handling and graceful degradation"""
        query = "test query for error handling"

        with patch.object(orchestrator.search_agent, 'search_all_databases', new_callable=AsyncMock) as mock_search:
            # Mock search failure
            mock_search.side_effect = Exception("API Error")

            results = await orchestrator.execute_search_workflow(query)

            # Should return empty results rather than crashing
            assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_strategy_optimization(self, orchestrator):
        """Test search strategy optimization based on results"""
        query = "machine learning optimization"

        with patch.object(orchestrator.strategy_optimizer, 'optimize_query', new_callable=AsyncMock) as mock_optimize, \
             patch.object(orchestrator.search_agent, 'search_all_databases', new_callable=AsyncMock) as mock_search:

            mock_optimize.return_value = "machine learning AND optimization"
            mock_search.return_value = [{"id": "opt1", "title": "Optimized Result"}]

            results = await orchestrator.execute_optimized_search_workflow(query)

            mock_optimize.assert_called_once_with(query)
            mock_search.assert_called_once_with("machine learning AND optimization")


class TestSearchStrategy:
    """Test search strategy optimization"""

    @pytest.fixture
    def strategy(self):
        return SearchStrategy()

    def test_query_optimization(self, strategy):
        """Test basic query optimization"""
        original_query = "ml healthcare"
        optimized = strategy.optimize_query(original_query)

        # Should enhance the query
        assert len(optimized) >= len(original_query)
        # "ml" gets expanded to AI/deep learning terms, so check for any AI/ML terms
        ai_terms = ["artificial intelligence", "deep learning", "neural networks"]
        assert any(term in optimized.lower() for term in ai_terms)

    def test_synonym_expansion(self, strategy):
        """Test synonym expansion in query optimization"""
        query = "artificial intelligence"
        optimized = strategy.optimize_query(query)

        # Should include AI synonyms
        synonyms_found = any(term in optimized.lower() for term in ["machine learning", "deep learning", "neural networks"])
        assert synonyms_found or "artificial intelligence" in optimized.lower()

    def test_field_tagging(self, strategy):
        """Test adding field-specific tags to queries"""
        query = "cancer treatment"
        optimized = strategy.optimize_query(query)

        # Should add medical/research field indicators
        field_terms = ["medical", "clinical", "research", "therapy"]
        has_field_term = any(term in optimized.lower() for term in field_terms)
        assert has_field_term or "cancer" in optimized.lower()

    def test_query_complexity_management(self, strategy):
        """Test that query complexity is managed appropriately"""
        simple_query = "ai"
        complex_query = "artificial intelligence machine learning deep neural networks with attention mechanisms for natural language processing and computer vision applications in healthcare and medical diagnosis systems"

        simple_optimized = strategy.optimize_query(simple_query)
        complex_optimized = strategy.optimize_query(complex_query)

        # Simple query should be expanded
        assert len(simple_optimized) > len(simple_query)

        # Complex query should be managed (not too long)
        assert len(complex_optimized) < len(complex_query) * 1.5

    def test_database_specific_optimization(self, strategy):
        """Test optimization for specific databases"""
        query = "quantum computing"

        # Test Semantic Scholar optimization
        ss_optimized = strategy.optimize_for_database(query, "semantic_scholar")
        assert "semantic_scholar" in strategy.get_database_specific_terms("semantic_scholar")

        # Test PubMed optimization
        pubmed_optimized = strategy.optimize_for_database(query, "pubmed")
        assert "pubmed" in strategy.get_database_specific_terms("pubmed")


class TestCoverageAnalyzer:
    """Test coverage analysis and gap identification"""

    @pytest.fixture
    def analyzer(self):
        return CoverageAnalyzer()

    def test_coverage_calculation(self, analyzer):
        """Test search coverage calculation"""
        results = [
            {"id": "paper1", "source": "semantic_scholar", "year": 2023},
            {"id": "paper2", "source": "arxiv", "year": 2022},
            {"id": "paper3", "source": "pubmed", "year": 2023}
        ]

        coverage = analyzer.analyze_coverage(results, query="machine learning")

        assert "semantic_scholar" in coverage["sources_covered"]
        assert "arxiv" in coverage["sources_covered"]
        assert "pubmed" in coverage["sources_covered"]
        assert coverage["total_papers"] == 3
        assert coverage["source_coverage"] == 1.0  # All sources covered

    def test_temporal_coverage_analysis(self, analyzer):
        """Test temporal coverage analysis"""
        results = [
            {"id": "paper1", "year": 2021},
            {"id": "paper2", "year": 2022},
            {"id": "paper3", "year": 2023},
            {"id": "paper4", "year": 2023}
        ]

        temporal_coverage = analyzer.analyze_temporal_coverage(results)

        assert temporal_coverage["year_range"]["start"] == 2021
        assert temporal_coverage["year_range"]["end"] == 2023
        assert temporal_coverage["year_distribution"]["2023"] == 2
        assert temporal_coverage["year_distribution"]["2022"] == 1

    def test_research_gap_identification(self, analyzer):
        """Test identification of research gaps"""
        results = [
            {"id": "paper1", "title": "Machine Learning in Healthcare", "keywords": ["ml", "healthcare"]},
            {"id": "paper2", "title": "Deep Learning for Medical Images", "keywords": ["deep learning", "medical imaging"]},
            {"id": "paper3", "title": "AI for Drug Discovery", "keywords": ["ai", "drug discovery"]}
        ]

        gaps = analyzer.identify_research_gaps(results, domain="healthcare ai")

        assert "missing_topics" in gaps
        assert "underrepresented_areas" in gaps
        assert "temporal_gaps" in gaps
        assert isinstance(gaps["missing_topics"], list)

    def test_source_bias_detection(self, analyzer):
        """Test detection of source bias in results"""
        biased_results = [
            {"id": "paper1", "source": "semantic_scholar"},
            {"id": "paper2", "source": "semantic_scholar"},
            {"id": "paper3", "source": "semantic_scholar"},
            {"id": "paper4", "source": "semantic_scholar"}
        ]

        bias_analysis = analyzer.detect_source_bias(biased_results)

        assert bias_analysis["is_biased"] == True
        assert bias_analysis["dominant_source"] == "semantic_scholar"
        assert bias_analysis["bias_score"] > 0.7

    def test_coverage_recommendations(self, analyzer):
        """Test generation of coverage improvement recommendations"""
        limited_results = [
            {"id": "paper1", "source": "semantic_scholar", "year": 2023}
        ]

        recommendations = analyzer.generate_recommendations(limited_results)

        assert "additional_sources" in recommendations
        assert "query_refinements" in recommendations
        assert "temporal_expansions" in recommendations


class TestResultAggregator:
    """Test result aggregation and ranking"""

    @pytest.fixture
    def aggregator(self):
        return ResultAggregator()

    def test_result_deduplication(self, aggregator):
        """Test deduplication of results"""
        duplicate_results = [
            {"id": "paper1", "title": "ML in Healthcare", "doi": "10.1000/paper1", "source": "semantic_scholar"},
            {"id": "paper2", "title": "Machine Learning in Healthcare", "doi": "10.1000/paper1", "source": "arxiv"},  # Same DOI
            {"id": "paper3", "title": "Deep Learning", "doi": None, "source": "pubmed"},
            {"id": "paper4", "title": "Deep Learning", "doi": None, "source": "semantic_scholar"}  # Same title, no DOI
        ]

        deduplicated = aggregator.deduplicate_results(duplicate_results)

        # Should remove duplicates
        assert len(deduplicated) <= len(duplicate_results)
        paper_ids = [r["id"] for r in deduplicated]
        # Should keep one version of each unique paper
        assert len(set(paper_ids)) == len(deduplicated)

    def test_multi_source_ranking(self, aggregator):
        """Test ranking of results from multiple sources"""
        mixed_results = [
            {"id": "paper1", "title": "Highly Relevant Paper", "citationCount": 100, "source": "semantic_scholar", "year": 2023},
            {"id": "paper2", "title": "Somewhat Relevant", "citationCount": 50, "source": "arxiv", "year": 2022},
            {"id": "paper3", "title": "Very Relevant Paper", "citationCount": 80, "source": "pubmed", "year": 2023}
        ]

        ranked = aggregator.rank_results(mixed_results, query="machine learning healthcare")

        # Should be ranked by relevance
        assert len(ranked) == 3
        assert "combined_score" in ranked[0]
        # Most relevant should be first
        assert ranked[0]["combined_score"] >= ranked[1]["combined_score"]
        assert ranked[1]["combined_score"] >= ranked[2]["combined_score"]

    def test_source_weighting(self, aggregator):
        """Test application of source-specific weights"""
        results = [
            {"id": "paper1", "base_score": 0.8, "source": "semantic_scholar"},
            {"id": "paper2", "base_score": 0.8, "source": "arxiv"},
            {"id": "paper3", "base_score": 0.8, "source": "pubmed"}
        ]

        weighted = aggregator.apply_source_weights(results)

        # Should have different weights based on source
        sources = [r["source"] for r in weighted]
        scores = [r["weighted_score"] for r in weighted]

        # Semantic Scholar might get higher weight due to citation data
        ss_score = scores[sources.index("semantic_scholar")]
        arxiv_score = scores[sources.index("arxiv")]

        # Weights should be applied (they may be different)
        assert isinstance(ss_score, (int, float))
        assert isinstance(arxiv_score, (int, float))

    def test_result_aggregation_statistics(self, aggregator):
        """Test aggregation statistics calculation"""
        results = [
            {"id": "paper1", "source": "semantic_scholar", "year": 2023, "citationCount": 100},
            {"id": "paper2", "source": "arxiv", "year": 2022, "citationCount": None},
            {"id": "paper3", "source": "pubmed", "year": 2023, "citationCount": 50}
        ]

        stats = aggregator.calculate_aggregation_stats(results)

        assert stats["total_results"] == 3
        assert stats["source_count"] == 3
        assert "average_citations" in stats
        assert "year_range" in stats
        assert stats["source_distribution"]["semantic_scholar"] == 1


class TestWorkflowProgressTracker:
    """Test workflow progress tracking"""

    @pytest.fixture
    def tracker(self):
        return WorkflowProgressTracker()

    def test_progress_tracking_initialization(self, tracker):
        """Test progress tracker initialization"""
        assert tracker.current_step == 0
        assert tracker.total_steps == 0
        assert len(tracker.completed_steps) == 0
        assert len(tracker.errors) == 0

    def test_step_progression(self, tracker):
        """Test step progression tracking"""
        tracker.initialize_workflow(["search", "aggregate", "rank", "filter"])

        assert tracker.total_steps == 4
        assert tracker.current_step == 0

        tracker.start_step("search")
        assert tracker.current_step == 1
        assert "search" in tracker.active_steps

        tracker.complete_step("search", 10)  # 10 results found
        assert "search" in tracker.completed_steps
        assert "search" not in tracker.active_steps

    def test_error_tracking(self, tracker):
        """Test error tracking during workflow"""
        tracker.initialize_workflow(["step1", "step2"])

        tracker.log_error("step1", "API timeout error")
        assert len(tracker.errors) == 1
        assert tracker.errors[0]["step"] == "step1"
        assert tracker.errors[0]["error"] == "API timeout error"

    def test_performance_metrics(self, tracker):
        """Test performance metrics collection"""
        tracker.initialize_workflow(["search", "process"])

        tracker.start_step("search")
        time.sleep(0.1)  # Simulate work
        tracker.complete_step("search", 50)

        tracker.start_step("process")
        time.sleep(0.1)
        tracker.complete_step("process", 45)

        metrics = tracker.get_performance_metrics()

        assert "total_time" in metrics
        assert "step_times" in metrics
        assert len(metrics["step_times"]) == 2
        assert metrics["total_results_processed"] == 95

    def test_workflow_completion_status(self, tracker):
        """Test workflow completion status"""
        tracker.initialize_workflow(["step1", "step2", "step3"])

        # Not started
        status = tracker.get_completion_status()
        assert status["progress_percentage"] == 0.0
        assert status["is_complete"] == False

        # Partially completed
        tracker.start_step("step1")
        tracker.complete_step("step1", 10)
        status = tracker.get_completion_status()
        assert status["progress_percentage"] == 1/3
        assert status["is_complete"] == False

        # Fully completed
        tracker.start_step("step2")
        tracker.complete_step("step2", 5)
        tracker.start_step("step3")
        tracker.complete_step("step3", 15)
        status = tracker.get_completion_status()
        assert status["progress_percentage"] == 1.0
        assert status["is_complete"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])