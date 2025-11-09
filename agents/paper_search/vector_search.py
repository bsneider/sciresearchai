"""
Vector Search and Similarity System
Implements T-SEARCH-003: Create Vector Search and Similarity System

Provides semantic search capabilities using:
- Sentence Transformers (all-mpnet-base-v2)
- ChromaDB vector storage
- Hybrid keyword + semantic search
- Embedding generation and caching
"""

import asyncio
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache
import time

# Import ChromaDB for vector storage
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Vector search disabled.")

# Import Sentence Transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("Sentence Transformers not available. Using mock embeddings.")


class EmbeddingGenerator:
    """Handles embedding generation using Sentence Transformers with caching"""

    def __init__(self, model_name: str = "all-mpnet-base-v2", cache_size: int = 1000):
        self.model_name = model_name
        self.cache_size = cache_size
        self.cache = {}

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
            except Exception as e:
                logging.error(f"Failed to load Sentence Transformer model: {e}")
                self.model = None
                self.embedding_dim = 768  # Default for all-mpnet-base-v2
        else:
            self.model = None
            self.embedding_dim = 768

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        if text in self.cache:
            return self.cache[text]

        try:
            if self.model is not None:
                embedding = self.model.encode(text, convert_to_numpy=True)
            else:
                # Fallback: random embedding (for testing without dependencies)
                embedding = np.random.rand(self.embedding_dim).astype(np.float32)

            # Validate embedding dimension
            if embedding.shape != (self.embedding_dim,):
                raise ValueError(
                    f"Expected embedding dimension ({self.embedding_dim},), "
                    f"got {embedding.shape}"
                )

            # Cache the embedding
            self._add_to_cache(text, embedding)
            return embedding

        except Exception as e:
            logging.error(f"Error generating embedding: {e}")
            # Return zero embedding as fallback
            return np.zeros(self.embedding_dim, dtype=np.float32)

    def generate_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        try:
            if self.model is not None:
                embeddings = self.model.encode(texts, convert_to_numpy=True)
            else:
                # Fallback: random embeddings
                embeddings = np.random.rand(len(texts), self.embedding_dim).astype(np.float32)

            # Validate embedding dimensions
            if embeddings.shape != (len(texts), self.embedding_dim):
                raise ValueError(
                    f"Expected batch embeddings shape ({len(texts)}, {self.embedding_dim}), "
                    f"got {embeddings.shape}"
                )

            # Cache embeddings
            for text, embedding in zip(texts, embeddings):
                self._add_to_cache(text, embedding)

            return embeddings

        except Exception as e:
            logging.error(f"Error generating batch embeddings: {e}")
            # Return zero embeddings as fallback
            return np.zeros((len(texts), self.embedding_dim), dtype=np.float32)

    def _add_to_cache(self, text: str, embedding: np.ndarray):
        """Add embedding to cache with size limit"""
        if len(self.cache) >= self.cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[text] = embedding.copy()


