"""
Unit tests for Vector Search and Similarity System
Tests T-SEARCH-003: Create Vector Search and Similarity System
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any

from agents.paper_search.vector_search import (
    VectorSearchEngine,
    EmbeddingGenerator,
    SimilarityCalculator,
    HybridSearchRanker
)


class TestEmbeddingGenerator:
    """Test embedding generation using Sentence Transformers"""

    @pytest.fixture
    def embedding_gen(self):
        return EmbeddingGenerator(model_name="all-mpnet-base-v2")

    def test_embedding_generator_initialization(self, embedding_gen):
        """Test embedding generator initializes correctly"""
        assert embedding_gen.model_name == "all-mpnet-base-v2"
        assert embedding_gen.model is not None
        assert hasattr(embedding_gen, 'embedding_dim')

    def test_generate_single_embedding(self, embedding_gen):
        """Test generating embedding for a single text"""
        text = "Machine learning in healthcare applications"

        with patch.object(embedding_gen.model, 'encode') as mock_encode:
            # Mock embedding output (768 dimensions for all-mpnet-base-v2)
            mock_embedding = np.random.rand(768).astype(np.float32)
            mock_encode.return_value = mock_embedding

            embedding = embedding_gen.generate_embedding(text)

            assert isinstance(embedding, np.ndarray)
            assert embedding.shape == (768,)
            assert embedding.dtype == np.float32
            mock_encode.assert_called_once_with(text)

    def test_generate_batch_embeddings(self, embedding_gen):
        """Test generating embeddings for multiple texts"""
        texts = [
            "Machine learning in healthcare",
            "Deep learning for medical imaging",
            "Natural language processing in medicine"
        ]

        with patch.object(embedding_gen.model, 'encode') as mock_encode:
            # Mock batch embedding output
            mock_embeddings = np.random.rand(3, 768).astype(np.float32)
            mock_encode.return_value = mock_embeddings

            embeddings = embedding_gen.generate_batch_embeddings(texts)

            assert isinstance(embeddings, np.ndarray)
            assert embeddings.shape == (3, 768)
            assert embeddings.dtype == np.float32
            mock_encode.assert_called_once_with(texts)

    def test_embedding_caching(self, embedding_gen):
        """Test that embeddings are cached efficiently"""
        text = "Test text for caching"

        with patch.object(embedding_gen.model, 'encode') as mock_encode:
            mock_embedding = np.random.rand(768).astype(np.float32)
            mock_encode.return_value = mock_embedding

            # First call should use the model
            embedding1 = embedding_gen.generate_embedding(text)
            assert mock_encode.call_count == 1

            # Second call should use cache
            embedding2 = embedding_gen.generate_embedding(text)
            assert mock_encode.call_count == 1  # No additional calls

            # Embeddings should be identical
            np.testing.assert_array_equal(embedding1, embedding2)

    def test_embedding_dimension_validation(self, embedding_gen):
        """Test that embedding dimensions are validated"""
        with patch.object(embedding_gen.model, 'encode') as mock_encode:
            # Mock incorrect embedding dimension
            mock_embedding = np.random.rand(512).astype(np.float32)  # Wrong dimension
            mock_encode.return_value = mock_embedding

            with pytest.raises(ValueError, match="Expected embedding dimension"):
                embedding_gen.generate_embedding("test text")

    def test_cache_size_limit(self, embedding_gen):
        """Test that cache size is limited to prevent memory issues"""
        # Create many unique texts to exceed cache limit
        texts = [f"Unique text {i}" for i in range(1500)]  # Exceed default cache of 1000

        with patch.object(embedding_gen.model, 'encode') as mock_encode:
            mock_embeddings = np.random.rand(len(texts), 768).astype(np.float32)
            mock_encode.return_value = mock_embeddings

            # Generate embeddings for all texts
            for text in texts:
                embedding_gen.generate_embedding(text)

            # Cache should not grow beyond limit
            assert len(embedding_gen.cache) <= 1000


class TestSimilarityCalculator:
    """Test similarity calculation algorithms"""

    @pytest.fixture
    def similarity_calc(self):
        return SimilarityCalculator()

    def test_cosine_similarity_calculation(self, similarity_calc):
        """Test cosine similarity calculation"""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        vec3 = np.array([1.0, 0.0, 0.0])

        # Orthogonal vectors should have similarity 0
        similarity = similarity_calc.cosine_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 1e-6

        # Identical vectors should have similarity 1
        similarity = similarity_calc.cosine_similarity(vec1, vec3)
        assert abs(similarity - 1.0) < 1e-6

    def test_batch_similarity_calculation(self, similarity_calc):
        """Test calculating similarity for multiple pairs"""
        query_vec = np.array([1.0, 0.0, 0.0])
        doc_vectors = np.array([
            [1.0, 0.0, 0.0],  # Identical -> similarity 1
            [0.0, 1.0, 0.0],  # Orthogonal -> similarity 0
            [0.707, 0.707, 0.0]  # 45 degrees -> similarity 0.707
        ])

        similarities = similarity_calc.batch_cosine_similarity(query_vec, doc_vectors)

        assert len(similarities) == 3
        assert abs(similarities[0] - 1.0) < 1e-6
        assert abs(similarities[1] - 0.0) < 1e-6
        assert abs(similarities[2] - 0.707) < 0.01

    def test_euclidean_distance_calculation(self, similarity_calc):
        """Test Euclidean distance calculation"""
        vec1 = np.array([0.0, 0.0])
        vec2 = np.array([3.0, 4.0])

        distance = similarity_calc.euclidean_distance(vec1, vec2)
        assert abs(distance - 5.0) < 1e-6  # 3-4-5 triangle

    def test_dot_product_calculation(self, similarity_calc):
        """Test dot product calculation"""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([4.0, 5.0, 6.0])

        dot_product = similarity_calc.dot_product(vec1, vec2)
        expected = 1*4 + 2*5 + 3*6  # 32
        assert abs(dot_product - expected) < 1e-6

    def test_dimension_mismatch_handling(self, similarity_calc):
        """Test handling of dimension mismatches"""
        vec1 = np.array([1.0, 2.0])
        vec2 = np.array([1.0, 2.0, 3.0])

        with pytest.raises(ValueError, match="Dimension mismatch"):
            similarity_calc.cosine_similarity(vec1, vec2)


class TestHybridSearchRanker:
    """Test hybrid search ranking combining keyword and semantic"""

    @pytest.fixture
    def ranker(self):
        return HybridSearchRanker(
            semantic_weight=0.7,
            keyword_weight=0.3
        )

    def test_hybrid_scoring(self, ranker):
        """Test hybrid scoring combining semantic and keyword scores"""
        semantic_scores = np.array([0.8, 0.6, 0.9])
        keyword_scores = np.array([0.5, 0.7, 0.4])

        hybrid_scores = ranker.calculate_hybrid_scores(semantic_scores, keyword_scores)

        expected_0 = 0.7 * 0.8 + 0.3 * 0.5  # 0.71
        expected_1 = 0.7 * 0.6 + 0.3 * 0.7  # 0.63
        expected_2 = 0.7 * 0.9 + 0.3 * 0.4  # 0.75

        assert len(hybrid_scores) == 3
        assert abs(hybrid_scores[0] - expected_0) < 1e-6
        assert abs(hybrid_scores[1] - expected_1) < 1e-6
        assert abs(hybrid_scores[2] - expected_2) < 1e-6

    def test_score_normalization(self, ranker):
        """Test score normalization to 0-1 range"""
        scores = np.array([2.0, 5.0, 8.0])
        normalized = ranker.normalize_scores(scores)

        assert len(normalized) == 3
        assert abs(normalized[0] - 0.0) < 1e-6  # Min value -> 0
        assert abs(normalized[1] - 0.5) < 1e-6  # Middle value -> 0.5
        assert abs(normalized[2] - 1.0) < 1e-6  # Max value -> 1

    def test_ranking_order(self, ranker):
        """Test that documents are ranked correctly"""
        documents = [
            {"id": "doc1", "title": "Low Score"},
            {"id": "doc2", "title": "High Score"},
            {"id": "doc3", "title": "Medium Score"}
        ]
        scores = np.array([0.2, 0.9, 0.5])

        ranked_docs = ranker.rank_documents(documents, scores)

        assert ranked_docs[0]["id"] == "doc2"  # Highest score
        assert ranked_docs[1]["id"] == "doc3"  # Medium score
        assert ranked_docs[2]["id"] == "doc1"  # Lowest score

    def test_weight_validation(self, ranker):
        """Test that weights sum to 1.0"""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            HybridSearchRanker(semantic_weight=0.8, keyword_weight=0.3)  # Sum = 1.1

    def test_tie_breaking(self, ranker):
        """Test tie-breaking in ranking"""
        documents = [
            {"id": "doc1", "title": "First"},
            {"id": "doc2", "title": "Second"}
        ]
        scores = np.array([0.5, 0.5])  # Equal scores

        ranked_docs = ranker.rank_documents(documents, scores)

        # Should maintain original order for ties
        assert ranked_docs[0]["id"] == "doc1"
        assert ranked_docs[1]["id"] == "doc2"


class TestVectorSearchEngine:
    """Test the main vector search engine integration"""

    @pytest.fixture
    def search_engine(self):
        return VectorSearchEngine(
            model_name="all-mpnet-base-v2",
            collection_name="test_papers"
        )

    @pytest.mark.asyncio
    async def test_add_documents(self, search_engine):
        """Test adding documents to vector store"""
        documents = [
            {"id": "doc1", "title": "Machine Learning in Healthcare", "content": "ML applications in medicine"},
            {"id": "doc2", "title": "Deep Learning for Images", "content": "CNN applications for medical imaging"}
        ]

        with patch.object(search_engine.embedding_gen, 'generate_batch_embeddings') as mock_embed, \
             patch.object(search_engine.collection, 'add') as mock_add:

            mock_embed.return_value = np.random.rand(2, 768).astype(np.float32)
            mock_add.return_value = {"ids": ["doc1", "doc2"]}

            await search_engine.add_documents(documents)

            mock_embed.assert_called_once()
            mock_add.assert_called_once()

    @pytest.mark.asyncio
    async def test_semantic_search(self, search_engine):
        """Test semantic similarity search"""
        query = "machine learning applications in medicine"

        with patch.object(search_engine.embedding_gen, 'generate_embedding') as mock_embed, \
             patch.object(search_engine.collection, 'query') as mock_query:

            mock_embed.return_value = np.random.rand(768).astype(np.float32)
            mock_query.return_value = {
                "ids": ["doc1", "doc2"],
                "documents": ["Paper 1", "Paper 2"],
                "distances": [0.1, 0.2]
            }

            results = await search_engine.semantic_search(query, top_k=10)

            assert len(results) == 2
            assert "id" in results[0]
            assert "content" in results[0]
            assert "similarity_score" in results[0]

    @pytest.mark.asyncio
    async def test_hybrid_search(self, search_engine):
        """Test hybrid search combining semantic and keyword matching"""
        query = "machine learning healthcare"

        with patch.object(search_engine, 'semantic_search') as mock_semantic, \
             patch.object(search_engine.ranker, 'calculate_hybrid_scores') as mock_hybrid:

            mock_semantic.return_value = [
                {"id": "doc1", "content": "Paper about ML", "similarity_score": 0.8},
                {"id": "doc2", "content": "Paper about healthcare", "similarity_score": 0.6}
            ]
            mock_hybrid.return_value = np.array([0.75, 0.65])

            results = await search_engine.hybrid_search(query, top_k=5)

            assert len(results) == 2
            assert "hybrid_score" in results[0]
            assert results[0]["hybrid_score"] > results[1]["hybrid_score"]

    @pytest.mark.asyncio
    async def test_delete_documents(self, search_engine):
        """Test deleting documents from vector store"""
        doc_ids = ["doc1", "doc2"]

        with patch.object(search_engine.collection, 'delete') as mock_delete:
            mock_delete.return_value = {"ids": doc_ids}

            await search_engine.delete_documents(doc_ids)

            mock_delete.assert_called_once_with(ids=doc_ids)

    @pytest.mark.asyncio
    async def test_update_document(self, search_engine):
        """Test updating existing document"""
        document = {"id": "doc1", "title": "Updated Title", "content": "Updated content"}

        with patch.object(search_engine, 'delete_documents') as mock_delete, \
             patch.object(search_engine, 'add_documents') as mock_add:

            await search_engine.update_document(document)

            mock_delete.assert_called_once_with(["doc1"])
            mock_add.assert_called_once_with([document])

    def test_collection_management(self, search_engine):
        """Test ChromaDB collection management"""
        with patch('chromadb.Client') as mock_client:
            mock_collection = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection

            # Test collection creation
            search_engine._get_or_create_collection()
            mock_client.get_or_create_collection.assert_called_once_with(
                name="test_papers",
                metadata={"hnsw:space": "cosine"}
            )

    def test_error_handling_for_invalid_documents(self, search_engine):
        """Test error handling for invalid document formats"""
        invalid_documents = [
            {"id": None, "content": "Missing ID"},
            {"id": "doc2"},  # Missing content
            "not a dict"  # Invalid type
        ]

        with pytest.raises(ValueError, match="Invalid document format"):
            asyncio.run(search_engine.add_documents(invalid_documents))

    @pytest.mark.asyncio
    async def test_search_performance_monitoring(self, search_engine):
        """Test that search performance is monitored"""
        query = "test query"

        with patch.object(search_engine.embedding_gen, 'generate_embedding') as mock_embed, \
             patch.object(search_engine.collection, 'query') as mock_query:

            mock_embed.return_value = np.random.rand(768).astype(np.float32)
            mock_query.return_value = {"ids": [], "documents": [], "distances": []}

            import time
            start_time = time.time()
            await search_engine.semantic_search(query)
            elapsed_time = time.time() - start_time

            # Performance should be reasonable
            assert elapsed_time < 5.0  # Should complete within 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])