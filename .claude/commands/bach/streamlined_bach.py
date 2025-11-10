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
        """Save results to a single clean file."""
        safe_topic = self.research_topic.replace(" ", "_").replace("/", "_")[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"research_outputs/{safe_topic}_bach_results_{timestamp}.json"

        os.makedirs("research_outputs", exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        self.results["file_path"] = output_file

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

        print(f"\n📁 Complete results saved to: {self.results.get('file_path', 'Unknown')}")
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