#!/usr/bin/env python3
"""
Streamlined Bach Research System
One-command research that produces clean, actionable results without excessive file generation.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add our streamlined modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'utils'))

try:
    from streamlined_research_executor import streamlined_search
    from streamlined_hypothesis_generator import generate_hypotheses_from_papers
except ImportError:
    print("❌ Streamlined Bach modules not found")
    sys.exit(1)


class StreamlinedBach:
    """Simplified Bach research system focused on results, not process documentation."""

    def __init__(self, research_topic: str):
        self.research_topic = research_topic
        self.results = {
            "topic": research_topic,
            "date": datetime.now().isoformat(),
            "papers": [],
            "hypotheses": [],
            "summary": {}
        }

    async def execute_research(self, max_papers: int = 10) -> dict:
        """Execute complete research workflow with minimal overhead."""
        print(f"🚀 Streamlined Bach Research: {self.research_topic}")
        print("=" * 60)

        # Step 1: Search for papers
        print("📚 Step 1: Searching for relevant papers...")
        executor = await streamlined_search(self.research_topic, max_papers)
        papers = executor.results["papers"]
        self.results["papers"] = papers

        if not papers:
            print("❌ No papers found. Research terminated.")
            return self.results

        # Step 2: Generate hypotheses
        print(f"\n🧠 Step 2: Generating hypotheses from {len(papers)} papers...")
        hypothesis_generator = generate_hypotheses_from_papers(self.research_topic, papers)
        self.results["hypotheses"] = hypothesis_generator.hypotheses

        # Step 3: Create summary
        self._create_summary()

        # Step 4: Save results
        self._save_results()

        return self.results

    def _create_summary(self) -> None:
        """Create concise research summary."""
        papers = self.results["papers"]
        hypotheses = self.results["hypotheses"]

        # Paper analysis
        recent_papers = [p for p in papers if p.get("year", 0) >= 2023]
        high_citation = [p for p in papers if p.get("citations", 0) > 50]

        # Hypothesis analysis
        high_scoring = [h for h in hypotheses if h.get("weighted_score", 0) >= 7.0]

        summary = {
            "papers_found": len(papers),
            "recent_papers": len(recent_papers),
            "highly_cited": len(high_citation),
            "hypotheses_generated": len(hypotheses),
            "high_scoring_hypotheses": len(high_scoring),
            "top_hypothesis": hypotheses[0] if hypotheses else None,
            "research_maturity": self._assess_maturity(),
            "action_level": self._determine_action_level()
        }

        self.results["summary"] = summary

    def _assess_maturity(self) -> str:
        """Assess research field maturity."""
        papers = self.results["papers"]
        if len(papers) == 0:
            return "Unknown"

        recent_papers = [p for p in papers if p.get("year", 0) >= 2023]
        total_papers = len(papers)

        if len(recent_papers) / total_papers > 0.6:
            return "Emerging (active recent research)"
        elif len(recent_papers) / total_papers > 0.3:
            return "Developing (steady research activity)"
        else:
            return "Established (limited recent activity)"

    def _determine_action_level(self) -> str:
        """Determine recommended action level."""
        hypotheses = self.results["hypotheses"]
        papers = self.results["papers"]

        if len(papers) < 5:
            return "EXPLORATORY - Limited literature, need broader search"
        elif len(hypotheses) == 0:
            return "FOUNDATIONAL - Need basic research and gap analysis"
        else:
            high_scoring = len([h for h in hypotheses if h.get("weighted_score", 0) >= 7.0])
            if high_scoring >= 2:
                return "IMPLEMENTATION - Strong candidates for development"
            else:
                return "DEVELOPMENT - Moderate potential, needs validation"

    def _save_results(self) -> None:
        """Save results to an organized research folder."""
        safe_topic = self.research_topic.replace(" ", "_").replace("/", "_")[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        research_folder = f"research_outputs/{safe_topic}_{timestamp}"

        # Create organized research folder
        os.makedirs(research_folder, exist_ok=True)

        # Save main results
        main_file = f"{research_folder}/bach_results.json"
        with open(main_file, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Save individual components for easy access
        papers_file = f"{research_folder}/papers.json"
        papers_data = {
            "topic": self.research_topic,
            "date": self.results["date"],
            "papers": self.results["papers"],
            "summary": {
                "total_papers": len(self.results["papers"]),
                "year_range": self._get_year_range(),
                "top_papers": self.results["papers"][:5]
            }
        }
        with open(papers_file, 'w') as f:
            json.dump(papers_data, f, indent=2, ensure_ascii=False)

        # Save hypotheses separately
        if self.results.get("hypotheses"):
            hypotheses_file = f"{research_folder}/hypotheses.json"
            hypotheses_data = {
                "topic": self.research_topic,
                "date": self.results["date"],
                "hypotheses": self.results["hypotheses"],
                "summary": {
                    "total_hypotheses": len(self.results["hypotheses"]),
                    "high_scoring": len([h for h in self.results["hypotheses"] if h.get("weighted_score", 0) >= 7.0]),
                    "top_hypothesis": self.results["hypotheses"][0] if self.results["hypotheses"] else None
                }
            }
            with open(hypotheses_file, 'w') as f:
                json.dump(hypotheses_data, f, indent=2, ensure_ascii=False)

        # Create research summary README
        readme_file = f"{research_folder}/README.md"
        readme_content = self._generate_readme()
        with open(readme_file, 'w') as f:
            f.write(readme_content)

        self.results["research_folder"] = research_folder
        self.results["files"] = {
            "main_results": main_file,
            "papers": papers_file,
            "hypotheses": hypotheses_file if self.results.get("hypotheses") else None,
            "readme": readme_file
        }

    def _get_year_range(self) -> str:
        """Get the year range of found papers."""
        papers = self.results["papers"]
        if not papers:
            return "N/A"

        years = [p.get("year") for p in papers if p.get("year")]
        if not years:
            return "N/A"

        return f"{min(years)}-{max(years)}"

    def _generate_readme(self) -> str:
        """Generate README content for the research folder."""
        summary = self.results.get("summary", {})
        papers = self.results.get("papers", [])
        hypotheses = self.results.get("hypotheses", [])

        readme = f"""# Bach Research Results: {self.research_topic}

