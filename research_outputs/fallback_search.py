#!/usr/bin/env python3
"""
Fallback literature search implementation for Atrial Fibrillation research
Uses available web APIs when Bach utilities are not accessible
"""

import asyncio
import json
import aiohttp
import os
from datetime import datetime
from pathlib import Path
import re


class FallbackLiteratureSearch:
    def __init__(self):
        self.base_urls = {
            'semantic_scholar': 'https://api.semanticscholar.org/graph/v1',
            'arxiv': 'http://export.arxiv.org/api/query',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
        }
        self.api_key = os.getenv('SEMANTIC_SCHOLAR_API_KEY')

    async def search_semantic_scholar(self, query, max_results=100):
        """Search Semantic Scholar API for literature"""
        print(f"Searching Semantic Scholar for: {query}")

        url = f"{self.base_urls['semantic_scholar']}/paper/search"
        params = {
            'query': query,
            'limit': min(max_results, 100),
            'fields': 'title,abstract,authors,year,citationCount,venue,journal,externalIds,url',
            'year': '2019-2024'
        }

        if self.api_key:
            params['apiKey'] = self.api_key

        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        papers = []

                        for paper in data.get('data', []):
                            processed_paper = {
                                'id': paper.get('paperId'),
                                'title': paper.get('title'),
                                'authors': [author.get('name', '') for author in paper.get('authors', [])],
                                'year': paper.get('year'),
                                'abstract': paper.get('abstract'),
                                'venue': paper.get('venue'),
                                'journal': paper.get('journal', {}).get('name') if paper.get('journal') else None,
                                'citationCount': paper.get('citationCount', 0),
                                'url': paper.get('url'),
                                'externalIds': paper.get('externalIds', {}),
                                'database_source': 'semantic_scholar',
                                'relevance_score': self._calculate_relevance_score(paper, query)
                            }
                            papers.append(processed_paper)

                        print(f"Found {len(papers)} papers from Semantic Scholar")
                        return papers
                    else:
                        print(f"Semantic Scholar API error: {response.status}")
                        return []

        except Exception as e:
            print(f"Error searching Semantic Scholar: {e}")
            return []

    async def search_arxiv(self, query, max_results=100):
        """Search arXiv for relevant papers"""
        print(f"Searching arXiv for: {query}")

        # Build arXiv query with category filters
        arxiv_query = f'all:"{query}" AND (cat:q-bio.QM OR cat:cs.LG OR cat:stat.ML)'

        params = {
            'search_query': arxiv_query,
            'start': 0,
            'max_results': min(max_results, 100),
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_urls['arxiv'], params=params) as response:
                    if response.status == 200:
                        import xml.etree.ElementTree as ET
                        xml_content = await response.text()
                        root = ET.fromstring(xml_content)

                        papers = []
                        namespace = {'atom': 'http://www.w3.org/2005/Atom',
                                   'arxiv': 'http://arxiv.org/schemas/atom'}

                        for entry in root.findall('atom:entry', namespace):
                            title = entry.find('atom:title', namespace).text.strip()
                            summary = entry.find('atom:summary', namespace).text.strip()

                            # Extract publication date
                            published = entry.find('atom:published', namespace)
                            year = int(published.text.split('-')[0]) if published else None

                            # Extract authors
                            authors = []
                            for author in entry.findall('atom:author', namespace):
                                name = author.find('atom:name', namespace).text
                                authors.append(name)

                            # Extract arXiv ID and URL
                            arxiv_id = entry.find('atom:id', namespace).text.split('/')[-1]
                            url = entry.find('atom:id', namespace).text

                            paper = {
                                'id': arxiv_id,
                                'title': title,
                                'authors': authors,
                                'year': year,
                                'abstract': summary,
                                'venue': 'arXiv',
                                'journal': None,
                                'citationCount': 0,  # arXiv doesn't provide citation count
                                'url': url,
                                'externalIds': {'arxiv': arxiv_id},
                                'database_source': 'arxiv',
                                'relevance_score': self._calculate_relevance_score({'title': title, 'abstract': summary}, query)
                            }

                            # Filter by publication year
                            if year and 2019 <= year <= 2024:
                                papers.append(paper)

                        print(f"Found {len(papers)} papers from arXiv")
                        return papers
                    else:
                        print(f"arXiv API error: {response.status}")
                        return []

        except Exception as e:
            print(f"Error searching arXiv: {e}")
            return []

    def _calculate_relevance_score(self, paper, query):
        """Calculate basic relevance score based on title and abstract matching"""
        title = (paper.get('title') or '').lower()
        abstract = (paper.get('abstract') or '').lower()
        query_lower = query.lower()

        # Extract key terms from query
        key_terms = ['atrial fibrillation', 'af', 'cardiac', 'arrhythmia', 'heart', 'cardiology']

        score = 0

        # Title matching (higher weight)
        for term in key_terms:
            if term in title:
                score += 20

        # Abstract matching
        for term in key_terms:
            if term in abstract:
                score += 10

        # Recent publication bonus
        year = paper.get('year')
        if year and year >= 2022:
            score += 5

        # Citation count bonus
        citations = paper.get('citationCount', 0)
        if citations > 50:
            score += 10
        elif citations > 10:
            score += 5

        return min(score, 100)  # Cap at 100

    async def execute_comprehensive_search(self, query, max_results_per_source=100):
        """Execute search across all available sources"""
        print(f"Starting comprehensive search for: {query}")

        all_results = {}

        # Try Semantic Scholar first
        try:
            semantic_results = await self.search_semantic_scholar("atrial fibrillation", max_results_per_source)
            all_results['semantic_scholar'] = semantic_results
        except Exception as e:
            print(f"Error with Semantic Scholar: {e}")
            all_results['semantic_scholar'] = []

        # Try arXiv with cardiac focus
        try:
            arxiv_results = await self.search_arxiv("atrial fibrillation cardiac", max_results_per_source)
            all_results['arxiv'] = arxiv_results
        except Exception as e:
            print(f"Error with arXiv: {e}")
            all_results['arxiv'] = []

        return all_results

    def deduplicate_results(self, all_results):
        """Deduplicate results across sources and apply relevance ranking"""
        print("Deduplicating and ranking results...")

        seen_papers = set()
        deduplicated_papers = []

        for source, papers in all_results.items():
            for paper in papers:
                # Create unique identifier based on title and authors
                title = paper.get('title', '').lower().strip()
                first_author = paper.get('authors', [''])[0].lower() if paper.get('authors') else ''
                year = paper.get('year', 0)

                identifier = f"{title}_{first_author}_{year}"

                if identifier not in seen_papers:
                    seen_papers.add(identifier)
                    deduplicated_papers.append(paper)

        # Sort by relevance score
        deduplicated_papers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        print(f"Deduplicated to {len(deduplicated_papers)} unique papers")
        return deduplicated_papers


