"""
Paper Quality Assessment Framework
Evaluates research papers across multiple quality criteria and metrics
"""

import re
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from collections import Counter

# Try to import textstat for readability metrics
try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    logging.warning("textstat not available. Readability metrics will be limited.")

# Try to import nltk for linguistic analysis
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available. Linguistic analysis will be limited.")


@dataclass
class QualityCriterion:
    """Quality assessment criterion definition"""
    name: str
    description: str
    weight: float
    assessor_func: Callable[[Dict[str, Any]], float]
    threshold: float = 0.5


class QualityAssessor:
    """
    Comprehensive paper quality assessment system

    Features:
    - Multi-criteria quality assessment
    - Structural completeness evaluation
    - Content quality metrics
    - Academic writing standards
    - Readability and clarity assessment
    """

    def __init__(self):
        """Initialize quality assessor"""
        self.logger = logging.getLogger(__name__)

        # Initialize linguistic tools if available
        self._init_linguistic_tools()

        # Define quality criteria
        self.quality_criteria = self._initialize_quality_criteria()

        # Academic writing indicators
        self.academic_indicators = self._initialize_academic_indicators()

        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 0.85,
            'good': 0.70,
            'acceptable': 0.55,
            'poor': 0.40
        }

    def _init_linguistic_tools(self):
        """Initialize linguistic analysis tools"""
        self.nltk_available = NLTK_AVAILABLE
        self.textstat_available = TEXTSTAT_AVAILABLE

        if self.nltk_available:
            try:
                # Download required NLTK data
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                self.stop_words = set(stopwords.words('english'))
            except Exception as e:
                self.logger.warning(f"Failed to initialize NLTK: {e}")
                self.nltk_available = False

    def _initialize_quality_criteria(self) -> Dict[str, QualityCriterion]:
        """Initialize quality assessment criteria"""
        criteria = {
            'structure_completeness': QualityCriterion(
                name='structure_completeness',
                description='Presence of required paper sections',
                weight=0.25,
                assessor_func=self._assess_structure_completeness,
                threshold=0.7
            ),

            'content_length': QualityCriterion(
                name='content_length',
                description='Appropriate content length for research paper',
                weight=0.15,
                assessor_func=self._assess_content_length,
                threshold=0.6
            ),

            'academic_language': QualityCriterion(
                name='academic_language',
                description='Use of appropriate academic language',
                weight=0.20,
                assessor_func=self._assess_academic_language,
                threshold=0.7
            ),

            'methodology_clarity': QualityCriterion(
                name='methodology_clarity',
                description='Clarity and detail of methodology description',
                weight=0.20,
                assessor_func=self._assess_methodology_clarity,
                threshold=0.6
            ),

            'statistical_rigor': QualityCriterion(
                name='statistical_rigor',
                description='Presence and quality of statistical analysis',
                weight=0.10,
                assessor_func=self._assess_statistical_rigor,
                threshold=0.5
            ),

            'citation_quality': QualityCriterion(
                name='citation_quality',
                description='Quality and quantity of citations',
                weight=0.10,
                assessor_func=self._assess_citation_quality,
                threshold=0.5
            )
        }

        return criteria

    def _initialize_academic_indicators(self) -> Dict[str, List[str]]:
        """Initialize academic writing indicators"""
        return {
            'positive': [
                r'\b(?:methodology|analysis|results?|findings?|conclusion|implications?)\b',
                r'\b(?:significant|statistical|hypothesis|experiment|research|study)\b',
                r'\b(?:previous|prior|subsequent|following|according to)\b',
                r'\b(?:however|therefore|furthermore|nevertheless|consequently)\b',
                r'\b(?:p\s*<\s*[0-9]+\.[0-9]+|p\s*=\s*[0-9]+\.[0-9]+)\b'
            ],
            'negative': [
                r'\b(?:i think|maybe|perhaps|probably|might|could be)\b',
                r'\b(?:awesome|great|terrible|awful|horrible)\b',
                r'\b(?:really|very|quite|rather|pretty)\b',
                r'\b(?:stuff|thing|things|lot of|lots of)\b',
                r'\b(?:gonna|wanna|kinda|sorta)\b'
            ]
        }

    def assess_quality(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess overall paper quality across multiple criteria

        Args:
            paper_data: Dictionary containing paper content and structure

        Returns:
            Dictionary containing:
            - quality_score: Overall quality score (0-1)
            - criteria: Individual criterion scores
            - grade: Quality grade (excellent, good, acceptable, poor)
            - recommendations: Quality improvement suggestions
        """
        try:
            # Assess each criterion
            criterion_scores = {}
            total_weighted_score = 0.0
            total_weight = 0.0

            for criterion_name, criterion in self.quality_criteria.items():
                try:
                    score = criterion.assessor_func(paper_data)
                    score = max(0.0, min(1.0, score))  # Clamp to [0, 1]

                    criterion_scores[criterion_name] = {
                        'score': score,
                        'weight': criterion.weight,
                        'threshold': criterion.threshold,
                        'passed': score >= criterion.threshold,
                        'description': criterion.description
                    }

                    total_weighted_score += score * criterion.weight
                    total_weight += criterion.weight

                except Exception as e:
                    self.logger.warning(f"Failed to assess criterion {criterion_name}: {e}")
                    criterion_scores[criterion_name] = {
                        'score': 0.0,
                        'weight': criterion.weight,
                        'threshold': criterion.threshold,
                        'passed': False,
                        'description': criterion.description,
                        'error': str(e)
                    }

            # Calculate overall quality score
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

            # Determine quality grade
            grade = self._determine_quality_grade(overall_score)

            # Generate recommendations
            recommendations = self._generate_recommendations(criterion_scores, overall_score)

            return {
                'quality_score': overall_score,
                'grade': grade,
                'criteria': criterion_scores,
                'total_weight': total_weight,
                'assessment_metadata': {
                    'assessor_version': '1.0.0',
                    'nltk_available': self.nltk_available,
                    'textstat_available': self.textstat_available
                },
                'recommendations': recommendations
            }

        except Exception as e:
            self.logger.error(f"Quality assessment failed: {str(e)}")
            raise Exception(f"Paper quality assessment failed: {str(e)}")

    def _assess_structure_completeness(self, paper_data: Dict[str, Any]) -> float:
        """Assess structural completeness of the paper"""
        structure = paper_data.get('structure', {})
        sections = structure.get('sections', {})

        # Define required sections
        required_sections = ['abstract', 'introduction', 'methods', 'results']
        optional_sections = ['discussion', 'conclusion']

        # Count present sections
        required_present = sum(1 for section in required_sections if sections.get(section))
        optional_present = sum(1 for section in optional_sections if sections.get(section))

        # Calculate completeness score
        required_score = required_present / len(required_sections)
        optional_score = optional_present / (len(optional_sections) * 2)  # Weight optional sections less

        return min(required_score + optional_score, 1.0)

    def _assess_content_length(self, paper_data: Dict[str, Any]) -> float:
        """Assess appropriate content length"""
        content = paper_data.get('content', '')

        if not content:
            return 0.0

        word_count = len(content.split())

        # Expected word counts for different sections
        if 'structure' in paper_data and 'sections' in paper_data['structure']:
            sections = paper_data['structure']['sections']
            total_expected = 0
            total_actual = 0

            section_requirements = {
                'abstract': (150, 300),      # min, max words
                'introduction': (500, 1500),
                'methods': (800, 2000),
                'results': (600, 1800),
                'discussion': (500, 1500),
                'conclusion': (200, 600)
            }

            for section, (min_words, max_words) in section_requirements.items():
                if section in sections:
                    section_content = sections[section]
                    section_words = len(section_content.split())

                    # Score based on being within acceptable range
                    if min_words <= section_words <= max_words:
                        section_score = 1.0
                    elif section_words < min_words:
                        section_score = section_words / min_words
                    else:
                        section_score = max(0, 1.0 - (section_words - max_words) / max_words)

                    total_actual += section_words * section_score
                    total_expected += min_words

            return min(total_actual / total_expected, 1.0) if total_expected > 0 else 0.0

        else:
            # Fallback: basic word count assessment
            if word_count < 2000:
                return word_count / 2000
            elif word_count > 10000:
                return max(0, 1.0 - (word_count - 10000) / 10000)
            else:
                return 1.0

    def _assess_academic_language(self, paper_data: Dict[str, Any]) -> float:
        """Assess use of appropriate academic language"""
        content = paper_data.get('content', '')

        if not content:
            return 0.0

        content_lower = content.lower()

        # Count academic indicators
        positive_count = sum(
            len(re.findall(pattern, content_lower))
            for pattern in self.academic_indicators['positive']
        )

        negative_count = sum(
            len(re.findall(pattern, content_lower))
            for pattern in self.academic_indicators['negative']
        )

        total_indicators = positive_count + negative_count

        if total_indicators == 0:
            return 0.5  # Neutral score

        # Calculate academic language score
        academic_ratio = positive_count / total_indicators

        # Apply readability bonus if available
        readability_bonus = 0.0
        if self.textstat_available:
            try:
                # Use Flesch-Kincaid readability
                readability = textstat.flesch_kincaid_grade(content)
                if 8 <= readability <= 16:  # Academic reading level
                    readability_bonus = 0.2
            except:
                pass

        return min(academic_ratio + readability_bonus, 1.0)

    def _assess_methodology_clarity(self, paper_data: Dict[str, Any]) -> float:
        """Assess clarity and detail of methodology description"""
        structure = paper_data.get('structure', {})
        sections = structure.get('sections', {})

        methods_content = sections.get('methods', '')

        if not methods_content:
            return 0.0

        methods_lower = methods_content.lower()

        # Look for methodology indicators
        clarity_indicators = [
            r'\b(?:participants?|subjects?|sample)\b',
            r'\b(?:procedure|protocol|method)\b',
            r'\b(?:materials?|equipment|tools?)\b',
            r'\b(?:data\s+collection|measurement)\b',
            r'\b(?:analysis|statistical|test)\b',
            r'\b(?:ethical|consent|approval)\b'
        ]

        indicator_count = sum(
            len(re.findall(pattern, methods_lower))
            for pattern in clarity_indicators
        )

        # Assess content length
        word_count = len(methods_content.split())
        length_score = min(word_count / 500, 1.0)  # Expect at least 500 words

        # Combine indicator and length scores
        clarity_score = min(indicator_count / 5, 1.0)  # Expect at least 5 indicators

        return (clarity_score + length_score) / 2

    def _assess_statistical_rigor(self, paper_data: Dict[str, Any]) -> float:
        """Assess statistical rigor in the paper"""
        content = paper_data.get('content', '')

        if not content:
            return 0.0

        content_lower = content.lower()

        # Look for statistical indicators
        statistical_indicators = [
            r'\bp\s*[<>=]\s*[0-9]+\.[0-9]+\b',      # p-values
            r'\b(?:mean|median|mode|sd|std|variance)\b',
            r'\b(?:correlation|coefficient|r\s*=\s*[0-9])\b',
            r'\b(?:significance|significant|confidence)\b',
            r'\b(?:sample\s*size|n\s*=\s*[0-9]+)\b',
            r'\b(?:anova|t[-]?test|regression|chi[-]?square)\b'
        ]

        indicator_count = sum(
            len(re.findall(pattern, content_lower))
            for pattern in statistical_indicators
        )

        # Score based on statistical indicators found
        if indicator_count >= 10:
            return 1.0
        elif indicator_count >= 5:
            return 0.8
        elif indicator_count >= 2:
            return 0.6
        elif indicator_count >= 1:
            return 0.4
        else:
            return 0.1

    def _assess_citation_quality(self, paper_data: Dict[str, Any]) -> float:
        """Assess citation quality and quantity"""
        content = paper_data.get('content', '')

        if not content:
            return 0.0

        # Look for citation patterns
        citation_patterns = [
            r'\(\s*[A-Z][a-z]+\s+[A-Z][a-z]*\s*,\s*\d{4}\s*\)',  # (Smith, 2020)
            r'\[[0-9]+\]',                                        # [1], [2], etc.
            r'\b(?:according|as\s+reported|based\s+on)\s+[A-Z]',  # According to Smith
            r'\b\d{4}\b',                                         # Year citations
            r'et\s+al\.'                                          # et al. citations
        ]

        citation_count = sum(
            len(re.findall(pattern, content))
            for pattern in citation_patterns
        )

        # Assess based on citation density
        word_count = len(content.split())
        citation_density = citation_count / max(word_count / 1000, 1)  # Citations per 1000 words

        if citation_density >= 15:
            return 1.0
        elif citation_density >= 10:
            return 0.8
        elif citation_density >= 5:
            return 0.6
        elif citation_density >= 2:
            return 0.4
        else:
            return 0.2

    def _determine_quality_grade(self, score: float) -> str:
        """Determine quality grade based on score"""
        for grade, threshold in self.quality_thresholds.items():
            if score >= threshold:
                return grade
        return 'very_poor'

    def _generate_recommendations(
        self,
        criterion_scores: Dict[str, Dict[str, Any]],
        overall_score: float
    ) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []

        # Specific recommendations based on failed criteria
        for criterion_name, criterion_data in criterion_scores.items():
            if not criterion_data.get('passed', True):
                score = criterion_data['score']

                if criterion_name == 'structure_completeness':
                    recommendations.append(
                        "Add missing required sections (abstract, introduction, methods, results)"
                    )
                elif criterion_name == 'content_length':
                    recommendations.append(
                        "Expand content to meet appropriate length for research paper"
                    )
                elif criterion_name == 'academic_language':
                    recommendations.append(
                        "Use more formal academic language and avoid informal expressions"
                    )
                elif criterion_name == 'methodology_clarity':
                    recommendations.append(
                        "Provide more detailed description of methods and procedures"
                    )
                elif criterion_name == 'statistical_rigor':
                    recommendations.append(
                        "Include statistical analysis and report p-values, sample sizes, and effect sizes"
                    )
                elif criterion_name == 'citation_quality':
                    recommendations.append(
                        "Add more citations to support claims and provide context"
                    )

        # General recommendations based on overall score
        if overall_score < 0.4:
            recommendations.append(
                "Consider significant revisions to meet basic academic paper standards"
            )
        elif overall_score < 0.6:
            recommendations.append(
                "Review and strengthen multiple aspects of the paper"
            )
        elif overall_score < 0.8:
            recommendations.append(
                "Make minor improvements to achieve higher quality"
            )

        # Remove duplicates
        recommendations = list(dict.fromkeys(recommendations))

        return recommendations

    def get_quality_criteria(self) -> Dict[str, Any]:
        """
        Get information about quality assessment criteria

        Returns:
            Dictionary with quality criteria information
        """
        return {
            'criteria': {
                name: {
                    'description': criterion.description,
                    'weight': criterion.weight,
                    'threshold': criterion.threshold
                }
                for name, criterion in self.quality_criteria.items()
            },
            'quality_thresholds': self.quality_thresholds,
            'academic_indicators': self.academic_indicators
        }