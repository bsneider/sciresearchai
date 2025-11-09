"""
Key Finding Extraction Algorithms
Identifies and extracts key findings from research paper content
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Try to import nltk for text processing
try:
    import nltk
    from nltk.tokenize import sent_tokenize
    from nltk.corpus import stopwords
    from nltk.chunk import ne_chunk
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available. Advanced extraction will be limited.")


@dataclass
class ExtractedFinding:
    """Represents an extracted key finding"""
    text: str
    confidence: float
    category: str
    evidence: str
    context: str


@dataclass
class FindingPattern:
    """Pattern for identifying specific types of findings"""
    name: str
    patterns: List[str]
    confidence_weight: float
    category: str


class KeyFindingExtractor:
    """
    Advanced key finding extraction from research papers

    Features:
    - Statistical finding identification
    - Quantitative result extraction
    - Comparative statement detection
    - Confidence scoring for findings
    - Duplicate detection and removal
    """

    def __init__(self):
        """Initialize finding extractor"""
        self.logger = logging.getLogger(__name__)

        # Initialize NLP tools if available
        self._init_nlp_tools()

        # Define finding patterns
        self.finding_patterns = self._initialize_finding_patterns()

        # Confidence thresholds
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }

    def _init_nlp_tools(self):
        """Initialize NLP tools for text processing"""
        self.nltk_available = NLTK_AVAILABLE

        if self.nltk_available:
            try:
                # Download required NLTK data
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                nltk.download('maxent_ne_chunker', quiet=True)
                nltk.download('words', quiet=True)
                self.stop_words = set(stopwords.words('english'))
            except Exception as e:
                self.logger.warning(f"Failed to initialize NLTK: {e}")
                self.nltk_available = False

    def _initialize_finding_patterns(self) -> List[FindingPattern]:
        """Initialize patterns for finding identification"""
        patterns = [
            # Statistical findings
            FindingPattern(
                name='statistical_significance',
                patterns=[
                    r'(?:significant|significantly|statistically\s+significant)',
                    r'p\s*[<>=]\s*[0-9]+\.[0-9]+',
                    r'p\s*=\s*[0-9]+\.[0-9]+',
                    r'(?:95%\s+confidence\s+interval|CI)',
                    r'(?:effect\s+size|cohen\'s\s*d\s*=\s*[0-9]',
                    r'(?:correlation|r\s*=\s*[-+]?\d*\.\d+)'
                ],
                confidence_weight=0.9,
                category='statistical'
            ),

            # Quantitative results
            FindingPattern(
                name='quantitative_results',
                patterns=[
                    r'(?:(?:increase|decrease|improve|reduce|grow|shrink)\s+by\s+\d+%?)',
                    r'(?:(?:\d+%|\d+\s*percent)\s+(?:increase|decrease|improvement|reduction))',
                    r'(?:score\s*of\s*\d+\.\d+|\d+\.\d+\s+points)',
                    r'(?:mean|average)\s*(?:of|=)?\s*\d+\.?\d*',
                    r'(?:median|mode)\s*(?:of|=)?\s*\d+\.?\d*',
                    r'(?:(?:n|N)\s*=\s*\d+|(?:sample\s*size|participants?)\s*[:=]\s*\d+)'
                ],
                confidence_weight=0.8,
                category='quantitative'
            ),

            # Comparative findings
            FindingPattern(
                name='comparative_findings',
                patterns=[
                    r'(?:compared\s+(?:to|with)|versus|vs\.?)',
                    r'(?:higher|lower|greater|less|more|fewer)\s+than',
                    r'(?:outperformed|exceeded|surpassed)',
                    r'(?:significant\s+difference|significantly\s+different)',
                    r'(?:superior\s+to|inferior\s+to)',
                    r'(?:better\s+performance|worse\s+performance)'
                ],
                confidence_weight=0.7,
                category='comparative'
            ),

            # Methodological innovations
            FindingPattern(
                name='methodological_findings',
                patterns=[
                    r'(?:novel|new|innovative|original)',
                    r'(?:developed|created|designed|proposed)',
                    r'(?:approach|method|technique|framework|algorithm)',
                    r'(?:first\s+(?:study|research|demonstration))',
                    r'(?:unlike|different\s+from|alternative\s+to)',
                    r'(?:combines|integrates|merges)'
                ],
                confidence_weight=0.6,
                category='methodological'
            ),

            # Causal findings
            FindingPattern(
                name='causal_findings',
                patterns=[
                    r'(?:caused|led\s+to|resulted\s+in)',
                    r'(?:due\s+to|because\s+of|as\s+a\s+result\s+of)',
                    r'(?:associated\s+with|correlated\s+with)',
                    r'(?:predicts|predicts|influences)',
                    r'(?:relationship|association|link)\s+between'
                ],
                confidence_weight=0.7,
                category='causal'
            )
        ]

        return patterns

    def extract_findings(self, content: str) -> Dict[str, Any]:
        """
        Extract key findings from research paper content

        Args:
            content: Text content to analyze

        Returns:
            Dictionary containing:
            - findings: List of extracted findings
            - confidence_scores: List of confidence scores
            - categories: List of finding categories
            - summary: Summary of extraction results
        """
        try:
            if not content or not content.strip():
                return {
                    'findings': [],
                    'confidence_scores': [],
                    'categories': [],
                    'summary': {
                        'total_findings': 0,
                        'high_confidence': 0,
                        'medium_confidence': 0,
                        'low_confidence': 0
                    }
                }

            # Split content into sentences
            sentences = self._split_into_sentences(content)

            # Extract findings from each sentence
            all_findings = []
            for sentence in sentences:
                sentence_findings = self._extract_from_sentence(sentence)
                all_findings.extend(sentence_findings)

            # Remove duplicates and consolidate findings
            consolidated_findings = self._consolidate_findings(all_findings)

            # Sort by confidence
            consolidated_findings.sort(key=lambda x: x.confidence, reverse=True)

            # Extract components for return
            findings_text = [f.text for f in consolidated_findings]
            confidence_scores = [f.confidence for f in consolidated_findings]
            categories = [f.category for f in consolidated_findings]

            # Generate summary
            summary = self._generate_summary(consolidated_findings)

            return {
                'findings': findings_text,
                'confidence_scores': confidence_scores,
                'categories': categories,
                'detailed_findings': [
                    {
                        'text': f.text,
                        'confidence': f.confidence,
                        'category': f.category,
                        'evidence': f.evidence,
                        'context': f.context
                    }
                    for f in consolidated_findings
                ],
                'summary': summary
            }

        except Exception as e:
            self.logger.error(f"Finding extraction failed: {str(e)}")
            raise Exception(f"Key finding extraction failed: {str(e)}")

    def _split_into_sentences(self, content: str) -> List[str]:
        """Split content into sentences"""
        if self.nltk_available:
            try:
                sentences = sent_tokenize(content)
                return [sent.strip() for sent in sentences if sent.strip()]
            except:
                pass

        # Fallback: simple sentence splitting
        sentences = re.split(r'[.!?]+', content)
        return [sent.strip() for sent in sentences if sent.strip()]

    def _extract_from_sentence(self, sentence: str) -> List[ExtractedFinding]:
        """Extract findings from a single sentence"""
        findings = []
        sentence_lower = sentence.lower()

        for pattern in self.finding_patterns:
            for pattern_str in pattern.patterns:
                try:
                    matches = re.finditer(pattern_str, sentence_lower, re.IGNORECASE)

                    for match in matches:
                        # Calculate confidence based on pattern and context
                        base_confidence = pattern.confidence_weight
                        context_confidence = self._calculate_context_confidence(sentence)
                        confidence = min(base_confidence * context_confidence, 1.0)

                        # Create finding object
                        finding = ExtractedFinding(
                            text=sentence.strip(),
                            confidence=confidence,
                            category=pattern.category,
                            evidence=match.group(),
                            context=self._get_sentence_context(sentence, content)
                        )

                        findings.append(finding)

                except re.error as e:
                    self.logger.warning(f"Regex error in pattern {pattern_str}: {e}")

        return findings

    def _calculate_context_confidence(self, sentence: str) -> float:
        """Calculate confidence based on sentence context"""
        confidence = 1.0

        # Boost confidence for sentences with specific indicators
        confidence_boosters = [
            r'\b(?:results?\s*show|found|observed|demonstrated)\b',
            r'\b(?:significant|notable|important|remarkable)\b',
            r'\b(?:clearly|strongly|significantly)\b'
        ]

        for booster in confidence_boosters:
            if re.search(booster, sentence, re.IGNORECASE):
                confidence *= 1.1
                break

        # Reduce confidence for speculative language
        confidence_reducers = [
            r'\b(?:might|could|perhaps|possibly|potentially)\b',
            r'\b(?:suggests?\s*that|seems?\s+to|appears?\s+to)\b',
            r'\b(?:tend\s+to|typically|generally)\b'
        ]

        for reducer in confidence_reducers:
            if re.search(reducer, sentence, re.IGNORECASE):
                confidence *= 0.8
                break

        return min(confidence, 1.0)

    def _get_sentence_context(self, sentence: str, full_content: str) -> str:
        """Get broader context around the finding sentence"""
        # Find sentence in content and get surrounding sentences
        try:
            sentences = self._split_into_sentences(full_content)

            if sentence in sentences:
                sentence_index = sentences.index(sentence)
                start_index = max(0, sentence_index - 1)
                end_index = min(len(sentences), sentence_index + 2)

                context_sentences = sentences[start_index:end_index]
                return ' '.join(context_sentences)
        except:
            pass

        return sentence

    def _consolidate_findings(self, findings: List[ExtractedFinding]) -> List[ExtractedFinding]:
        """Remove duplicate and consolidate similar findings"""
        if not findings:
            return []

        # Sort by confidence
        findings.sort(key=lambda x: x.confidence, reverse=True)

        consolidated = []
        seen_texts = set()

        for finding in findings:
            # Check for duplicates
            text_key = self._normalize_finding_text(finding.text)

            # Check if similar to existing finding
            is_duplicate = False
            for seen_text in seen_texts:
                if self._text_similarity(text_key, seen_text) > 0.8:
                    is_duplicate = True
                    break

            if not is_duplicate:
                consolidated.append(finding)
                seen_texts.add(text_key)

        return consolidated

    def _normalize_finding_text(self, text: str) -> str:
        """Normalize text for duplicate detection"""
        # Remove extra whitespace and convert to lowercase
        text = re.sub(r'\s+', ' ', text.lower().strip())

        # Remove common stopwords
        if self.nltk_available:
            words = [word for word in text.split() if word not in self.stop_words]
            text = ' '.join(words)

        return text

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.split())
        words2 = set(text2.split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _generate_summary(self, findings: List[ExtractedFinding]) -> Dict[str, Any]:
        """Generate summary of extracted findings"""
        if not findings:
            return {
                'total_findings': 0,
                'high_confidence': 0,
                'medium_confidence': 0,
                'low_confidence': 0,
                'categories': {},
                'average_confidence': 0.0
            }

        # Count by confidence level
        high_conf = sum(1 for f in findings if f.confidence >= self.confidence_thresholds['high'])
        medium_conf = sum(1 for f in findings if self.confidence_thresholds['medium'] <= f.confidence < self.confidence_thresholds['high'])
        low_conf = sum(1 for f in findings if f.confidence < self.confidence_thresholds['medium'])

        # Count by category
        category_counts = defaultdict(int)
        for finding in findings:
            category_counts[finding.category] += 1

        # Calculate average confidence
        avg_confidence = sum(f.confidence for f in findings) / len(findings)

        return {
            'total_findings': len(findings),
            'high_confidence': high_conf,
            'medium_confidence': medium_conf,
            'low_confidence': low_conf,
            'categories': dict(category_counts),
            'average_confidence': avg_confidence
        }

    def get_extraction_methods(self) -> Dict[str, Any]:
        """
        Get information about extraction methods

        Returns:
            Dictionary with extraction method information
        """
        return {
            'patterns': [
                {
                    'name': pattern.name,
                    'category': pattern.category,
                    'confidence_weight': pattern.confidence_weight,
                    'pattern_count': len(pattern.patterns)
                }
                for pattern in self.finding_patterns
            ],
            'confidence_thresholds': self.confidence_thresholds,
            'nltk_available': self.nltk_available,
            'deduplication_enabled': True,
            'context_analysis_enabled': True
        }

    def add_custom_pattern(
        self,
        name: str,
        patterns: List[str],
        category: str,
        confidence_weight: float = 0.5
    ) -> None:
        """
        Add custom finding pattern

        Args:
            name: Pattern name
            patterns: List of regex patterns
            category: Finding category
            confidence_weight: Base confidence weight
        """
        custom_pattern = FindingPattern(
            name=name,
            patterns=patterns,
            confidence_weight=confidence_weight,
            category=category
        )

        self.finding_patterns.append(custom_pattern)
        self.logger.info(f"Added custom finding pattern: {name}")