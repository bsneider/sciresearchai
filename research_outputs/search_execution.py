#!/usr/bin/env python3
"""
Comprehensive literature search for Atrial Fibrillation research
Using Bach utilities with MCP-first approach and API fallback
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from bach.utils.search_integration import (
        comprehensive_research_search,
        quick_paper_search,
        unified_search
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Attempting to continue with basic search functionality...")
    # Fallback implementations will be added below


async def execute_atrial_fibrillation_search():
    """Execute comprehensive search for atrial fibrillation literature"""

    # Search configuration
    query = "Atrial fibrillation in cardiology"
    domain = "clinical"  # Clinical medicine focus

    # API keys from environment variables
    api_keys = {
        'semantic_scholar': os.getenv('SEMANTIC_SCHOLAR_API_KEY'),
        'pubmed': os.getenv('PUBMED_EMAIL'),
        'crossref': os.getenv('CROSSREF_API_KEY')
    }

    print(f"Starting comprehensive search for: {query}")
    print(f"Domain: {domain}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Create output directory structure
    output_dir = Path("research_outputs")
    output_dir.mkdir(exist_ok=True)

    search_results = {}

    try:
        # Method 1: Try comprehensive research search first
        print("\n=== Executing Comprehensive Research Search ===")
        results = await comprehensive_research_search(
            query=query,
            domain=domain,
            max_results=300,
            api_keys=api_keys
        )

        if results:
            search_results['comprehensive'] = results
            print(f"Found {len(results)} papers via comprehensive search")

        # Method 2: Quick paper search for additional results
        print("\n=== Executing Quick Paper Search ===")
        quick_results = await quick_paper_search(
            query,
            max_results=100,
            api_keys=api_keys
        )

        if quick_results:
            search_results['quick'] = quick_results
            print(f"Found {len(quick_results)} papers via quick search")

        # Method 3: Unified search with all sources
        print("\n=== Executing Unified Multi-Source Search ===")
        unified_results = await unified_search(
            query=query,
            include_papers=True,
            include_datasets=False,
            paper_sources=["semantic_scholar", "arxiv", "pubmed"],
            prefer_mcp=True,
            fallback_to_api=True,
            max_results=200
        )

        if unified_results:
            search_results['unified'] = unified_results
            print(f"Found {len(unified_results)} papers via unified search")

    except Exception as e:
        print(f"Error during search execution: {e}")
        # Implement fallback search logic here if needed

    # Save all search results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for search_type, results in search_results.items():
        output_file = output_dir / f"search_results_{search_type}_{timestamp}.json"

        # Add search metadata
        search_metadata = {
            "search_timestamp": datetime.now().isoformat(),
            "search_type": search_type,
            "query": query,
            "domain": domain,
            "total_results": len(results) if results else 0,
            "search_config": {
                "max_results": 300 if search_type == "comprehensive" else 100,
                "api_keys_provided": bool(api_keys.get('semantic_scholar') or
                                         api_keys.get('pubmed'))
            }
        }

        output_data = {
            "metadata": search_metadata,
            "results": results or []
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(results) if results else 0} results to {output_file}")

    # Generate summary report
    await generate_search_summary(search_results, output_dir, timestamp)

    return search_results


async def generate_search_summary(search_results, output_dir, timestamp):
    """Generate a comprehensive summary of all search results"""

    total_papers = sum(len(results) for results in search_results.values() if results)
    search_types = list(search_results.keys())

    summary = {
        "search_summary": {
            "timestamp": datetime.now().isoformat(),
            "research_topic": "Atrial fibrillation in cardiology",
            "total_papers_found": total_papers,
            "search_methods_used": search_types,
            "search_success": bool(search_results)
        },
        "results_by_method": {}
    }

    for search_type, results in search_results.items():
        if results:
            # Analyze results for this search method
            years = [paper.get('year', 0) for paper in results if paper.get('year')]
            citation_counts = [paper.get('citationCount', 0) for paper in results if paper.get('citationCount')]

            summary["results_by_method"][search_type] = {
                "paper_count": len(results),
                "year_range": f"{min(years)}-{max(years)}" if years else "N/A",
                "avg_citations": sum(citation_counts) / len(citation_counts) if citation_counts else 0,
                "top_journals": _extract_top_journals(results),
                "sample_titles": [paper.get('title', '')[:100] + "..." if len(paper.get('title', '')) > 100 else paper.get('title', '') for paper in results[:5]]
            }

    # Save summary
    summary_file = output_dir / f"search_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n=== SEARCH SUMMARY ===")
    print(f"Total papers found: {total_papers}")
    print(f"Search methods used: {', '.join(search_types)}")
    print(f"Summary saved to: {summary_file}")

    # Generate human-readable report
    await generate_human_readable_report(summary, output_dir, timestamp)


def _extract_top_journals(results, top_n=5):
    """Extract top journals from search results"""
    journal_counts = {}
    for paper in results:
        journal = paper.get('journal', '') or paper.get('venue', '')
        if journal:
            journal_counts[journal] = journal_counts.get(journal, 0) + 1

    # Sort by count and return top N
    sorted_journals = sorted(journal_counts.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_journals[:top_n])


async def generate_human_readable_report(summary, output_dir, timestamp):
    """Generate a markdown report of search results"""

    report_file = output_dir / f"search_report_{timestamp}.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Atrial Fibrillation Literature Search Report\n\n")
        f.write(f"**Search Date:** {summary['search_summary']['timestamp']}\n")
        f.write(f"**Research Topic:** {summary['search_summary']['research_topic']}\n")
        f.write(f"**Total Papers Found:** {summary['search_summary']['total_papers_found']}\n\n")

        f.write("## Search Methods Used\n\n")
        for method in summary['search_summary']['search_methods_used']:
            f.write(f"- {method}\n")

        f.write("\n## Results by Search Method\n\n")

        for method, data in summary['results_by_method'].items():
            f.write(f"### {method.title()} Search\n\n")
            f.write(f"- **Papers Found:** {data['paper_count']}\n")
            f.write(f"- **Publication Year Range:** {data['year_range']}\n")
            f.write(f"- **Average Citations:** {data['avg_citations']:.1f}\n")

            if data['top_journals']:
                f.write("\n**Top Journals:**\n")
                for journal, count in data['top_journals'].items():
                    f.write(f"- {journal}: {count} papers\n")

            f.write("\n**Sample Titles:**\n")
            for title in data['sample_titles']:
                f.write(f"- {title}\n")

            f.write("\n")

        f.write("## Next Steps\n\n")
        f.write("1. Review and deduplicate results across search methods\n")
        f.write("2. Apply relevance scoring and ranking\n")
        f.write("3. Select top papers for detailed analysis\n")
        f.write("4. Pass selected papers to Paper Reader Subagent\n")

    print(f"Human-readable report saved to: {report_file}")


if __name__ == "__main__":
    print("=== Atrial Fibrillation Literature Search ===")
    print("Starting comprehensive search execution...\n")

    # Run the search
    results = asyncio.run(execute_atrial_fibrillation_search())

    if results:
        print(f"\nSearch completed successfully!")
        total_papers = sum(len(r) for r in results.values() if r)
        print(f"Total papers collected: {total_papers}")
    else:
        print("\nSearch completed but no results were found.")
        print("This might indicate API key issues or network connectivity problems.")