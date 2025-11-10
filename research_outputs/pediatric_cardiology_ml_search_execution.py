#!/usr/bin/env python3
"""
Pediatric Cardiology ML - Comprehensive Literature Search Execution
Uses local PubMed data + remote APIs for comprehensive coverage
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add Bach utilities to path
sys.path.append('.claude/commands/bach/utils')
sys.path.append('.claude/commands/bach/utils/apis')

class PediatricCardiologyMLSearch:
    def __init__(self):
        self.search_config = self.load_search_config()
        self.results = {
            "search_metadata": {
                "search_date": datetime.now().isoformat(),
                "research_topic": "pediatric cardiology machine learning",
                "databases_searched": [],
                "total_results": 0,
                "after_deduplication": 0
            },
            "search_strategy": {
                "keywords": ["pediatric", "cardiology", "machine learning"],
                "databases_used": [],
                "inclusion_criteria": [],
                "exclusion_criteria": []
            },
            "results": [],
            "quality_assessment": {}
        }

    def load_search_config(self):
        """Load search configuration from JSON file."""
        try:
            with open("research_outputs/pediatric_cardiology_ml_search_config.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading search config: {e}")
            return self.default_config()

    def default_config(self):
        """Fallback configuration if config file not found."""
        return {
            "query": "pediatric cardiology machine learning",
            "databases": ["local_pubmed", "semantic_scholar", "arxiv"],
            "max_results_per_source": 100,
            "filters": {
                "date_range": {"start": "2019-01-01", "end": "2024-12-31"}
            }
        }

    async def execute_comprehensive_search(self):
        """Execute search across multiple databases."""
        print("🚀 Starting Pediatric Cardiology ML Literature Search")
        print("=" * 60)

        # Phase 1: Local PubMed Search
        print("\n📚 Phase 1: Local PubMed Database Search")
        local_papers = await self.search_local_pubmed()
        self.results["search_metadata"]["databases_searched"].append("local_pubmed")
        self.results["results"].extend(local_papers)

        # Phase 2: Semantic Scholar Search
        print("\n🌐 Phase 2: Semantic Scholar API Search")
        semantic_papers = await self.search_semantic_scholar()
        if semantic_papers:
            self.results["search_metadata"]["databases_searched"].append("semantic_scholar")
            self.results["results"].extend(semantic_papers)

        # Phase 3: arXiv Search
        print("\n📄 Phase 3: arXiv Preprint Search")
        arxiv_papers = await self.search_arxiv()
        if arxiv_papers:
            self.results["search_metadata"]["databases_searched"].append("arxiv")
            self.results["results"].extend(arxiv_papers)

        # Phase 4: Deduplication and Ranking
        print("\n🔍 Phase 4: Deduplication and Quality Ranking")
        deduplicated_results = self.deduplicate_and_rank()

        # Phase 5: Final Curation
        print("\n📊 Phase 5: Final Curation and Analysis")
        final_results = self.curate_final_results(deduplicated_results)

        # Update metadata
        self.results["search_metadata"]["total_results"] = len(self.results["results"])
        self.results["search_metadata"]["after_deduplication"] = len(final_results)
        self.results["results"] = final_results

        return self.results

    async def search_local_pubmed(self):
        """Search local PubMed database."""
        try:
            from local_pubmed_data import LocalPubMedDataLoader

            loader = LocalPubMedDataLoader()
            if not loader.initialize():
                print("❌ Failed to initialize local PubMed loader")
                return []

            # Search with multiple query terms
            queries = [
                "pediatric cardiology machine learning",
                "children heart disease artificial intelligence",
                "congenital heart defect deep learning",
                "pediatric cardiac neural network",
                "children echocardiogram AI"
            ]

            all_papers = []
            for query in queries:
                papers = loader.search(query, limit=50)
                all_papers.extend(papers)

            # Remove duplicates and add relevance scoring
            unique_papers = self.remove_duplicates(all_papers)
            scored_papers = self.score_relevance(unique_papers, "local_pubmed")

            print(f"✅ Found {len(scored_papers)} papers from local PubMed")
            return scored_papers

        except Exception as e:
            print(f"❌ Local PubMed search failed: {e}")
            return []

    async def search_semantic_scholar(self):
        """Search Semantic Scholar API."""
        try:
            import aiohttp

            query = "pediatric cardiology machine learning OR children heart disease AI OR congenital heart defect deep learning"
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": query,
                "limit": 100,
                "fields": "title,abstract,authors,year,citationCount,venue,url,doi"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        papers = []
                        for paper in data.get("data", []):
                            # Filter for pediatric relevance
                            if self.is_pediatric_cardiology_relevant(paper):
                                processed_paper = {
                                    "id": paper.get("paperId"),
                                    "title": paper.get("title"),
                                    "authors": [a.get("name", "") for a in paper.get("authors", [])],
                                    "year": paper.get("year"),
                                    "abstract": paper.get("abstract"),
                                    "venue": paper.get("venue"),
                                    "doi": paper.get("doi"),
                                    "url": paper.get("url"),
                                    "citation_count": paper.get("citationCount", 0),
                                    "database_source": "semantic_scholar",
                                    "relevance_score": 0.0
                                }
                                papers.append(processed_paper)

                        scored_papers = self.score_relevance(papers, "semantic_scholar")
                        print(f"✅ Found {len(scored_papers)} relevant papers from Semantic Scholar")
                        return scored_papers
                    else:
                        print(f"❌ Semantic Scholar API error: {response.status}")
                        return []
        except Exception as e:
            print(f"❌ Semantic Scholar search failed: {e}")
            return []

    async def search_arxiv(self):
        """Search arXiv for relevant preprints."""
        try:
            import aiohttp

            query = "all:\"pediatric cardiology\" AND all:\"machine learning\" OR all:\"children\" AND all:\"cardiac\" AND all:\"neural network\""
            url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=50"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        papers = self.parse_arxiv_response(xml_content)

                        # Filter for relevance
                        relevant_papers = [p for p in papers if self.is_pediatric_cardiology_relevant(p)]
                        scored_papers = self.score_relevance(relevant_papers, "arxiv")

                        print(f"✅ Found {len(scored_papers)} relevant papers from arXiv")
                        return scored_papers
                    else:
                        print(f"❌ arXiv API error: {response.status}")
                        return []
        except Exception as e:
            print(f"❌ arXiv search failed: {e}")
            return []

    def parse_arxiv_response(self, xml_content):
        """Parse arXiv XML response."""
        papers = []
        if "<entry>" in xml_content:
            entries = xml_content.split("<entry>")[1:]  # Skip first part
            for entry in entries:
                if "</entry>" in entry:
                    entry_content = entry.split("</entry>")[0]
                    paper = self.extract_arxiv_paper(entry_content)
                    if paper:
                        papers.append(paper)
        return papers

    def extract_arxiv_paper(self, entry):
        """Extract paper information from arXiv entry."""
        try:
            title = self.extract_xml_tag(entry, "title")
            summary = self.extract_xml_tag(entry, "summary")
            paper_id = self.extract_xml_tag(entry, "id")

            if title and summary:
                return {
                    "id": paper_id.split("/")[-1] if paper_id else "",
                    "title": title.strip(),
                    "abstract": summary.strip(),
                    "authors": self.extract_arxiv_authors(entry),
                    "year": self.extract_year_from_arxiv_entry(entry),
                    "url": paper_id,
                    "database_source": "arxiv",
                    "citation_count": 0,  # arXiv doesn't provide citation count
                    "relevance_score": 0.0
                }
        except Exception:
            pass
        return None

    def extract_xml_tag(self, content, tag):
        """Extract content between XML tags."""
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"

        if start_tag in content and end_tag in content:
            start = content.find(start_tag) + len(start_tag)
            end = content.find(end_tag, start)
            return content[start:end]
        return None

    def extract_arxiv_authors(self, entry):
        """Extract authors from arXiv entry."""
        authors = []
        if "<author>" in entry:
            author_entries = entry.split("<author>")[1:]
            for author_entry in author_entries:
                if "</author>" in author_entry:
                    name = self.extract_xml_tag(author_entry, "name")
                    if name:
                        authors.append(name)
        return authors

    def extract_year_from_arxiv_entry(self, entry):
        """Extract year from arXiv entry."""
        try:
            published = self.extract_xml_tag(entry, "published")
            if published:
                return int(published.split("-")[0])
        except Exception:
            pass
        return 2024  # Default

    def is_pediatric_cardiology_relevant(self, paper):
        """Check if paper is relevant to pediatric cardiology ML."""
        title = (paper.get("title", "") or "").lower()
        abstract = (paper.get("abstract", "") or "").lower()
        text = f"{title} {abstract}"

        # Pediatric keywords
        pediatric_terms = ["pediatric", "paediatric", "children", "child", "infant", "neonatal", "newborn", "adolescent"]
        # Cardiology keywords
        cardiology_terms = ["cardiology", "cardiac", "heart", "congenital heart", "chd", "echocardiogram", "ecg", "electrocardiogram"]
        # ML keywords
        ml_terms = ["machine learning", "artificial intelligence", "ai", "deep learning", "neural network", "algorithm", "predictive model"]

        has_pediatric = any(term in text for term in pediatric_terms)
        has_cardiology = any(term in text for term in cardiology_terms)
        has_ml = any(term in text for term in ml_terms)

        return has_pediatric and has_cardiology and has_ml

    def remove_duplicates(self, papers):
        """Remove duplicate papers based on title similarity."""
        seen_titles = set()
        unique_papers = []

        for paper in papers:
            title = paper.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)

        return unique_papers

    def score_relevance(self, papers, source):
        """Score papers for relevance to pediatric cardiology ML."""
        for paper in papers:
            title = (paper.get("title", "") or "").lower()
            abstract = (paper.get("abstract", "") or "").lower()
            text = f"{title} {abstract}"

            score = 0.0

            # Pediatric relevance (40% weight)
            pediatric_terms = ["pediatric", "children", "child", "infant", "neonatal"]
            pediatric_count = sum(1 for term in pediatric_terms if term in text)
            score += min(pediatric_count * 0.1, 0.4)

            # Cardiology relevance (30% weight)
            cardiology_terms = ["cardiology", "cardiac", "heart", "congenital"]
            cardiology_count = sum(1 for term in cardiology_terms if term in text)
            score += min(cardiology_count * 0.075, 0.3)

            # ML relevance (20% weight)
            ml_terms = ["machine learning", "deep learning", "neural network", "ai", "algorithm"]
            ml_count = sum(1 for term in ml_terms if term in text)
            score += min(ml_count * 0.05, 0.2)

            # Quality indicators (10% weight)
            if source == "semantic_scholar" and paper.get("citation_count", 0) > 5:
                score += 0.05
            if paper.get("year", 2020) >= 2022:
                score += 0.05

            paper["relevance_score"] = min(score, 1.0)

        return sorted(papers, key=lambda x: x["relevance_score"], reverse=True)

    def deduplicate_and_rank(self):
        """Remove duplicates across sources and rank by relevance."""
        # Group by title similarity
        unique_papers = []
        seen_titles = set()

        for paper in self.results["results"]:
            title = paper.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)

        return sorted(unique_papers, key=lambda x: x["relevance_score"], reverse=True)

    def curate_final_results(self, papers):
        """Apply final quality filters and curation."""
        # Filter by minimum relevance score
        min_score = 0.3  # Minimum relevance threshold
        relevant_papers = [p for p in papers if p.get("relevance_score", 0) >= min_score]

        # Limit to top results
        max_results = self.search_config.get("total_max_results", 100)
        final_papers = relevant_papers[:max_results]

        # Add metadata
        for i, paper in enumerate(final_papers):
            paper["rank"] = i + 1

        return final_papers

    def save_results(self):
        """Save search results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save main results
        main_file = f"research_outputs/pediatric_cardiology_ml_search_results_{timestamp}.json"
        with open(main_file, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Save curated paper list
        curated_file = f"research_outputs/pediatric_cardiology_ml_selected_papers_{timestamp}.json"
        selected_papers = {
            "search_metadata": self.results["search_metadata"],
            "total_found": len(self.results["results"]),
            "curated_count": len(self.results["results"]),
            "papers": self.results["results"][:50]  # Top 50 papers
        }
        with open(curated_file, 'w') as f:
            json.dump(selected_papers, f, indent=2, ensure_ascii=False)

        # Save search metrics
        metrics_file = f"research_outputs/pediatric_cardiology_ml_search_metrics_{timestamp}.json"
        metrics = {
            "search_date": self.results["search_metadata"]["search_date"],
            "databases_searched": self.results["search_metadata"]["databases_searched"],
            "raw_results": self.results["search_metadata"]["total_results"],
            "deduplicated_results": self.results["search_metadata"]["after_deduplication"],
            "final_curated": len(self.results["results"]),
            "relevance_distribution": self.calculate_relevance_distribution(),
            "database_contributions": self.calculate_database_contributions()
        }
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        return {
            "main_results": main_file,
            "selected_papers": curated_file,
            "metrics": metrics_file
        }

    def calculate_relevance_distribution(self):
        """Calculate distribution of relevance scores."""
        scores = [p.get("relevance_score", 0) for p in self.results["results"]]
        if not scores:
            return {}

        return {
            "high_relevance": len([s for s in scores if s >= 0.7]),
            "medium_relevance": len([s for s in scores if 0.4 <= s < 0.7]),
            "low_relevance": len([s for s in scores if s < 0.4]),
            "average_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "min_score": min(scores)
        }

    def calculate_database_contributions(self):
        """Calculate contribution of each database."""
        contributions = {}
        for paper in self.results["results"]:
            source = paper.get("database_source", "unknown")
            contributions[source] = contributions.get(source, 0) + 1
        return contributions

async def main():
    """Execute the comprehensive search."""
    searcher = PediatricCardiologyMLSearch()

    # Execute search
    results = await searcher.execute_comprehensive_search()

    # Print summary
    print(f"\n📊 SEARCH SUMMARY")
    print("=" * 60)
    print(f"Databases Searched: {', '.join(results['search_metadata']['databases_searched'])}")
    print(f"Raw Results: {results['search_metadata']['total_results']}")
    print(f"After Deduplication: {results['search_metadata']['after_deduplication']}")
    print(f"Final Curated: {len(results['results'])}")

    # Show top papers
    print(f"\n🏆 TOP 10 PAPERS")
    print("=" * 60)
    for i, paper in enumerate(results["results"][:10], 1):
        title = paper.get("title", "No title")
        score = paper.get("relevance_score", 0)
        source = paper.get("database_source", "unknown")
        year = paper.get("year", "N/A")
        print(f"{i:2d}. [{score:.2f}] {title[:70]}... ({year}, {source})")

    # Save results
    saved_files = searcher.save_results()
    print(f"\n📁 Results saved:")
    for file_type, file_path in saved_files.items():
        print(f"   {file_type}: {file_path}")

    return results

if __name__ == "__main__":
    # Set environment for local PubMed data
    os.environ["LOCAL_PUBMED_DATA_PATH"] = "temp_aiscientist/data/pubmed_data_2000.csv"

    # Execute search
    asyncio.run(main())