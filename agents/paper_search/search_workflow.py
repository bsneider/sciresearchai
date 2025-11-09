"""
Search Workflow Coordination
Implements T-SEARCH-004: Implement Search Workflow Coordination

Provides end-to-end search process orchestration with:
- Search workflow orchestration logic
- Multi-database query coordination
- Result aggregation and ranking system
- Coverage analysis and gap identification
- Search strategy optimization feedback loop
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re



class SearchStrategy:
    """Handles search query optimization and strategy"""

    def __init__(self):
        self.query_synonyms = {
            "ai": ["artificial intelligence", "machine learning", "deep learning", "neural networks"],
            "ml": ["machine learning", "artificial intelligence", "deep learning"],
            "healthcare": ["medical", "clinical", "medicine", "health"],
            "treatment": ["therapy", "intervention", "cure", "medical care"],
            "diagnosis": ["detection", "identification", "recognition", "diagnostic"],
            "cancer": ["oncology", "tumor", "malignancy", "neoplasm"]
        }

        self.database_terms = {
            "semantic_scholar": ["machine learning", "artificial intelligence", "deep learning"],
            "pubmed": ["clinical", "medical", "therapy", "diagnosis", "treatment"],
            "arxiv": ["cs.AI", "cs.LG", "cs.CV", "stat.ML"]  # arXiv categories
        }

    def optimize_query(self, query: str) -> str:
        """Optimize search query for better results"""
        original_terms = query.lower().split()
        optimized_terms = set(original_terms)

        # Add synonyms for key terms
        for term in original_terms:
            if term in self.query_synonyms:
                optimized_terms.update(self.query_synonyms[term])

        # Add field-specific terms for medical/health queries
        medical_indicators = ["health", "medical", "clinical", "patient", "disease"]
        if any(indicator in original_terms for indicator in medical_indicators):
            optimized_terms.update(["medicine", "healthcare", "therapy"])

        # Remove very short terms and common stopwords
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        optimized_terms = [term for term in optimized_terms if len(term) > 2 and term not in stopwords]

        # Build optimized query
        if len(optimized_terms) <= 3:
            # For simple queries, use OR to broaden search
            return " OR ".join(optimized_terms)
        else:
            # For complex queries, use AND for specificity but include some OR combinations
            return " AND ".join(optimized_terms[:5])  # Limit to avoid overly complex queries

    def optimize_for_database(self, query: str, database: str) -> str:
        """Optimize query for specific database"""
        base_optimized = self.optimize_query(query)

        if database in self.database_terms:
            db_specific = " ".join(self.database_terms[database])
            return f"({base_optimized}) AND ({db_specific})"

        return base_optimized

    def get_database_specific_terms(self, database: str) -> List[str]:
        """Get database-specific search terms"""
        return self.database_terms.get(database, [])


class CoverageAnalyzer:
    """Analyzes search coverage and identifies gaps"""

    def __init__(self):
        self.expected_sources = {"semantic_scholar", "arxiv", "pubmed"}

    def analyze_coverage(self, results: List[Dict], query: str) -> Dict[str, Any]:
        """Analyze coverage of search results"""
        sources = set(r.get("source", "unknown") for r in results)

        coverage = {
            "total_papers": len(results),
            "sources_covered": list(sources),
            "source_coverage": len(sources.intersection(self.expected_sources)) / len(self.expected_sources),
            "missing_sources": list(self.expected_sources - sources),
            "query": query,
            "coverage_quality": self._assess_coverage_quality(sources, len(results))
        }

        return coverage

    def analyze_temporal_coverage(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal distribution of results"""
        years = [r.get("year", datetime.now().year) for r in results if r.get("year")]

        if not years:
            return {"error": "No year information available"}

        year_counts = Counter(years)

        temporal = {
            "year_range": {"start": min(years), "end": max(years)},
            "year_distribution": dict(year_counts),
            "median_year": sorted(years)[len(years) // 2],
            "recent_papers": sum(1 for y in years if y >= datetime.now().year - 2),
            "temporal_span": max(years) - min(years) if years else 0
        }

        return temporal

    def identify_research_gaps(self, results: List[Dict], domain: str) -> Dict[str, Any]:
        """Identify potential research gaps"""
        # Extract keywords and topics from results
        all_keywords = []
        for result in results:
            if "keywords" in result:
                all_keywords.extend(result["keywords"])
            elif "title" in result:
                # Extract terms from title
                title_words = re.findall(r'\b\w+\b', result["title"].lower())
                all_keywords.extend([w for w in title_words if len(w) > 3])

        keyword_counts = Counter(all_keywords)

        # Identify underrepresented areas
        common_keywords = set([k for k, v in keyword_counts.most_common(10)])
        domain_terms = set(domain.lower().split())

        gaps = {
            "missing_topics": list(domain_terms - common_keywords)[:5],  # Domain terms not well covered
            "underrepresented_areas": [k for k, v in keyword_counts.items() if v == 1][:10],  # Topics with only 1 paper
            "temporal_gaps": self._identify_temporal_gaps(results),
            "source_gaps": self._identify_source_gaps(results),
            "research_density": len(results) / len(common_keywords) if common_keywords else 0
        }

        return gaps

    def detect_source_bias(self, results: List[Dict]) -> Dict[str, Any]:
        """Detect potential bias in source distribution"""
        source_counts = Counter(r.get("source", "unknown") for r in results)
        total_papers = len(results)

        if total_papers == 0:
            return {"error": "No results to analyze"}

        # Calculate bias metrics
        max_count = max(source_counts.values())
        dominant_source = max(source_counts, key=source_counts.get)
        bias_score = max_count / total_papers

        bias_analysis = {
            "is_biased": bias_score > 0.7,  # More than 70% from one source is considered biased
            "dominant_source": dominant_source,
            "bias_score": bias_score,
            "source_distribution": dict(source_counts),
            "entropy": self._calculate_entropy(source_counts),  # Higher entropy = more diversity
            "recommendations": self._get_bias_recommendations(source_counts)
        }

        return bias_analysis

    def generate_recommendations(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate recommendations for improving search coverage"""
        coverage = self.analyze_coverage(results, "")
        bias = self.detect_source_bias(results)

        recommendations = {
            "additional_sources": coverage["missing_sources"],
            "query_refinements": self._suggest_query_refinements(results),
            "temporal_expansions": self._suggest_temporal_expansions(results),
            "bias_mitigation": bias.get("recommendations", []),
            "sample_size": len(results),
            "coverage_score": coverage["coverage_quality"]
        }

        return recommendations

    def _assess_coverage_quality(self, sources: Set[str], result_count: int) -> float:
        """Assess overall coverage quality (0-1 scale)"""
        source_score = len(sources.intersection(self.expected_sources)) / len(self.expected_sources)
        quantity_score = min(result_count / 50, 1.0)  # Normalize to 0-1, 50 papers is considered good
        diversity_score = len(sources) / max(len(self.expected_sources), 1)

        return (source_score * 0.4 + quantity_score * 0.3 + diversity_score * 0.3)

    def _identify_temporal_gaps(self, results: List[Dict]) -> List[str]:
        """Identify gaps in temporal coverage"""
        years = sorted(set(r.get("year", datetime.now().year) for r in results if r.get("year")))

        if len(years) < 2:
            return ["Insufficient temporal data"]

        gaps = []
        for i in range(1, len(years)):
            if years[i] - years[i-1] > 3:  # Gap of more than 3 years
                gaps.append(f"Gap between {years[i-1]} and {years[i]}")

        # Check for very recent papers
        current_year = datetime.now().year
        if not any(year >= current_year - 1 for year in years):
            gaps.append("No very recent papers (current year)")

        return gaps

    def _identify_source_gaps(self, results: List[Dict]) -> List[str]:
        """Identify gaps in source coverage"""
        sources = set(r.get("source", "unknown") for r in results)
        return list(self.expected_sources - sources)

    def _calculate_entropy(self, counts: Counter) -> float:
        """Calculate Shannon entropy for source diversity"""
        total = sum(counts.values())
        if total == 0:
            return 0

        entropy = 0
        for count in counts.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * (probability.bit_length() if hasattr(probability, 'bit_length') else 0)

        return entropy

    def _get_bias_recommendations(self, source_counts: Counter) -> List[str]:
        """Get recommendations to reduce source bias"""
        recommendations = []
        total = sum(source_counts.values())

        for source, count in source_counts.items():
            percentage = (count / total) * 100
            if percentage > 70:
                recommendations.append(f"Reduce reliance on {source} (currently {percentage:.1f}%)")
            elif percentage < 10:
                recommendations.append(f"Increase coverage from {source} (currently {percentage:.1f}%)")

        return recommendations

    def _suggest_query_refinements(self, results: List[Dict]) -> List[str]:
        """Suggest query refinements based on results"""
        if len(results) < 5:
            return ["Use broader search terms", "Remove specific constraints"]
        elif len(results) > 100:
            return ["Add more specific terms", "Use AND operators", "Add temporal constraints"]
        else:
            return ["Consider related terminology", "Try different field combinations"]

    def _suggest_temporal_expansions(self, results: List[Dict]) -> List[str]:
        """Suggest temporal search expansions"""
        years = [r.get("year") for r in results if r.get("year")]

        if not years:
            return ["Add year constraints to focus results"]

        min_year, max_year = min(years), max(years)
        current_year = datetime.now().year

        suggestions = []

        if max_year < current_year - 2:
            suggestions.append("Search for more recent papers")

        if min_year > current_year - 10:
            suggestions.append("Consider expanding to include older foundational work")

        if max_year - min_year < 3:
            suggestions.append("Expand temporal range for broader coverage")

        return suggestions


class ResultAggregator:
    """Aggregates and ranks results from multiple sources"""

    def __init__(self):
        self.source_weights = {
            "semantic_scholar": 1.2,  # Higher weight due to citation data
            "pubmed": 1.1,           # Medical authority
            "arxiv": 1.0             # General academic
        }

    def deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate papers based on DOI, title, and ID"""
        seen_dois = set()
        seen_titles = set()
        seen_ids = set()
        unique_results = []

        for result in results:
            doi = result.get("doi")
            if doi:
                doi = doi.lower()
            title = result.get("title", "")
            if title:
                title = title.lower().strip()
            result_id = result.get("id", "")

            # Check DOI first (most reliable)
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)

            # Check title similarity
            if title and title in seen_titles:
                continue
            if title:
                seen_titles.add(title)

            # Check ID
            if result_id and result_id in seen_ids:
                continue
            if result_id:
                seen_ids.add(result_id)

            unique_results.append(result)

        return unique_results

    def rank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Rank results using multiple scoring factors"""
        scored_results = []

        for result in results:
            score = self._calculate_combined_score(result, query)
            result["combined_score"] = score
            scored_results.append(result)

        # Sort by combined score (descending)
        scored_results.sort(key=lambda x: x["combined_score"], reverse=True)
        return scored_results

    def apply_source_weights(self, results: List[Dict]) -> List[Dict]:
        """Apply source-specific weights to results"""
        for result in results:
            source = result.get("source", "unknown")
            base_score = result.get("base_score", 1.0)
            weight = self.source_weights.get(source, 1.0)
            result["weighted_score"] = base_score * weight

        return results

    def calculate_aggregation_stats(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate aggregation statistics"""
        source_counts = Counter(r.get("source", "unknown") for r in results)
        years = [r.get("year") for r in results if r.get("year")]
        citations = [r.get("citationCount", 0) for r in results if r.get("citationCount")]

        stats = {
            "total_results": len(results),
            "source_count": len(source_counts),
            "source_distribution": dict(source_counts),
            "year_range": {"min": min(years), "max": max(years)} if years else None,
            "average_citations": sum(citations) / len(citations) if citations else 0,
            "has_citation_data": len(citations) > 0,
            "unique_sources": len(source_counts)
        }

        return stats

    def _calculate_combined_score(self, result: Dict, query: str) -> float:
        """Calculate combined relevance score for a result"""
        score = 0.0

        # Citation count bonus
        citations = result.get("citationCount", 0)
        if citations > 0:
            # Logarithmic scaling to avoid dominance
            score += min(citations / 100, 1.0) * 0.3

        # Recency bonus
        year = result.get("year")
        if year:
            current_year = datetime.now().year
            recency_factor = max(0, (current_year - year) / 10)  # Decay over 10 years
            score += (1 - recency_factor) * 0.2

        # Source weight
        source = result.get("source", "unknown")
        score += self.source_weights.get(source, 1.0) * 0.2

        # Title match bonus
        title = result.get("title", "").lower()
        query_terms = query.lower().split()
        title_matches = sum(1 for term in query_terms if term in title)
        if title_matches > 0:
            score += (title_matches / len(query_terms)) * 0.3

        return score


class WorkflowProgressTracker:
    """Tracks progress and performance of search workflows"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset tracker for new workflow"""
        self.steps = []
        self.current_step = 0
        self.completed_steps = []
        self.active_steps = set()
        self.errors = []
        self.step_start_times = {}
        self.step_results = {}
        self.total_results = 0

    def initialize_workflow(self, steps: List[str]):
        """Initialize workflow with step sequence"""
        self.steps = steps
        self.total_steps = len(steps)

    def start_step(self, step_name: str):
        """Mark a step as started"""
        self.active_steps.add(step_name)
        self.step_start_times[step_name] = time.time()
        if step_name in self.steps:
            self.current_step = self.steps.index(step_name) + 1

    def complete_step(self, step_name: str, result_count: int = 0):
        """Mark a step as completed"""
        if step_name in self.active_steps:
            self.active_steps.remove(step_name)

        self.completed_steps.append(step_name)
        self.step_results[step_name] = result_count
        self.total_results += result_count

    def log_error(self, step_name: str, error_message: str):
        """Log an error that occurred during a step"""
        self.errors.append({
            "step": step_name,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        })

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get workflow performance metrics"""
        total_time = 0
        step_times = {}

        for step in self.completed_steps:
            if step in self.step_start_times:
                # Estimate completion time (start time + average step duration)
                step_time = time.time() - self.step_start_times[step]
                step_times[step] = step_time
                total_time += step_time

        return {
            "total_time": total_time,
            "step_times": step_times,
            "steps_completed": len(self.completed_steps),
            "steps_total": self.total_steps,
            "errors_encountered": len(self.errors),
            "total_results_processed": self.total_results,
            "average_step_time": total_time / len(self.completed_steps) if self.completed_steps else 0
        }

    def get_completion_status(self) -> Dict[str, Any]:
        """Get current workflow completion status"""
        progress = len(self.completed_steps) / self.total_steps if self.total_steps > 0 else 0

        return {
            "progress_percentage": progress,
            "is_complete": len(self.completed_steps) == self.total_steps,
            "current_step": self.current_step,
            "completed_steps": len(self.completed_steps),
            "total_steps": self.total_steps,
            "active_steps": list(self.active_steps),
            "error_count": len(self.errors)
        }


class SearchWorkflowOrchestrator:
    """Main orchestrator for search workflows"""

    def __init__(self, search_agent):
        self.search_agent = search_agent
        self.strategy_optimizer = SearchStrategy()
        self.coverage_analyzer = CoverageAnalyzer()
        self.result_aggregator = ResultAggregator()
        self.progress_tracker = WorkflowProgressTracker()

    async def execute_search_workflow(self, query: str, max_results: int = 100) -> List[Dict]:
        """Execute basic search workflow"""
        self.progress_tracker.reset()
        self.progress_tracker.initialize_workflow([
            "api_search", "deduplication", "ranking", "final_results"
        ])

        try:
            # Step 1: API Search
            self.progress_tracker.start_step("api_search")
            results = await self.search_agent.search_all_databases(query)
            self.progress_tracker.complete_step("api_search", len(results))

            # Step 2: Deduplication
            self.progress_tracker.start_step("deduplication")
            unique_results = self.result_aggregator.deduplicate_results(results)
            self.progress_tracker.complete_step("deduplication", len(unique_results))

            # Step 3: Ranking
            self.progress_tracker.start_step("ranking")
            ranked_results = await self.search_agent.score_relevance(unique_results, query)
            # Apply additional aggregation ranking
            ranked_results = self.result_aggregator.rank_results(ranked_results, query)
            self.progress_tracker.complete_step("ranking", len(ranked_results))

            # Step 4: Final Results
            self.progress_tracker.start_step("final_results")
            final_results = ranked_results[:max_results]
            self.progress_tracker.complete_step("final_results", len(final_results))

            return final_results

        except Exception as e:
            self.progress_tracker.log_error("workflow_execution", str(e))
            logging.error(f"Search workflow error: {e}")
            return []

    async def coordinate_parallel_search(self, query: str) -> List[Dict]:
        """Coordinate parallel searches across all databases"""
        search_tasks = []

        # Optimize query for each database
        ss_query = self.strategy_optimizer.optimize_for_database(query, "semantic_scholar")
        arxiv_query = self.strategy_optimizer.optimize_for_database(query, "arxiv")
        pubmed_query = self.strategy_optimizer.optimize_for_database(query, "pubmed")

        # Queue parallel searches
        if self.search_agent.api_manager.is_available("semantic_scholar"):
            search_tasks.append(self.search_agent.search_semantic_scholar(ss_query))

        # arXiv is always available
        search_tasks.append(self.search_agent.search_arxiv(arxiv_query))

        if self.search_agent.api_manager.is_available("pubmed"):
            search_tasks.append(self.search_agent.search_pubmed(pubmed_query))

        # Execute searches in parallel
        results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Combine and format results
        all_papers = []
        for i, result in enumerate(results):
            if isinstance(result, list):
                for paper in result:
                    paper["source"] = self._get_source_name(i)
                    all_papers.append(paper)
            elif isinstance(result, Exception):
                logging.error(f"Search {i} failed: {result}")

        return all_papers

    async def execute_enhanced_search_workflow(self, query: str, max_results: int = 50) -> List[Dict]:
        """Execute enhanced search workflow with vector search"""
        if not self.search_agent.vector_engine:
            # Fallback to basic workflow
            return await self.execute_search_workflow(query, max_results)

        self.progress_tracker.reset()
        self.progress_tracker.initialize_workflow([
            "vector_search", "api_search", "aggregation", "ranking", "coverage_analysis"
        ])

        try:
            # Step 1: Vector Search
            self.progress_tracker.start_step("vector_search")
            vector_results = await self.search_agent.vector_search(query, max_results // 2, "hybrid")
            self.progress_tracker.complete_step("vector_search", len(vector_results))

            # Step 2: API Search
            self.progress_tracker.start_step("api_search")
            api_results = await self.search_agent.search_all_databases(query)
            self.progress_tracker.complete_step("api_search", len(api_results))

            # Step 3: Add API results to vector store for future searches
            if api_results:
                await self.search_agent.add_papers_to_vector_store(api_results)

            # Step 4: Aggregation
            self.progress_tracker.start_step("aggregation")
            all_results = vector_results + api_results
            unique_results = self.result_aggregator.deduplicate_results(all_results)
            self.progress_tracker.complete_step("aggregation", len(unique_results))

            # Step 5: Ranking
            self.progress_tracker.start_step("ranking")
            ranked_results = self.result_aggregator.rank_results(unique_results, query)
            final_results = ranked_results[:max_results]
            self.progress_tracker.complete_step("ranking", len(final_results))

            # Step 6: Coverage Analysis (non-blocking)
            self.progress_tracker.start_step("coverage_analysis")
            coverage = self.coverage_analyzer.analyze_coverage(final_results, query)
            self.progress_tracker.complete_step("coverage_analysis", 1)

            # Add coverage info to results metadata
            for result in final_results:
                result["coverage_analysis"] = coverage

            return final_results

        except Exception as e:
            self.progress_tracker.log_error("enhanced_workflow", str(e))
            logging.error(f"Enhanced search workflow error: {e}")
            # Fallback to basic workflow
            return await self.execute_search_workflow(query, max_results)

    async def execute_optimized_search_workflow(self, query: str, max_results: int = 100) -> List[Dict]:
        """Execute optimized search with strategy optimization"""
        # Optimize the query
        optimized_query = self.strategy_optimizer.optimize_query(query)

        # Execute with optimized query
        results = await self.execute_search_workflow(optimized_query, max_results)

        return results

    def analyze_search_performance(self, results: List[Dict], query: str) -> Dict[str, Any]:
        """Analyze search performance and provide insights"""
        if not results:
            return {"error": "No results to analyze"}

        analysis = {
            "query": query,
            "result_count": len(results),
            "coverage": self.coverage_analyzer.analyze_coverage(results, query),
            "temporal_coverage": self.coverage_analyzer.analyze_temporal_coverage(results),
            "bias_analysis": self.coverage_analyzer.detect_source_bias(results),
            "aggregation_stats": self.result_aggregator.calculate_aggregation_stats(results),
            "recommendations": self.coverage_analyzer.generate_recommendations(results),
            "performance_metrics": self.progress_tracker.get_performance_metrics()
        }

        return analysis

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "progress": self.progress_tracker.get_completion_status(),
            "performance": self.progress_tracker.get_performance_metrics(),
            "errors": self.progress_tracker.errors
        }

    def _get_source_name(self, index: int) -> str:
        """Get database source name from index"""
        sources = ["semantic_scholar", "arxiv", "pubmed"]
        return sources[index] if index < len(sources) else "unknown"