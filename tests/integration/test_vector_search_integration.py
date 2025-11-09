"""
Integration tests for Vector Search System
Tests complete vector search workflow with SearchAgent integration
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from agents.paper_search import SearchAgent, VectorSearchEngine


@pytest.mark.asyncio
class TestVectorSearchIntegration:
    """Test vector search integration with SearchAgent"""

    async def test_vector_search_initialization(self):
        """Test that SearchAgent initializes vector search correctly"""
        agent = SearchAgent()

        # Vector search should be initialized if dependencies are available
        assert hasattr(agent, 'vector_search')

        # Should either be VectorSearchEngine instance or None (if deps missing)
        if agent.vector_search is not None:
            assert isinstance(agent.vector_search, VectorSearchEngine)

    async def test_add_papers_to_vector_store(self):
        """Test adding papers to vector store"""
        agent = SearchAgent()

        # Mock papers
        papers = [
            {
                "id": "paper1",
                "title": "Machine Learning in Healthcare",
                "abstract": "Applications of ML in medical diagnosis",
                "content": "This paper explores ML applications..."
            },
            {
                "id": "paper2",
                "title": "Deep Learning for Image Analysis",
                "abstract": "CNN applications in medical imaging",
                "content": "Deep learning techniques..."
            }
        ]

        # Test adding papers (should work even if vector search unavailable)
        await agent.add_papers_to_vector_store(papers)

        # No exception should be raised
        assert True

    async def test_vector_search_functionality(self):
        """Test vector search functionality"""
        agent = SearchAgent()

        # Test vector search (should return empty list if no papers stored)
        results = await agent.vector_search("machine learning healthcare")

        # Should return list (empty if no papers)
        assert isinstance(results, list)

    async def test_hybrid_search_enhancement(self):
        """Test enhanced search combining API and vector search"""
        agent = SearchAgent({"semantic_scholar": "test_key"})

        # Mock API search
        with patch.object(agent.api_manager, 'search_all', new_callable=AsyncMock) as mock_api_search:
            mock_api_search.return_value = [
                {
                    "id": "api_paper1",
                    "title": "API Paper 1",
                    "abstract": "Abstract from API",
                    "source": "semantic_scholar"
                }
            ]

            # Mock vector search
            with patch.object(agent, 'vector_search', new_callable=AsyncMock) as mock_vector_search:
                mock_vector_search.return_value = [
                    {
                        "id": "vector_paper1",
                        "content": "Vector search result",
                        "hybrid_score": 0.85
                    }
                ]

                results = await agent.search_with_vector_enhancement("machine learning")

                # Should combine results from both sources
                assert len(results) >= 1

                # Check that both searches were called
                mock_api_search.assert_called_once()
                mock_vector_search.assert_called_once()

    async def test_vector_search_error_handling(self):
        """Test error handling in vector search"""
        agent = SearchAgent()

        # Test with invalid search type
        with pytest.raises(ValueError, match="Unknown search type"):
            await agent.vector_search("test", search_type="invalid_type")

    async def test_semantic_vs_hybrid_search(self):
        """Test difference between semantic and hybrid search"""
        agent = SearchAgent()

        # Mock vector search responses
        with patch.object(agent.vector_engine, 'semantic_search', new_callable=AsyncMock) as mock_semantic, \
             patch.object(agent.vector_engine, 'hybrid_search', new_callable=AsyncMock) as mock_hybrid:

            mock_semantic.return_value = [
                {"id": "semantic1", "similarity_score": 0.9}
            ]
            mock_hybrid.return_value = [
                {"id": "hybrid1", "hybrid_score": 0.85}
            ]

            # Test semantic search
            semantic_results = await agent.vector_search("test", search_type="semantic")
            assert len(semantic_results) == 1
            mock_semantic.assert_called_once()

            # Test hybrid search
            hybrid_results = await agent.vector_search("test", search_type="hybrid")
            assert len(hybrid_results) == 1
            mock_hybrid.assert_called_once()

    async def test_paper_preparation_for_embedding(self):
        """Test paper text preparation for embedding"""
        engine = VectorSearchEngine()

        # Test paper with title, abstract, and content
        paper = {
            "id": "test_paper",
            "title": "Test Title",
            "abstract": "Test Abstract",
            "content": "Test Content"
        }

        prepared_text = engine._prepare_document_text(paper)
        expected = "Test Title Test Abstract Test Content"
        assert prepared_text == expected

        # Test paper with only title
        paper_title_only = {"id": "test2", "title": "Only Title"}
        prepared_text = engine._prepare_document_text(paper_title_only)
        assert prepared_text == "Only Title"

    async def test_vector_search_with_real_model(self):
        """Test vector search with actual sentence transformer model (if available)"""
        try:
            engine = VectorSearchEngine()

            # Test embedding generation
            text = "Machine learning in healthcare applications"
            embedding = engine.embedding_gen.generate_embedding(text)

            assert isinstance(embedding, list) or isinstance(embedding, type(None))

            # Test similarity calculation
            vec1 = engine.embedding_gen.generate_embedding("similar text")
            vec2 = engine.embedding_gen.generate_embedding("different text")

            if vec1 is not None and vec2 is not None:
                similarity = engine.similarity_calc.cosine_similarity(vec1, vec2)
                assert isinstance(similarity, (int, float))
                assert 0 <= similarity <= 1

        except ImportError:
            pytest.skip("Sentence transformers not available")

    async def test_batch_embedding_generation(self):
        """Test batch embedding generation"""
        try:
            engine = VectorSearchEngine()

            texts = [
                "Machine learning in healthcare",
                "Deep learning for images",
                "Natural language processing"
            ]

            embeddings = engine.embedding_gen.generate_batch_embeddings(texts)

            if embeddings is not None:
                assert len(embeddings) == 3
                assert all(isinstance(emb, list) for emb in embeddings)

        except ImportError:
            pytest.skip("Sentence transformers not available")

    async def test_hybrid_search_ranking(self):
        """Test hybrid search ranking functionality"""
        try:
            engine = VectorSearchEngine()
            ranker = engine.ranker

            # Test hybrid scoring
            semantic_scores = [0.8, 0.6, 0.9]
            keyword_scores = [0.5, 0.7, 0.4]

            hybrid_scores = ranker.calculate_hybrid_scores(
                semantic_scores, keyword_scores
            )

            assert len(hybrid_scores) == 3
            assert all(0 <= score <= 1 for score in hybrid_scores)

        except ImportError:
            pytest.skip("ChromaDB not available")

    async def test_vector_search_performance(self):
        """Test vector search performance characteristics"""
        try:
            engine = VectorSearchEngine()

            # Test embedding generation speed
            import time
            start_time = time.time()

            text = "Performance test text for embedding generation"
            embedding = engine.embedding_gen.generate_embedding(text)

            elapsed_time = time.time() - start_time

            # Should complete within reasonable time (5 seconds)
            assert elapsed_time < 5.0

        except ImportError:
            pytest.skip("Vector search dependencies not available")


@pytest.mark.asyncio
class TestVectorSearchWorkflow:
    """Test end-to-end vector search workflow"""

    async def test_complete_vector_search_workflow(self):
        """Test complete workflow from paper addition to search"""
        try:
            agent = SearchAgent()

            # Step 1: Add papers to vector store
            papers = [
                {
                    "id": "workflow_test_1",
                    "title": "Neural Networks in Medicine",
                    "abstract": "Applications of neural networks in medical diagnosis",
                    "content": "This comprehensive review explores..."
                },
                {
                    "id": "workflow_test_2",
                    "title": "AI for Drug Discovery",
                    "abstract": "Machine learning approaches to pharmaceutical research",
                    "content": "Artificial intelligence is transforming..."
                }
            ]

            await agent.add_papers_to_vector_store(papers)

            # Step 2: Perform vector search
            results = await agent.vector_search("neural networks medicine", search_type="semantic")

            # Step 3: Verify results structure
            assert isinstance(results, list)

            if results:  # If vector search worked and found results
                for result in results:
                    assert "id" in result or "content" in result

        except ImportError:
            pytest.skip("Vector search dependencies not available")

    async def test_vector_vs_api_search_comparison(self):
        """Test comparing vector search results with API search results"""
        agent = SearchAgent({"semantic_scholar": "test_key"})

        # Mock API search
        with patch.object(agent.api_manager, 'search_all', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = [
                {"id": "api_1", "title": "API Result 1", "source": "semantic_scholar"}
            ]

            # Get API results
            api_results = await agent.search_all_databases("machine learning")

            # Get vector search results
            vector_results = await agent.vector_search("machine learning")

            # Both should return lists
            assert isinstance(api_results, list)
            assert isinstance(vector_results, list)

            # API results should have source information
            if api_results:
                assert "source" in api_results[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])