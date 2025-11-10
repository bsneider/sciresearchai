#!/usr/bin/env python3
"""
Streamlined Hypothesis Generator for Bach Research
Focuses on generating quality hypotheses without excessive documentation overhead.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class StreamlinedHypothesisGenerator:
    """Simplified hypothesis generator focused on quality, not quantity of outputs."""

    def __init__(self, research_topic: str, papers: List[Dict]):
        self.research_topic = research_topic
        self.papers = papers
        self.hypotheses = []

    def identify_research_gaps(self) -> List[str]:
        """Identify key research gaps from paper analysis."""
        gaps = []

        # Analyze paper content for gaps
        recent_papers = [p for p in self.papers if p.get("year", 0) >= 2022]
        older_papers = [p for p in self.papers if p.get("year", 0) < 2022]

        # Check for longitudinal gaps
        if len(self.papers) > 0:
            year_range = max(p.get("year", 2020) for p in self.papers) - min(p.get("year", 2020) for p in self.papers)
            if year_range < 5:
                gaps.append("Limited long-term outcome data")

        # Check for implementation gaps
        if any("review" in p.get("title", "").lower() or "guideline" in p.get("title", "").lower() for p in self.papers):
            gaps.append("Gap between guidelines and real-world implementation")

        # Check for population gaps
        if len(self.papers) > 0:
            has_diverse_populations = any(
                "diverse" in p.get("title", "").lower() or
                "population" in p.get("title", "").lower() or
                "underrepresented" in p.get("title", "").lower()
                for p in self.papers
            )
            if not has_diverse_populations:
                gaps.append("Limited research in diverse populations")

        # Check for technology gaps
        tech_keywords = ["ai", "machine learning", "digital", "technology", "algorithm"]
        has_tech = any(
            any(keyword in (p.get("title", "") or "").lower() or keyword in (p.get("abstract", "") or "").lower()
                for keyword in tech_keywords)
            for p in self.papers
        )
        if not has_tech:
            gaps.append("Limited technology integration research")

        # Add general gaps if none found
        if not gaps:
            gaps = ["Need for innovative approaches", "Require implementation research"]

        return gaps

    def generate_hypotheses(self) -> List[Dict]:
        """Generate focused, testable hypotheses."""
        gaps = self.identify_research_gaps()

        # Generate hypotheses based on gaps and paper content
        hypothesis_templates = [
            {
                "type": "implementation",
                "template": "Standardized {intervention} implementation will improve {outcome} by {percentage}% in {setting}"
            },
            {
                "type": "technology",
                "template": "{technology}-enabled {process} will achieve {metric} in {population}"
            },
            {
                "type": "comparison",
                "template": "{approach_A} compared to {approach_B} will show {difference} in {outcome}"
            },
            {
                "type": "longitudinal",
                "template": "Long-term {duration} follow-up of {intervention} will demonstrate {outcome}"
            }
        ]

        # Generate 3-5 high-quality hypotheses
        for i, gap in enumerate(gaps[:3]):
            template = hypothesis_templates[i % len(hypothesis_templates)]
            hypothesis = self._fill_template(template, gap, i + 1)
            if hypothesis:
                self.hypotheses.append(hypothesis)

        return self.hypotheses

    def _fill_template(self, template: Dict, gap: str, hypothesis_id: int) -> Optional[Dict]:
        """Fill hypothesis template with relevant content."""
        # Extract key terms from papers
        all_text = " ".join([
            p.get("title", "") + " " + p.get("abstract", "")
            for p in self.papers
        ]).lower()

        # Simple mapping based on topic and gap
        topic_lower = self.research_topic.lower()

        if "implementation" in template["type"]:
            intervention = "evidence-based protocol"
            outcome = "guideline adherence"
            percentage = "30"
            setting = "clinical practice"

        elif "technology" in template["type"]:
            if "digital" in topic_lower or "ai" in topic_lower:
                technology = "AI-powered"
            else:
                technology = "Digital"
            process = "risk stratification"
            metric = "improved prediction accuracy"
            population = "patient populations"

        elif "comparison" in template["type"]:
            approach_A = "standard care"
            approach_B = "enhanced intervention"
            difference = "significant improvement"
            outcome = "clinical outcomes"

        elif "longitudinal" in template["type"]:
            duration = "5-year"
            intervention = "treatment strategy"
            outcome = "sustained benefits"

        else:
            return None

        # Fill template
        try:
            statement = template["template"].format(**locals())
        except KeyError:
            statement = f"New approach addressing {gap} will improve research outcomes"

        return {
            "id": f"H{hypothesis_id:03d}",
            "title": statement[:100] + "..." if len(statement) > 100 else statement,
            "statement": statement,
            "gap_addressed": gap,
            "type": template["type"],
            "evidence_level": self._assess_evidence_level(),
            "feasibility": self._assess_feasibility(),
            "impact_potential": self._assess_impact()
        }

    def _assess_evidence_level(self) -> str:
        """Assess evidence level based on available papers."""
        if len(self.papers) >= 10:
            return "Strong"
        elif len(self.papers) >= 5:
            return "Moderate"
        else:
            return "Limited"

    def _assess_feasibility(self) -> str:
        """Assess feasibility based on research complexity."""
        if "implementation" in self.research_topic.lower():
            return "High"
        elif "technology" in self.research_topic.lower() or "ai" in self.research_topic.lower():
            return "Medium"
        else:
            return "High"

    def _assess_impact(self) -> str:
        """Assess potential impact."""
        recent_papers = [p for p in self.papers if p.get("year", 0) >= 2023]
        if len(recent_papers) >= 3:
            return "High"
        elif len(recent_papers) >= 1:
            return "Medium"
        else:
            return "Variable"

    def score_hypotheses(self) -> None:
        """Apply realistic scoring to hypotheses."""
        for hypothesis in self.hypotheses:
            # Evidence strength (30% weight)
            evidence_scores = {"Strong": 8, "Moderate": 6, "Limited": 4}
            evidence_score = evidence_scores.get(hypothesis["evidence_level"], 5)

            # Feasibility (25% weight)
            feasibility_scores = {"High": 8, "Medium": 6, "Low": 4}
            feasibility_score = feasibility_scores.get(hypothesis["feasibility"], 5)

            # Impact potential (25% weight)
            impact_scores = {"High": 9, "Medium": 7, "Variable": 5}
            impact_score = impact_scores.get(hypothesis["impact_potential"], 6)

            # Innovation (20% weight)
            innovation_score = 6  # Default moderate innovation

            # Calculate weighted score
            weighted_score = (
                evidence_score * 0.30 +
                feasibility_score * 0.25 +
                impact_score * 0.25 +
                innovation_score * 0.20
            )

            hypothesis["weighted_score"] = round(weighted_score, 1)

        # Sort by score
        self.hypotheses.sort(key=lambda x: x["weighted_score"], reverse=True)

    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if not self.hypotheses:
            return ["Unable to generate hypotheses - insufficient data"]

        top_hypotheses = [h for h in self.hypotheses if h["weighted_score"] >= 7.0]
        medium_hypotheses = [h for h in self.hypotheses if 5.0 <= h["weighted_score"] < 7.0]

        if top_hypotheses:
            recommendations.append(f"Prioritize {len(top_hypotheses)} high-scoring hypotheses (≥7.0) for immediate development")

        if medium_hypotheses:
            recommendations.append(f"Consider {len(medium_hypotheses)} medium-scoring hypotheses (5.0-6.9) for future research")

        # Check feasibility
        feasible_count = len([h for h in self.hypotheses if h["feasibility"] == "High"])
        if feasible_count > 0:
            recommendations.append(f"{feasible_count} hypotheses have high feasibility - focus resources here")

        return recommendations

    def save_results(self, output_file: Optional[str] = None) -> str:
        """Save hypothesis results to a single clean file."""
        if output_file is None:
            safe_topic = self.research_topic.replace(" ", "_").replace("/", "_")[:50]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"research_outputs/{safe_topic}_hypotheses_{timestamp}.json"

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        results = {
            "research_topic": self.research_topic,
            "date": datetime.now().isoformat(),
            "papers_analyzed": len(self.papers),
            "research_gaps": self.identify_research_gaps(),
            "hypotheses": self.hypotheses,
            "recommendations": self.generate_recommendations()
        }

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        return output_file

    def print_summary(self) -> None:
        """Print concise hypothesis summary."""
        print(f"\n🧠 HYPOTHESIS GENERATION: {self.research_topic}")
        print("=" * 60)
        print(f"📄 Papers Analyzed: {len(self.papers)}")
        print(f"💡 Hypotheses Generated: {len(self.hypotheses)}")

        gaps = self.identify_research_gaps()
        if gaps:
            print(f"\n🔍 RESEARCH GAPS IDENTIFIED:")
            for gap in gaps:
                print(f"   • {gap}")

        if self.hypotheses:
            print(f"\n🏆 TOP HYPOTHESES (Scored):")
            for i, hyp in enumerate(self.hypotheses[:5], 1):
                title = hyp["title"][:70] + "..." if len(hyp["title"]) > 70 else hyp["title"]
                print(f"   {i}. [{hyp['weighted_score']}/10] {title}")
                print(f"      🎯 Type: {hyp['type']} | 📊 Evidence: {hyp['evidence_level']} | ⚙️ Feasibility: {hyp['feasibility']}")

        recommendations = self.generate_recommendations()
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   • {rec}")

        print(f"\n📁 Results saved to: {self.save_results()}")


def generate_hypotheses_from_papers(topic: str, papers: List[Dict]) -> StreamlinedHypothesisGenerator:
    """Main hypothesis generation function."""
    generator = StreamlinedHypothesisGenerator(topic, papers)

    generator.generate_hypotheses()
    generator.score_hypotheses()

    generator.print_summary()
    return generator