#!/usr/bin/env python3
"""
Post-processing and enhancement of search results for Atrial Fibrillation research
Includes deduplication, relevance ranking, and quality assessment
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def load_search_results():
    """Load the most recent search results"""
    output_dir = Path("research_outputs")

    # Find the most recent comprehensive results file
    comprehensive_files = list(output_dir.glob("search_results_comprehensive_*.json"))

    if not comprehensive_files:
        print("No search results found!")
        return None

    # Sort by modification time and get the most recent
    latest_file = max(comprehensive_files, key=lambda f: f.stat().st_mtime)
    print(f"Loading results from: {latest_file}")

    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def enhance_papers_metadata(papers):
    """Enhance paper metadata with additional analysis"""

    enhanced_papers = []

    for paper in papers:
        enhanced_paper = paper.copy()

        # Add paper type classification
        enhanced_paper['paper_type'] = classify_paper_type(paper)

        # Add clinical relevance score
        enhanced_paper['clinical_relevance'] = calculate_clinical_relevance(paper)

        # Add methodology assessment
        enhanced_paper['methodology'] = assess_methodology(paper)

        # Add target audience
        enhanced_paper['target_audience'] = determine_target_audience(paper)

        # Add research gaps addressed
        enhanced_paper['research_gaps'] = identify_research_gaps(paper)

        enhanced_papers.append(enhanced_paper)

    return enhanced_papers


def classify_paper_type(paper):
    """Classify the type of paper based on title and abstract"""

    title = (paper.get('title', '') + ' ' + paper.get('abstract', '')).lower()

    if 'guideline' in title or 'recommendation' in title or 'consensus' in title:
        return 'clinical_guideline'
    elif 'systematic review' in title or 'meta-analysis' in title:
        return 'systematic_review'
    elif 'randomized' in title or 'trial' in title or 'rct' in title:
        return 'clinical_trial'
    elif 'machine learning' in title or 'deep learning' in title or 'ai' in title or 'artificial intelligence' in title:
        return 'machine_learning'
    elif 'review' in title:
        return 'review_article'
    elif 'study' in title or 'analysis' in title:
        return 'observational_study'
    else:
        return 'original_research'


def calculate_clinical_relevance(paper):
    """Calculate clinical relevance score (0-100)"""

    title = (paper.get('title', '')).lower()
    abstract = (paper.get('abstract', '')).lower()

    score = 0

    # Clinical keywords (high weight)
    clinical_keywords = [
        'patient', 'clinical', 'treatment', 'therapy', 'management',
        'outcome', 'prognosis', 'diagnosis', 'prevention', 'guideline',
        'randomized', 'trial', 'study', 'cohort', 'mortality'
    ]

    for keyword in clinical_keywords:
        if keyword in title:
            score += 10
        if keyword in abstract:
            score += 5

    # High-impact clinical topics
    high_impact_topics = [
        'stroke prevention', 'anticoagulation', 'catheter ablation',
        'mortality', 'quality of life', 'guidelines', 'risk stratification'
    ]

    for topic in high_impact_topics:
        if topic in abstract:
            score += 15

    # Recent publications (bonus)
    year = paper.get('year')
    if year and year >= 2023:
        score += 10
    elif year and year >= 2022:
        score += 5

    # Citation count impact
    citations = paper.get('citationCount', 0)
    if citations >= 100:
        score += 20
    elif citations >= 50:
        score += 15
    elif citations >= 20:
        score += 10
    elif citations >= 5:
        score += 5

    # Journal quality (simplified assessment)
    journal = (paper.get('journal') or '').lower()
    high_impact_journals = [
        'new england journal', 'lancet', 'jama', 'nature', 'circulation',
        'european heart', 'journal of american college', 'heart rhythm'
    ]

    for journal_name in high_impact_journals:
        if journal_name in journal:
            score += 15
            break

    return min(score, 100)


def assess_methodology(paper):
    """Assess the methodology strength of the paper"""

    abstract = (paper.get('abstract', '')).lower()

    methodology_score = 0
    methodology_type = []

    # Study design detection
    if 'randomized' in abstract and 'trial' in abstract:
        methodology_score += 40
        methodology_type.append('randomized_controlled_trial')
    elif 'systematic review' in abstract or 'meta-analysis' in abstract:
        methodology_score += 35
        methodology_type.append('systematic_review')
    elif 'prospective' in abstract:
        methodology_score += 25
        methodology_type.append('prospective_study')
    elif 'multicenter' in abstract:
        methodology_score += 20
        methodology_type.append('multicenter_study')
    elif 'cohort' in abstract:
        methodology_score += 15
        methodology_type.append('cohort_study')
    elif 'cross-sectional' in abstract:
        methodology_score += 10
        methodology_type.append('cross_sectional')

    # Sample size assessment
    import re
    numbers = re.findall(r'\d+', abstract)
    for num in numbers:
        if int(num) >= 10000:
            methodology_score += 15
            break
        elif int(num) >= 1000:
            methodology_score += 10
            break
        elif int(num) >= 100:
            methodology_score += 5
            break

    # Statistical methods
    statistical_terms = ['statistically significant', 'p-value', 'confidence interval',
                        'hazard ratio', 'odds ratio', 'multivariate', 'adjusted']
    stat_count = sum(1 for term in statistical_terms if term in abstract)
    methodology_score += min(stat_count * 2, 10)

    return {
        'score': min(methodology_score, 100),
        'type': methodology_type,
        'strength': 'strong' if methodology_score >= 70 else
                   'moderate' if methodology_score >= 40 else 'limited'
    }


def determine_target_audience(paper):
    """Determine the primary target audience for the paper"""

    title = (paper.get('title', '') + ' ' + paper.get('abstract', '')).lower()

    audiences = []

    if 'guideline' in title or 'recommendation' in title:
        audiences.append('clinicians')
        audiences.append('policy_makers')

    if 'machine learning' in title or 'algorithm' in title or 'computational' in title:
        audiences.append('data_scientists')
        audiences.append('researchers')

    if 'treatment' in title or 'therapy' in title or 'management' in title:
        audiences.append('cardiologists')
        audiences.append('electrophysiologists')

    if 'diagnosis' in title or 'detection' in title or 'screening' in title:
        audiences.append('primary_care_physicians')
        audiences.append('cardiologists')

    if 'cost' in title or 'economic' in title or 'healthcare' in title:
        audiences.append('healthcare_administrators')
        audiences.append('policy_makers')

    if not audiences:
        audiences.append('researchers')
        audiences.append('clinicians')

    return audiences


def identify_research_gaps(paper):
    """Identify research gaps addressed by the paper"""

    abstract = paper.get('abstract', '').lower()

    gaps = []

    if 'novel' in abstract or 'first' in abstract or 'new' in abstract:
        gaps.append('innovative_approach')

    if 'limitations' in abstract or 'future' in abstract or 'need' in abstract:
        gaps.append('addresses_limitations')

    if 'understudied' in abstract or 'rare' in abstract or 'less known' in abstract:
        gaps.append('understudied_population')

    if 'comparison' in abstract or 'versus' in abstract or 'compare' in abstract:
        gaps.append('comparative_effectiveness')

    if 'real-world' in abstract or 'practice' in abstract:
        gaps.append('real_world_evidence')

    if 'long-term' in abstract or 'follow-up' in abstract:
        gaps.append('long_term_outcomes')

    return gaps if gaps else ['general_research_contribution']


def create_analysis_report(enhanced_papers):
    """Create comprehensive analysis report"""

    # Statistics
    total_papers = len(enhanced_papers)
    paper_types = defaultdict(int)
    methodology_scores = []
    clinical_relevance_scores = []
    target_audiences = defaultdict(int)
    research_gaps = defaultdict(int)

    for paper in enhanced_papers:
        # Paper type distribution
        paper_types[paper['paper_type']] += 1

        # Methodology and clinical relevance scores
        methodology_scores.append(paper['methodology']['score'])
        clinical_relevance_scores.append(paper['clinical_relevance'])

        # Target audiences
        for audience in paper['target_audience']:
            target_audiences[audience] += 1

        # Research gaps
        for gap in paper['research_gaps']:
            research_gaps[gap] += 1

    # Calculate averages
    avg_methodology_score = sum(methodology_scores) / len(methodology_scores) if methodology_scores else 0
    avg_clinical_relevance = sum(clinical_relevance_scores) / len(clinical_relevance_scores) if clinical_relevance_scores else 0

    # High-quality papers (top 25% by clinical relevance)
    sorted_by_relevance = sorted(enhanced_papers, key=lambda x: x['clinical_relevance'], reverse=True)
    top_papers_count = max(1, int(total_papers * 0.25))
    top_papers = sorted_by_relevance[:top_papers_count]

    report = {
        "analysis_metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_papers_analyzed": total_papers,
            "analysis_type": "comprehensive_post_processing"
        },
        "paper_type_distribution": dict(paper_types),
        "quality_metrics": {
            "average_methodology_score": round(avg_methodology_score, 1),
            "average_clinical_relevance": round(avg_clinical_relevance, 1),
            "high_quality_papers_count": len(top_papers),
            "high_quality_threshold": "top 25% by clinical relevance"
        },
        "target_audience_distribution": dict(target_audiences),
        "research_gaps_addressed": dict(research_gaps),
        "top_papers_by_relevance": [
            {
                "rank": i + 1,
                "title": paper['title'],
                "authors": paper['authors'][:3],
                "year": paper['year'],
                "clinical_relevance": paper['clinical_relevance'],
                "methodology_score": paper['methodology']['score'],
                "paper_type": paper['paper_type'],
                "target_audience": paper['target_audience']
            }
            for i, paper in enumerate(top_papers)
        ],
        "recommendations_for_next_phase": [
            "Prioritize papers with clinical_relevance >= 80 for detailed analysis",
            "Focus on systematic reviews and clinical trials first",
            "Include recent guidelines for current practice context",
            "Consider machine learning papers separately for methodological review",
            "Ensure representation of different target audiences in final selection"
        ]
    }

    return report


def main():
    """Main processing function"""

    print("=== POST-PROCESSING SEARCH RESULTS ===")

    # Load search results
    search_data = load_search_results()
    if not search_data:
        return

    papers = search_data.get('results', [])
    metadata = search_data.get('metadata', {})

    print(f"Loaded {len(papers)} papers for processing")

    # Enhance papers with additional metadata
    enhanced_papers = enhance_papers_metadata(papers)
    print(f"Enhanced metadata for {len(enhanced_papers)} papers")

    # Create analysis report
    analysis_report = create_analysis_report(enhanced_papers)

    # Save enhanced results
    output_dir = Path("research_results")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save enhanced papers
    enhanced_file = output_dir / f"enhanced_papers_{timestamp}.json"
    enhanced_data = {
        "metadata": {
            **metadata,
            "processing_timestamp": datetime.now().isoformat(),
            "processing_type": "comprehensive_enhancement"
        },
        "results": enhanced_papers
    }

    with open(enhanced_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, indent=2, ensure_ascii=False)

    # Save analysis report
    analysis_file = output_dir / f"analysis_report_{timestamp}.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, indent=2, ensure_ascii=False)

    # Create human-readable summary
    summary_file = output_dir / f"post_processing_summary_{timestamp}.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Atrial Fibrillation Search Results - Post-Processing Summary\n\n")
        f.write(f"**Processing Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Total Papers Analyzed:** {analysis_report['analysis_metadata']['total_papers_analyzed']}\n\n")

        f.write("## Paper Type Distribution\n\n")
        for paper_type, count in analysis_report['paper_type_distribution'].items():
            f.write(f"- {paper_type.replace('_', ' ').title()}: {count} papers\n")

        f.write(f"\n## Quality Metrics\n\n")
        f.write(f"- **Average Methodology Score:** {analysis_report['quality_metrics']['average_methodology_score']}/100\n")
        f.write(f"- **Average Clinical Relevance:** {analysis_report['quality_metrics']['average_clinical_relevance']}/100\n")
        f.write(f"- **High-Quality Papers:** {analysis_report['quality_metrics']['high_quality_papers_count']}\n\n")

        f.write("## Top 5 Papers by Clinical Relevance\n\n")
        for paper in analysis_report['top_papers_by_relevance'][:5]:
            f.write(f"**{paper['rank']}.** {paper['title']}\n")
            f.write(f"   - Clinical Relevance: {paper['clinical_relevance']}/100\n")
            f.write(f"   - Methodology Score: {paper['methodology_score']}/100\n")
            f.write(f"   - Type: {paper['paper_type'].replace('_', ' ').title()}\n\n")

        f.write("## Recommendations for Next Phase\n\n")
        for rec in analysis_report['recommendations_for_next_phase']:
            f.write(f"- {rec}\n")

    print(f"\n=== POST-PROCESSING COMPLETE ===")
    print(f"Enhanced papers saved to: {enhanced_file}")
    print(f"Analysis report saved to: {analysis_file}")
    print(f"Summary report saved to: {summary_file}")
    print(f"\nQuality Summary:")
    print(f"- Total papers: {len(enhanced_papers)}")
    print(f"- Average clinical relevance: {analysis_report['quality_metrics']['average_clinical_relevance']:.1f}/100")
    print(f"- High-quality papers (top 25%): {analysis_report['quality_metrics']['high_quality_papers_count']}")


if __name__ == "__main__":
    main()