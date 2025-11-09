"""
Research Paper Structure Recognition System
Identifies and analyzes sections of scientific papers (abstract, methods, results, etc.)
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SectionPattern:
    """Pattern for identifying paper sections"""
    name: str
    patterns: List[str]
    weight: float = 1.0
    required: bool = False


class PaperStructureAnalyzer:
    """
    Analyzes research paper structure and identifies standard sections

    Features:
    - Section identification (abstract, introduction, methods, results, etc.)
    - Order validation
    - Content extraction by section
    - Confidence scoring for section identification
    """

    def __init__(self):
        """Initialize structure analyzer"""
        self.logger = logging.getLogger(__name__)

        # Define section patterns for recognition
        self.section_patterns = self._initialize_section_patterns()

        # Section order (typical for scientific papers)
        self.expected_order = [
            'abstract',
            'introduction',
            'methods',
            'results',
            'discussion',
            'conclusion',
            'references',
            'appendix'
        ]

    def _initialize_section_patterns(self) -> Dict[str, SectionPattern]:
        """Initialize patterns for section identification"""
        patterns = {
            'abstract': SectionPattern(
                name='abstract',
                patterns=[
                    r'^abstract$',
                    r'^abstract\s*[:\-]?\s*$',
                    r'\babstract\b',
                    r'^summary$',
                    r'^summary\s*[:\-]?\s*$'
                ],
                weight=1.0,
                required=True
            ),

            'introduction': SectionPattern(
                name='introduction',
                patterns=[
                    r'^introduction$',
                    r'^1\.\s*introduction',
                    r'^introduction\s*[:\-]?\s*$',
                    r'\bintroduction\b',
                    r'^background$',
                    r'^background\s*[:\-]?\s*$'
                ],
                weight=1.0,
                required=True
            ),

            'methods': SectionPattern(
                name='methods',
                patterns=[
                    r'^methods?$',
                    r'^2\.\s*methods?',
                    r'^methods?\s*[:\-]?\s*$',
                    r'^methodology$',
                    r'^methodology\s*[:\-]?\s*$',
                    r'^materials?\s+and\s+methods?$',
                    r'^experimental\s+methods?$',
                    r'^procedures?$',
                    r'^study\s+design$'
                ],
                weight=1.0,
                required=True
            ),

            'results': SectionPattern(
                name='results',
                patterns=[
                    r'^results?$',
                    r'^3\.\s*results?',
                    r'^results?\s*[:\-]?\s*$',
                    r'^findings?$',
                    r'^findings?\s*[:\-]?\s*$',
                    r'^outcomes?$',
                    r'^data\s+analysis$',
                    r'^statistical\s+analysis$'
                ],
                weight=1.0,
                required=True
            ),

            'discussion': SectionPattern(
                name='discussion',
                patterns=[
                    r'^discussion$',
                    r'^4\.\s*discussion',
                    r'^discussion\s*[:\-]?\s*$',
                    r'^analysis$',
                    r'^interpretation$',
                    r'^interpretation\s*[:\-]?\s*$',
                    r'^implications$'
                ],
                weight=1.0,
                required=False
            ),

            'conclusion': SectionPattern(
                name='conclusion',
                patterns=[
                    r'^conclusion$',
                    r'^5\.\s*conclusion',
                    r'^conclusion\s*[:\-]?\s*$',
                    r'^conclusions$',
                    r'^conclusions\s*[:\-]?\s*$',
                    r'^summary$',
                    r'^summary\s*[:\-]?\s*$',
                    r'^future\s+work$',
                    r'^limitations$'
                ],
                weight=1.0,
                required=False
            ),

            'references': SectionPattern(
                name='references',
                patterns=[
                    r'^references?$',
                    r'^bibliography$',
                    r'^references?\s*[:\-]?\s*$',
                    r'^bibliography\s*[:\-]?\s*$',
                    r'^works\s+cited$',
                    r'^cited\s+works$'
                ],
                weight=0.8,
                required=False
            ),

            'appendix': SectionPattern(
                name='appendix',
                patterns=[
                    r'^appendix$',
                    r'^appendix\s+[a-z]$',
                    r'^appendix\s*[:\-]?\s*$',
                    r'^supplementary\s+material$',
                    r'^supplemental\s+material$'
                ],
                weight=0.6,
                required=False
            )
        }

        return patterns

    def analyze_structure(self, content: str) -> Dict[str, Any]:
        """
        Analyze paper structure and identify sections

        Args:
            content: Full text content of the paper

        Returns:
            Dictionary containing:
            - sections: Identified sections with content
            - order: Order of identified sections
            - confidence: Overall confidence in structure identification
            - missing_required: List of missing required sections
        """
        try:
            # Preprocess content
            processed_content = self._preprocess_content(content)

            # Identify sections
            sections, section_positions = self._identify_sections(processed_content)

            # Extract content for each section
            section_contents = self._extract_section_contents(
                processed_content, sections, section_positions
            )

            # Validate section order
            order_validation = self._validate_section_order(sections)

            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(section_contents)

            # Identify missing required sections
            missing_required = self._identify_missing_sections(sections)

            return {
                'sections': section_contents,
                'section_order': sections,
                'section_positions': section_positions,
                'order_validation': order_validation,
                'confidence': overall_confidence,
                'missing_required': missing_required,
                'total_sections': len(sections)
            }

        except Exception as e:
            self.logger.error(f"Structure analysis failed: {str(e)}")
            raise Exception(f"Paper structure analysis failed: {str(e)}")

    def _preprocess_content(self, content: str) -> str:
        """
        Preprocess content for better section identification

        Args:
            content: Raw text content

        Returns:
            Preprocessed content
        """
        if not content:
            return ""

        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # Split into lines
        lines = content.split('\n')

        # Process each line
        processed_lines = []
        for line in lines:
            # Remove extra whitespace but preserve line structure
            line = line.strip()

            # Skip empty lines (they help identify section boundaries)
            if line:
                processed_lines.append(line)

        return '\n'.join(processed_lines)

    def _identify_sections(self, content: str) -> Tuple[List[str], Dict[str, int]]:
        """
        Identify sections using pattern matching

        Args:
            content: Preprocessed content

        Returns:
            Tuple of (section_names, section_positions)
        """
        lines = content.split('\n')
        sections = []
        section_positions = {}

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Check against section patterns
            for section_name, pattern in self.section_patterns.items():
                for pattern_str in pattern.patterns:
                    try:
                        # Try to match the pattern
                        if re.match(pattern_str, line_lower, re.IGNORECASE):
                            if section_name not in sections:
                                sections.append(section_name)
                                section_positions[section_name] = i
                                self.logger.debug(f"Found {section_name} at line {i}: {line}")
                                break
                    except re.error as e:
                        self.logger.warning(f"Regex error in pattern {pattern_str}: {e}")

        return sections, section_positions

    def _extract_section_contents(
        self,
        content: str,
        sections: List[str],
        section_positions: Dict[str, int]
    ) -> Dict[str, str]:
        """
        Extract content for each identified section

        Args:
            content: Full text content
            sections: List of section names
            section_positions: Line positions of sections

        Returns:
            Dictionary mapping section names to content
        """
        lines = content.split('\n')
        section_contents = {}

        for i, section_name in enumerate(sections):
            start_pos = section_positions[section_name]

            # Find end position (start of next section or end of document)
            end_pos = len(lines)
            if i + 1 < len(sections):
                next_section = sections[i + 1]
                end_pos = section_positions.get(next_section, len(lines))

            # Extract section content
            section_lines = lines[start_pos + 1:end_pos]  # Skip section header

            # Clean up section content
            section_content = '\n'.join(section_lines).strip()

            # Remove leading non-content lines (page numbers, etc.)
            section_content = self._clean_section_content(section_content)

            if section_content:
                section_contents[section_name] = section_content
            else:
                section_contents[section_name] = ""

        return section_contents

    def _clean_section_content(self, content: str) -> str:
        """
        Clean section content by removing artifacts

        Args:
            content: Raw section content

        Returns:
            Cleaned content
        """
        if not content:
            return ""

        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()

            # Skip likely page numbers or headers
            if re.match(r'^\d+$', line):
                continue
            if re.match(r'^page\s+\d+', line, re.IGNORECASE):
                continue
            if len(line) < 3 and not line.endswith('.'):
                continue  # Skip very short lines

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _validate_section_order(self, sections: List[str]) -> Dict[str, Any]:
        """
        Validate that sections are in expected order

        Args:
            sections: List of identified sections

        Returns:
            Dictionary with order validation results
        """
        if len(sections) < 2:
            return {
                'valid': True,
                'message': 'Insufficient sections to validate order'
            }

        # Calculate order score
        order_scores = []
        for i, section in enumerate(sections):
            if section in self.expected_order:
                expected_pos = self.expected_order.index(section)
                # Compare with actual position relative to expected
                actual_pos = i
                max_pos = len(sections) - 1
                expected_normalized = expected_pos / len(self.expected_order)
                actual_normalized = actual_pos / max_pos if max_pos > 0 else 0
                score = 1 - abs(expected_normalized - actual_normalized)
                order_scores.append(score)

        overall_order_score = sum(order_scores) / len(order_scores) if order_scores else 1.0

        return {
            'valid': overall_order_score >= 0.7,
            'score': overall_order_score,
            'message': f"Order validation score: {overall_order_score:.2f}"
        }

    def _calculate_overall_confidence(self, section_contents: Dict[str, str]) -> float:
        """
        Calculate overall confidence in structure identification

        Args:
            section_contents: Dictionary of section contents

        Returns:
            Overall confidence score (0-1)
        """
        if not section_contents:
            return 0.0

        confidence_scores = []

        for section_name, content in section_contents.items():
            section_score = 0.0

            # Check if section has content
            if content and len(content.strip()) > 50:
                section_score += 0.5

            # Check if section is expected (higher weight for core sections)
            if section_name in ['abstract', 'introduction', 'methods', 'results']:
                section_score += 0.5
            elif section_name in ['discussion', 'conclusion']:
                section_score += 0.3
            else:
                section_score += 0.2

            confidence_scores.append(min(section_score, 1.0))

        # Average confidence across all sections
        overall_confidence = sum(confidence_scores) / len(confidence_scores)

        return min(overall_confidence, 1.0)

    def _identify_missing_sections(self, sections: List[str]) -> List[str]:
        """
        Identify missing required sections

        Args:
            sections: List of identified sections

        Returns:
            List of missing required section names
        """
        missing = []
        for section_name, pattern in self.section_patterns.items():
            if pattern.required and section_name not in sections:
                missing.append(section_name)

        return missing

    def get_supported_sections(self) -> List[str]:
        """
        Get list of supported section types

        Returns:
            List of supported section names
        """
        return list(self.section_patterns.keys())

    def add_section_pattern(self, section_name: str, patterns: List[str], weight: float = 1.0) -> None:
        """
        Add custom section pattern

        Args:
            section_name: Name of the section
            patterns: List of regex patterns for identification
            weight: Weight for confidence scoring
        """
        self.section_patterns[section_name] = SectionPattern(
            name=section_name,
            patterns=patterns,
            weight=weight,
            required=False
        )
        self.logger.info(f"Added custom section pattern: {section_name}")

    def analyze_section_quality(self, section_name: str, content: str) -> Dict[str, Any]:
        """
        Analyze quality of a specific section

        Args:
            section_name: Name of the section
            content: Section content

        Returns:
            Dictionary with quality analysis
        """
        if not content:
            return {
                'section': section_name,
                'quality_score': 0.0,
                'word_count': 0,
                'issues': ['No content found']
            }

        word_count = len(content.split())
        sentence_count = len(re.split(r'[.!?]+', content))

        # Basic quality metrics
        quality_metrics = {
            'section': section_name,
            'quality_score': 0.0,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': word_count / max(sentence_count, 1),
            'issues': []
        }

        # Section-specific quality checks
        if section_name == 'abstract':
            if word_count < 100:
                quality_metrics['issues'].append('Abstract too short (< 100 words)')
            elif word_count > 300:
                quality_metrics['issues'].append('Abstract too long (> 300 words)')
            else:
                quality_metrics['quality_score'] = 1.0

        elif section_name in ['introduction', 'methods', 'results']:
            if word_count < 200:
                quality_metrics['issues'].append(f'{section_name.capitalize()} too short (< 200 words)')
            else:
                quality_metrics['quality_score'] = min(word_count / 500, 1.0)

        else:
            # Generic quality assessment
            if word_count > 50:
                quality_metrics['quality_score'] = min(word_count / 200, 1.0)

        return quality_metrics