**Research Date:** {self.results.get("date", "N/A")}
**Status:** {summary.get("action_level", "N/A")}

## 📊 Summary

- **Papers Found:** {len(papers)}
- **Year Range:** {self._get_year_range()}
- **Hypotheses Generated:** {len(hypotheses)}
- **High-Scoring Hypotheses:** {len([h for h in hypotheses if h.get("weighted_score", 0) >= 7.0])}

## 🏆 Top Papers

"""

        for i, paper in enumerate(papers[:5], 1):
            title = paper.get("title", "No title")
            year = paper.get("year", "N/A")
            source = paper.get("source", "N/A")
            readme += f"{i}. **{title}** ({year}) - {source}\n"

        if hypotheses:
            readme += f"""
## 💡 Top Hypothesis

**Score:** {hypotheses[0].get('weighted_score', 0):.1f}/10
**Type:** {hypotheses[0].get('type', 'N/A')}
**Statement:** {hypotheses[0].get('statement', 'N/A')}
"""

        readme += f"""
## 📁 Files in this Folder

- `bach_results.json` - Complete research results with all data
- `papers.json` - Detailed paper information and analysis
- `hypotheses.json` - Generated hypotheses with scoring
- `README.md` - This summary file

## 🚀 Next Steps

{self._get_next_steps()}

---