async def execute_fallback_search():
    """Execute the fallback search implementation"""
    print("=== Fallback Literature Search Implementation ===")
    print("Executing comprehensive search for Atrial Fibrillation...\n")

    searcher = FallbackLiteratureSearch()
    query = "atrial fibrillation cardiac arrhythmia heart cardiology"

    # Execute search
    all_results = await searcher.execute_comprehensive_search(query)

    # Deduplicate and rank results
    final_papers = searcher.deduplicate_results(all_results)

    # Save results
    output_dir = Path("research_outputs")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save comprehensive results
    comprehensive_file = output_dir / f"search_results_comprehensive_fallback_{timestamp}.json"

    search_metadata = {
        "search_timestamp": datetime.now().isoformat(),
        "search_type": "comprehensive_fallback",
        "query": query,
        "total_results": len(final_papers),
        "sources_searched": list(all_results.keys()),
        "papers_by_source": {source: len(papers) for source, papers in all_results.items()}
    }

    output_data = {
        "metadata": search_metadata,
        "results": final_papers
    }

    with open(comprehensive_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n=== SEARCH RESULTS ===")
    print(f"Total unique papers found: {len(final_papers)}")
    print(f"Sources searched: {', '.join(all_results.keys())}")

    # Show top papers
    print(f"\n=== TOP 10 PAPERS BY RELEVANCE ===")
    for i, paper in enumerate(final_papers[:10], 1):
        title = paper.get('title', 'No title')
        authors = paper.get('authors', [])[:3]  # First 3 authors
        year = paper.get('year', 'N/A')
        citations = paper.get('citationCount', 0)
        source = paper.get('database_source', 'unknown')
        score = paper.get('relevance_score', 0)

        authors_str = ', '.join(authors)
        if len(paper.get('authors', [])) > 3:
            authors_str += ' et al.'

        print(f"\n{i}. {title}")
        print(f"   Authors: {authors_str}")
        print(f"   Year: {year} | Citations: {citations} | Source: {source} | Score: {score}")

    # Save summary
    summary_file = output_dir / f"search_summary_fallback_{timestamp}.json"
    summary_data = {
        "search_summary": {
            "timestamp": datetime.now().isoformat(),
            "research_topic": "Atrial fibrillation in cardiology",
            "total_papers_found": len(final_papers),
            "search_methods_used": ["fallback_semantic_scholar", "fallback_arxiv"],
            "search_success": True
        },
        "source_breakdown": {
            source: len(papers) for source, papers in all_results.items()
        },
        "top_papers": [
            {
                "title": paper.get('title'),
                "authors": paper.get('authors', [])[:3],
                "year": paper.get('year'),
                "citations": paper.get('citationCount', 0),
                "relevance_score": paper.get('relevance_score', 0)
            }
            for paper in final_papers[:10]
        ]
    }

    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {comprehensive_file}")
    print(f"Summary saved to: {summary_file}")

    return final_papers


if __name__ == "__main__":
    results = asyncio.run(execute_fallback_search())