class SimilarityCalculator:
    """Handles similarity calculations between vectors"""

    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        if vec1.shape != vec2.shape:
            raise ValueError(f"Dimension mismatch: {vec1.shape} vs {vec2.shape}")

        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    @staticmethod
    def batch_cosine_similarity(query_vec: np.ndarray, doc_vectors: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and multiple documents"""
        if query_vec.shape[0] != doc_vectors.shape[1]:
            raise ValueError(f"Dimension mismatch: query {query_vec.shape} vs docs {doc_vectors.shape}")

        # Normalize query vector
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return np.zeros(doc_vectors.shape[0])

        query_normalized = query_vec / query_norm

        # Normalize document vectors
        doc_norms = np.linalg.norm(doc_vectors, axis=1)
        doc_norms[doc_norms == 0] = 1  # Avoid division by zero
        doc_normalized = doc_vectors / doc_norms.reshape(-1, 1)

        # Calculate cosine similarities
        similarities = np.dot(doc_normalized, query_normalized)
        return similarities

    @staticmethod
    def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate Euclidean distance between two vectors"""
        if vec1.shape != vec2.shape:
            raise ValueError(f"Dimension mismatch: {vec1.shape} vs {vec2.shape}")

        return np.linalg.norm(vec1 - vec2)

    @staticmethod
    def dot_product(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate dot product between two vectors"""
        if vec1.shape != vec2.shape:
            raise ValueError(f"Dimension mismatch: {vec1.shape} vs {vec2.shape}")

        return np.dot(vec1, vec2)


class HybridSearchRanker:
    """Handles hybrid search ranking combining semantic and keyword scores"""

    def __init__(self, semantic_weight: float = 0.7, keyword_weight: float = 0.3):
        if not np.isclose(semantic_weight + keyword_weight, 1.0):
            raise ValueError("Weights must sum to 1.0")

        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight

    def calculate_hybrid_scores(self, semantic_scores: np.ndarray, keyword_scores: np.ndarray) -> np.ndarray:
        """Calculate hybrid scores combining semantic and keyword scores"""
        if semantic_scores.shape != keyword_scores.shape:
            raise ValueError(f"Score arrays must have same shape: {semantic_scores.shape} vs {keyword_scores.shape}")

        # Normalize scores to 0-1 range
        semantic_norm = self.normalize_scores(semantic_scores)
        keyword_norm = self.normalize_scores(keyword_scores)

        # Calculate weighted combination
        hybrid_scores = (self.semantic_weight * semantic_norm +
                        self.keyword_weight * keyword_norm)

        return hybrid_scores

    def normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """Normalize scores to 0-1 range"""
        if len(scores) == 0:
            return scores

        min_score = np.min(scores)
        max_score = np.max(scores)

        if max_score == min_score:
            return np.ones_like(scores)

        return (scores - min_score) / (max_score - min_score)

    def rank_documents(self, documents: List[Dict], scores: np.ndarray) -> List[Dict]:
        """Rank documents based on scores"""
        if len(documents) != len(scores):
            raise ValueError(f"Number of documents ({len(documents)}) must match number of scores ({len(scores)})")

        # Pair documents with scores
        scored_docs = list(zip(documents, scores))

        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Return ranked documents with scores
        ranked_docs = []
        for doc, score in scored_docs:
            doc_copy = doc.copy()
            doc_copy["hybrid_score"] = float(score)
            ranked_docs.append(doc_copy)

        return ranked_docs


class VectorSearchEngine:
    """Main vector search engine integrating all components"""

    def __init__(self, model_name: str = "all-mpnet-base-v2", collection_name: str = "papers"):
        self.model_name = model_name
        self.collection_name = collection_name

        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is required for vector search")

        # Initialize components
        self.embedding_gen = EmbeddingGenerator(model_name)
        self.similarity_calc = SimilarityCalculator()
        self.ranker = HybridSearchRanker()

        # Initialize ChromaDB
        self.client = chromadb.Client(Settings())
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Get or create ChromaDB collection"""
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

    def _validate_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Validate document format"""
        for doc in documents:
            if not isinstance(doc, dict):
                raise ValueError(f"Document must be dict, got {type(doc)}")
            if "id" not in doc or not doc["id"]:
                raise ValueError("Document must have non-empty 'id' field")
            if "content" not in doc and "title" not in doc:
                raise ValueError("Document must have 'content' or 'title' field")

    def _prepare_document_text(self, doc: Dict[str, Any]) -> str:
        """Prepare text for embedding from document"""
        text_parts = []

        if "title" in doc and doc["title"]:
            text_parts.append(doc["title"])

        if "content" in doc and doc["content"]:
            text_parts.append(doc["content"])

        if "abstract" in doc and doc["abstract"]:
            text_parts.append(doc["abstract"])

        return " ".join(text_parts)

    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to vector store"""
        self._validate_documents(documents)

        # Prepare text for embedding
        texts = [self._prepare_document_text(doc) for doc in documents]

        # Generate embeddings
        embeddings = self.embedding_gen.generate_batch_embeddings(texts)

        # Prepare documents for ChromaDB
        ids = [doc["id"] for doc in documents]
        documents_for_db = [self._prepare_document_text(doc) for doc in documents]
        metadatas = []

        for doc in documents:
            metadata = {k: v for k, v in doc.items() if k not in ["id", "content", "abstract"]}
            metadatas.append(metadata)

        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            documents=documents_for_db,
            metadatas=metadatas,
            embeddings=embeddings.tolist()
        )

        logging.info(f"Added {len(documents)} documents to vector store")

    async def semantic_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic similarity search"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_gen.generate_embedding(query)

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )

            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    result = {
                        "id": doc_id,
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "similarity_score": 1 - results["distances"][0][i] if results["distances"] else 0.0,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                    }
                    formatted_results.append(result)

            return formatted_results

        except Exception as e:
            logging.error(f"Error in semantic search: {e}")
            return []

    async def hybrid_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and keyword matching"""
        try:
            # Get semantic search results
            semantic_results = await self.semantic_search(query, top_k * 2)  # Get more for reranking

            if not semantic_results:
                return []

            # Extract semantic scores
            semantic_scores = np.array([r["similarity_score"] for r in semantic_results])

            # Calculate keyword scores (simple text matching for now)
            query_terms = set(query.lower().split())
            keyword_scores = []

            for result in semantic_results:
                content = (result.get("content", "") + " " +
                          " ".join(result.get("metadata", {}).values())).lower()

                # Simple keyword matching score
                matching_terms = sum(1 for term in query_terms if term in content)
                keyword_score = matching_terms / len(query_terms) if query_terms else 0.0
                keyword_scores.append(keyword_score)

            keyword_scores = np.array(keyword_scores)

            # Calculate hybrid scores
            hybrid_scores = self.ranker.calculate_hybrid_scores(semantic_scores, keyword_scores)

            # Rank documents by hybrid scores
            ranked_results = self.ranker.rank_documents(semantic_results, hybrid_scores)

            # Return top_k results
            return ranked_results[:top_k]

        except Exception as e:
            logging.error(f"Error in hybrid search: {e}")
            return []

    async def delete_documents(self, doc_ids: List[str]) -> None:
        """Delete documents from vector store"""
        try:
            self.collection.delete(ids=doc_ids)
            logging.info(f"Deleted {len(doc_ids)} documents from vector store")
        except Exception as e:
            logging.error(f"Error deleting documents: {e}")

    async def update_document(self, document: Dict[str, Any]) -> None:
        """Update existing document in vector store"""
        self._validate_documents([document])

        # Delete existing document
        await self.delete_documents([document["id"]])

        # Add updated document
        await self.add_documents([document])

    async def search_with_timing(self, query: str, search_type: str = "semantic", top_k: int = 10) -> Dict[str, Any]:
        """Perform search with timing information"""
        start_time = time.time()

        if search_type == "semantic":
            results = await self.semantic_search(query, top_k)
        elif search_type == "hybrid":
            results = await self.hybrid_search(query, top_k)
        else:
            raise ValueError(f"Unknown search type: {search_type}")

        elapsed_time = time.time() - start_time

        return {
            "results": results,
            "query": query,
            "search_type": search_type,
            "num_results": len(results),
            "elapsed_time": elapsed_time
        }

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "model_name": self.model_name,
                "embedding_dimension": self.embedding_gen.embedding_dim
            }
        except Exception as e:
            logging.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}