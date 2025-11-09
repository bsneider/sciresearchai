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
```

## Architecture

The SearchAgent follows TDD principles with comprehensive test coverage for:

- Core functionality (initialization, query optimization)
- Scoring and ranking algorithms
- Duplicate detection and removal
- Rate limiting and API coordination
- Error handling and fallback mechanisms
- Integration with external APIs

## Dependencies

- `requests`: HTTP client for API calls
- `tenacity`: Retry logic with exponential backoff
- `asyncio`: Async/await for concurrent operations

## Configuration

API keys should be provided during initialization:

```python
api_keys = {
    "semantic_scholar": "semantic_scholar_api_key",  # Required for Semantic Scholar
    "arxiv": None,                                    # Not required (no key needed)
    "pubmed": "email@example.com"                     # Required for higher rate limits
}
```