*Generated by Streamlined Bach Research System*
"""

        return readme

    def _get_next_steps(self) -> str:
        """Get recommended next steps based on research results."""
        action_level = self.results.get("summary", {}).get("action_level", "")

        if "IMPLEMENTATION" in action_level:
            return "• Strong candidates ready for protocol development\n• Seek implementation funding (Phase 1)\n• Focus on high-scoring hypotheses"
        elif "DEVELOPMENT" in action_level:
            return "• Moderate potential - needs validation studies\n• Seek exploratory funding\n• Refine hypotheses with additional research"
        else:
            return "• Early-stage research area\n• Consider systematic review\n• Explore foundational research questions"

    def print_final_summary(self) -> None:
        """Print final research summary."""
        summary = self.results["summary"]
        papers = self.results["papers"]
        hypotheses = self.results["hypotheses"]

        print(f"\n🎯 RESEARCH SUMMARY")
        print("=" * 60)
        print(f"📚 Literature: {summary['papers_found']} papers found")
        print(f"🔬 Field Status: {summary['research_maturity']}")
        print(f"💡 Innovation: {summary['hypotheses_generated']} hypotheses generated")
        print(f"🎪 Action Level: {summary['action_level']}")

        if summary["top_hypothesis"]:
            top_hyp = summary["top_hypothesis"]
            print(f"\n🏆 TOP HYPOTHESIS:")
            print(f"   Score: {top_hyp.get('weighted_score', 'N/A')}/10")
            print(f"   Type: {top_hyp.get('type', 'N/A')}")
            print(f"   Statement: {top_hyp.get('title', 'N/A')}")

        print(f"\n📈 QUICK INSIGHTS:")
        print(f"   📅 Recent Research: {summary['recent_papers']}/{summary['papers_found']} papers from 2023+")
        if summary['highly_cited'] > 0:
            print(f"   🌟 Highly Cited Work: {summary['highly_cited']} papers with 50+ citations")
        print(f"   🎯 High-Scoring Ideas: {summary['high_scoring_hypotheses']} hypotheses with ≥7.0 score")

        # Action recommendations
        print(f"\n🚀 NEXT STEPS:")
        if "IMPLEMENTATION" in summary["action_level"]:
            print("   ✅ Strong candidates - ready for protocol development")
            print("   💰 Seek implementation funding (Phase 1)")
        elif "DEVELOPMENT" in summary["action_level"]:
            print("   🔬 Moderate potential - needs validation studies")
            print("   💰 Seek exploratory funding")
        elif "EXPLORATORY" in summary["action_level"]:
            print("   🔍 Limited literature - broaden search scope")
            print("   💰 Focus on systematic review first")
        else:
            print("   🧪 Foundational research needed")
            print("   💰 Consider basic science funding")

        research_folder = self.results.get('research_folder', 'Unknown')
        print(f"\n📁 Research folder created: {research_folder}")
        print(f"   📄 bach_results.json - Complete results")
        print(f"   📄 papers.json - Paper details")
        print(f"   📄 hypotheses.json - Generated hypotheses")
        print(f"   📄 README.md - Research summary")
        print(f"\n✨ Streamlined Bach research complete!")


async def run_streamlined_bach(research_topic: str, max_papers: int = 10) -> dict:
    """Main streamlined Bach execution."""
    bach = StreamlinedBach(research_topic)
    results = await bach.execute_research(max_papers)
    bach.print_final_summary()
    return results


def main():
    """CLI interface for streamlined Bach."""
    if len(sys.argv) < 2:
        print("Usage: python streamlined_bach.py 'research topic' [max_papers]")
        print("Example: python streamlined_bach.py 'atrial fibrillation' 15")
        sys.exit(1)

    topic = " ".join(sys.argv[1:-1]) if len(sys.argv) > 2 else sys.argv[1]
    max_papers = int(sys.argv[-1]) if len(sys.argv) > 2 and sys.argv[-1].isdigit() else 10

    # Run the research
    asyncio.run(run_streamlined_bach(topic, max_papers))


if __name__ == "__main__":
    main()