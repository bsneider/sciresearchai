#!/usr/bin/env python3
"""
Streamlined Bach Research Executor
Simplified, focused research execution that produces meaningful results without excessive output files.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp

# Import local PubMed data loader directly (avoid package imports)
try:
    import sys
    import os
    api_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apis')
    sys.path.insert(0, api_path)
    from local_pubmed_data import LocalPubMedDataLoader
except ImportError:
    LocalPubMedDataLoader = None


class StreamlinedResearchExecutor:
    """Simplified research executor focused on results, not process documentation."""

    def __init__(self, research_topic: str):
        self.research_topic = research_topic
        self.results = {
            "topic": research_topic,
            "date": datetime.now().isoformat(),
            "papers": [],
            "analysis": {},
            "recommendations": []
        }

    async def search_papers(self, max_results: int = 10) -> List[Dict]:
        """Search for papers across multiple sources with minimal overhead."""
        papers = []

        # Try local PubMed data first (fastest and most reliable)
        local_papers = await self._search_local_pubmed(max_results)
        papers.extend(local_papers)

        print(f"📊 Found {len(local_papers)} papers from local PubMed data")

        # If we have enough local papers, use those first
        if len(papers) >= max_results:
            self.results["papers"] = papers[:max_results]
            return papers[:max_results]

        # Otherwise supplement with remote sources
        remaining_needed = max_results - len(papers)

        # Try Semantic Scholar
        semantic_papers = await self._search_semantic_scholar(remaining_needed)
        papers.extend(semantic_papers)

        # Try arXiv for computational papers
        if len(papers) < max_results:
            remaining_needed = max_results - len(papers)
            arxiv_papers = await self._search_arxiv(remaining_needed)
            papers.extend(arxiv_papers)

        # Remove duplicates and sort by relevance
        papers = self._deduplicate_and_rank(papers)

        self.results["papers"] = papers[:max_results]
        return papers[:max_results]

    async def _search_local_pubmed(self, limit: int) -> List[Dict]:
        """Search local PubMed data for relevant papers."""
        if not LocalPubMedDataLoader:
            return []

        try:
            loader = LocalPubMedDataLoader()
            if loader.initialize():
                papers = loader.search(self.research_topic, limit)
                # Add quality scores if not present
                for paper in papers:
                    if 'quality_score' not in paper:
                        paper['quality_score'] = 1.0  # Default score for local data
                return papers
        except Exception as e:
            print(f"Local PubMed search failed: {e}")
        return []

    async def _search_semantic_scholar(self, limit: int) -> List[Dict]:
        """Search Semantic Scholar API."""
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": self.research_topic,
                "limit": limit,
                "fields": "title,abstract,authors,year,citationCount,venue,url"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        papers = []
                        for paper in data.get("data", []):
                            papers.append({
                                "id": paper.get("paperId"),
                                "title": paper.get("title"),
                                "authors": [a.get("name", "") for a in paper.get("authors", [])],
                                "year": paper.get("year"),
                                "abstract": paper.get("abstract"),
                                "venue": paper.get("venue"),
                                "citations": paper.get("citationCount", 0),
                                "url": paper.get("url"),
                                "source": "semantic_scholar"
                            })
                        return papers
        except Exception as e:
            print(f"Semantic Scholar search failed: {e}")
        return []

    async def _search_arxiv(self, limit: int) -> List[Dict]:
        """Search arXiv for relevant papers."""
        try:
            # Clean query for arXiv
            query = self.research_topic.replace(" ", "+")
            url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={limit}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        # Simple XML parsing (without external dependencies)
                        papers = []
                        if "<entry>" in xml_content:
                            entries = xml_content.split("<entry>")[1:]  # Skip first part
                            for entry in entries[:limit]:
                                if "</entry>" in entry:
                                    entry_content = entry.split("</entry>")[0]
                                    paper = self._parse_arxiv_entry(entry_content)
                                    if paper:
                                        papers.append(paper)
                        return papers
        except Exception as e:
            print(f"arXiv search failed: {e}")
        return []

    def _parse_arxiv_entry(self, entry: str) -> Optional[Dict]:
        """Parse individual arXiv entry without full XML parsing."""
        try:
            title = self._extract_xml_tag(entry, "title")
            summary = self._extract_xml_tag(entry, "summary")

            if title and summary:
                return {
                    "title": title.strip(),
                    "abstract": summary.strip(),
                    "source": "arxiv",
                    "citations": 0,  # arXiv doesn't provide this
                    "year": self._extract_year_from_entry(entry)
                }
        except Exception:
            pass
        return None

    def _extract_xml_tag(self, content: str, tag: str) -> Optional[str]:
        """Extract content between XML tags."""
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"

        if start_tag in content and end_tag in content:
            start = content.find(start_tag) + len(start_tag)
            end = content.find(end_tag, start)
            return content[start:end]
        return None

    def _extract_year_from_entry(self, entry: str) -> int:
        """Extract year from arXiv entry."""
        try:
            published = self._extract_xml_tag(entry, "published")
            if published:
                return int(published.split("-")[0])
        except Exception:
            pass
        return 2024  # Default

    def _deduplicate_and_rank(self, papers: List[Dict]) -> List[Dict]:
        """Remove duplicates and rank by relevance."""
        # Simple deduplication by title similarity
        seen_titles = set()
        unique_papers = []

        for paper in papers:
            title = paper.get("title", "").lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                # Add relevance score
                paper["relevance"] = self._calculate_relevance(paper)
                unique_papers.append(paper)

        # Sort by relevance
        unique_papers.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        return unique_papers

    def _calculate_relevance(self, paper: Dict) -> float:
        """Calculate simple relevance score."""
        score = 0
        title = ((paper.get("title", "") or "") + " " + (paper.get("abstract", "") or "")).lower()
        topic_words = self.research_topic.lower().split()

        # Title matching (higher weight)
        for word in topic_words:
            if word in title:
                score += 10

        # Citations bonus
        citations = paper.get("citations", 0)
        if citations > 100:
            score += 5
        elif citations > 10:
            score += 3

        # Recent publication bonus
        year = paper.get("year", 2020)
        if year >= 2023:
            score += 2

        return score

    def analyze_results(self) -> Dict:
        """Generate concise analysis of search results."""
        papers = self.results["papers"]

        if not papers:
            return {"status": "No papers found", "recommendations": ["Try broader search terms"]}

        analysis = {
            "total_papers": len(papers),
            "year_range": f"{min(p.get('year', 2020) for p in papers)}-{max(p.get('year', 2024) for p in papers)}",
            "avg_citations": sum(p.get('citations', 0) for p in papers) / len(papers),
            "top_venues": self._get_top_venues(papers),
            "key_themes": self._extract_key_themes(papers)
        }

        self.results["analysis"] = analysis
        return analysis

    def _get_top_venues(self, papers: List[Dict], top_n: int = 5) -> List[str]:
        """Get top publication venues."""
        venue_counts = {}
        for paper in papers:
            venue = paper.get("venue", "Unknown")
            venue_counts[venue] = venue_counts.get(venue, 0) + 1

        sorted_venues = sorted(venue_counts.items(), key=lambda x: x[1], reverse=True)
        return [venue for venue, count in sorted_venues[:top_n]]

    def _extract_key_themes(self, papers: List[Dict]) -> List[str]:
        """Extract key themes from paper titles and abstracts."""
        all_text = " ".join([
            (p.get("title", "") or "") + " " + (p.get("abstract", "") or "")
            for p in papers
        ]).lower()

        # Simple keyword extraction based on topic
        topic_words = self.research_topic.lower().split()
        themes = []

        for word in topic_words:
            if word in all_text and len(word) > 3:
                themes.append(word)

        return list(set(themes))[:5]  # Top 5 themes

    def generate_recommendations(self) -> List[str]:
        """Generate concise recommendations based on results."""
        papers = self.results["papers"]
        recommendations = []

        if len(papers) == 0:
            recommendations.append("No relevant papers found - consider broadening search terms")
            return recommendations

        # Check for recent research
        recent_papers = [p for p in papers if p.get("year", 0) >= 2023]
        if len(recent_papers) >= 3:
            recommendations.append("Strong recent research activity - field is actively developing")
        elif len(recent_papers) == 0:
            recommendations.append("Limited recent research - potential gap in current literature")

        # Check for highly cited work
        high_citation = [p for p in papers if p.get("citations", 0) > 50]
        if high_citation:
            recommendations.append(f"Field includes {len(high_citation)} highly cited papers (>50 citations)")

        # Check diversity of sources
        sources = set(p.get("source", "") for p in papers)
        if len(sources) >= 2:
            recommendations.append("Multi-source search provides comprehensive coverage")

        # General recommendation
        recommendations.append(f"Focus on top {min(5, len(papers))} papers for detailed analysis")

        self.results["recommendations"] = recommendations
        return recommendations

    def save_results(self, output_file: Optional[str] = None) -> str:
        """Save results to a single, clean file."""
        if output_file is None:
            # Clean topic name for filename
            safe_topic = self.research_topic.replace(" ", "_").replace("/", "_")[:50]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"research_outputs/{safe_topic}_results_{timestamp}.json"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        return output_file

    def print_summary(self) -> None:
        """Print a concise summary."""
        papers = self.results["papers"]
        analysis = self.results.get("analysis", {})

        print(f"\n📊 RESEARCH RESULTS: {self.research_topic}")
        print("=" * 60)
        print(f"📄 Papers Found: {len(papers)}")
        if analysis:
            print(f"📅 Year Range: {analysis.get('year_range', 'N/A')}")
            print(f"📈 Avg Citations: {analysis.get('avg_citations', 0):.1f}")

        print(f"\n🏆 TOP 5 PAPERS:")
        for i, paper in enumerate(papers[:5], 1):
            title = paper.get("title", "No title")[:80] + "..." if len(paper.get("title", "")) > 80 else paper.get("title", "No title")
            print(f"   {i}. {title}")
            print(f"      📊 Relevance: {paper.get('relevance', 0):.1f} | 📚 Citations: {paper.get('citations', 0)} | 📅 Year: {paper.get('year', 'N/A')}")

        recommendations = self.results.get("recommendations", [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   • {rec}")

        print(f"\n📁 Results saved to: {self.save_results()}")


async def streamlined_search(topic: str, max_results: int = 10) -> StreamlinedResearchExecutor:
    """Main streamlined search function."""
    executor = StreamlinedResearchExecutor(topic)

    print(f"🔍 Searching for: {topic}")
    papers = await executor.search_papers(max_results)

    if papers:
        executor.analyze_results()
        executor.generate_recommendations()

    executor.print_summary()
    return executor


# Simplified CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python streamlined_research_executor.py 'research topic'")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    asyncio.run(streamlined_search(topic))