# Paper Search Subagent

Core infrastructure for comprehensive literature discovery and retrieval across multiple scientific databases.

## Features

- **Multi-database Search**: Integration with Semantic Scholar, arXiv, and PubMed/NCBI
- **Rate Limiting**: Respects API rate limits with configurable backoff strategies
- **Query Optimization**: Improves search queries for better coverage
- **Relevance Scoring**: Ranks papers by relevance to research queries
- **Duplicate Detection**: Removes duplicate papers based on DOI and title similarity
- **Error Handling**: Graceful degradation with fallback mechanisms

## Usage

```python
from agents.paper_search import SearchAgent

# Initialize with API keys
agent = SearchAgent({
    "semantic_scholar": "your_api_key",
    "pubmed": "your_email@example.com"
})

# Search across all databases
results = await agent.search_all_databases("machine learning in healthcare")

# Search specific database
ss_results = await agent.search_semantic_scholar("artificial intelligence")

# Score papers by relevance
ranked_papers = await agent.score_relevance(papers, query)

# Vector search on stored papers
vector_results = await agent.vector_search("machine learning healthcare", search_type="hybrid")

# Enhanced search combining API and vector search
enhanced_results = await agent.search_with_vector_enhancement("deep learning medical imaging")

# Add papers to vector store
await agent.add_papers_to_vector_store(papers)

# Execute complete search workflow with orchestration
workflow_results = await agent.execute_search_workflow("machine learning healthcare")

# Execute enhanced workflow with vector search
enhanced_results = await agent.execute_enhanced_search_workflow("deep learning medical imaging")

# Analyze search coverage and performance
analysis = await agent.analyze_search_coverage(results, query)
```

## Architecture

The SearchAgent follows TDD principles with comprehensive test coverage for:

- Core functionality (initialization, query optimization)
- API integration with Semantic Scholar, arXiv, PubMed
- Vector search with Sentence Transformers and ChromaDB
- Hybrid search combining semantic and keyword matching
- Search workflow orchestration and coordination
- Multi-database query coordination and parallel processing
- Result aggregation and ranking system
- Coverage analysis and gap identification
- Search strategy optimization and feedback loops
- Scoring and ranking algorithms
- Duplicate detection and removal
- Rate limiting and API coordination
- Error handling and fallback mechanisms
- Integration with external APIs and vector databases

## Dependencies

- `aiohttp`: Async HTTP client for API calls
- `biopython`: NCBI/PubMed E-utilities integration
- `sentence-transformers`: Embedding generation with all-mpnet-base-v2
- `chromadb`: Vector storage and similarity search
- `tenacity`: Retry logic with exponential backoff
- `asyncio`: Async/await for concurrent operations

## Configuration

API keys should be provided during initialization:

```python
api_keys = {
    "semantic_scholar": "semantic_scholar_api_key",  # Required for Semantic Scholar
    "arxiv": None,                                    # Not required (no key needed)
    "pubmed": "email@example.com"                     # Required for NCBI access
}
```

## API Integration Details

### Semantic Scholar API
- **Rate Limiting**: 1 call per second with exponential backoff
- **Authentication**: API key required in headers
- **Data Format**: JSON with paper metadata, citations, authors
- **Fields Retrieved**: paperId, title, abstract, year, citationCount, authors, venue, url

### arXiv API
- **Rate Limiting**: 1 call per 3 seconds (respectful use)
- **Authentication**: None required (public API)
- **Data Format**: XML parsed to structured data
- **Attribution**: Proper User-Agent and attribution included
- **Fields Retrieved**: id, title, summary, authors, categories, publication date, PDF URL

### PubMed/NCBI API
- **Rate Limiting**: 3 calls per second (NCBI guidelines)
- **Authentication**: Email required (API key optional for higher limits)
- **Data Format**: XML via BioPython Entrez
- **Fields Retrieved**: PMID, title, abstract, authors, journal, publication date

## Vector Search System

The system provides advanced vector search capabilities:

### Sentence Transformer Integration
- **Model**: all-mpnet-base-v2 (768-dimensional embeddings)
- **Embedding Caching**: LRU cache with configurable size limit
- **Batch Processing**: Efficient generation of multiple embeddings
- **Dimension Validation**: Ensures consistent embedding dimensions

### ChromaDB Vector Storage
- **Collection Management**: Automatic collection creation and management
- **Similarity Metrics**: Cosine similarity for document matching
- **Metadata Support**: Flexible metadata storage and retrieval
- **Performance Optimized**: HNSW indexing for fast approximate search

### Hybrid Search Ranking
- **Semantic Scoring**: Vector similarity using Sentence Transformers
- **Keyword Matching**: Text-based keyword relevance scoring
- **Weighted Combination**: Configurable semantic (70%) + keyword (30%) weights
- **Score Normalization**: Min-max normalization to 0-1 range

### Search Types
- **Semantic Search**: Pure vector similarity search
- **Hybrid Search**: Combined semantic + keyword ranking
- **Enhanced Search**: API results + vector search with re-ranking

## Search Workflow Coordination

The system provides sophisticated workflow orchestration:

### Search Workflow Orchestrator
- **End-to-End Orchestration**: Complete search pipeline management
- **Multi-Step Processing**: Step-by-step workflow with progress tracking
- **Error Recovery**: Graceful handling of failures at each stage
- **Performance Monitoring**: Detailed metrics and timing analysis

### Multi-Database Coordination
- **Parallel Search**: Concurrent searches across Semantic Scholar, arXiv, PubMed
- **Query Optimization**: Database-specific query enhancement
- **Result Aggregation**: Intelligent combination of results from multiple sources
- **Load Balancing**: Distributed processing to avoid API rate limits

### Coverage Analysis
- **Source Coverage**: Analysis of database representation in results
- **Temporal Coverage**: Year distribution and temporal gap identification
- **Bias Detection**: Identification of source bias and recommendations
- **Gap Analysis**: Research gap identification and topic coverage assessment

### Strategy Optimization
- **Query Enhancement**: Synonym expansion and term optimization
- **Feedback Loops**: Performance-based strategy refinement
- **Source-Specific Terms**: Database-appropriate terminology
- **Complexity Management**: Query complexity optimization

### Result Aggregation
- **Deduplication**: DOI, title, and ID-based duplicate removal
- **Multi-Factor Ranking**: Citation count, recency, source weighting
- **Performance Analytics**: Aggregation statistics and metrics
- **Quality Scoring**: Combined relevance scoring algorithms

## Error Handling

The system implements comprehensive error handling:
- **Rate Limit Protection**: Configurable rate limiters per API
- **Exponential Backoff**: Automatic retry with increasing delays
- **Graceful Degradation**: Continues search if individual APIs fail
- **Fallback Mechanisms**: Returns partial results when possible
- **Health Monitoring**: Built-in API health checking
- **Vector Search Fallbacks**: Mock embeddings when dependencies unavailable