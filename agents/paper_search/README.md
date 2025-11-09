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

- `aiohttp`: Async HTTP client for API calls
- `biopython`: NCBI/PubMed E-utilities integration
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

## Error Handling

The system implements comprehensive error handling:
- **Rate Limit Protection**: Configurable rate limiters per API
- **Exponential Backoff**: Automatic retry with increasing delays
- **Graceful Degradation**: Continues search if individual APIs fail
- **Fallback Mechanisms**: Returns partial results when possible
- **Health Monitoring**: Built-in API health checking