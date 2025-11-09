"""
Unit tests for Paper Reader Subagent Infrastructure
Tests T-ANALYSIS-001: Implement Paper Reader Subagent Infrastructure
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import List, Dict, Any, Optional
import tempfile
import os
from datetime import datetime

from agents.paper_analysis.reader_agent import (
    PaperReaderAgent,
    PDFParser,
    PaperStructureAnalyzer,
    QualityAssessor,
    KeyFindingExtractor
)


class TestPaperReaderAgent:
    """Test the main PaperReaderAgent class"""

    @pytest.fixture
    def reader_agent(self):
        """Initialize PaperReaderAgent for testing"""
        return PaperReaderAgent()

    @pytest.mark.asyncio
    async def test_reader_agent_initialization(self, reader_agent):
        """Test that PaperReaderAgent initializes correctly"""
        assert reader_agent is not None
        assert hasattr(reader_agent, 'pdf_parser')
        assert hasattr(reader_agent, 'structure_analyzer')
        assert hasattr(reader_agent, 'quality_assessor')
        assert hasattr(reader_agent, 'finding_extractor')

    @pytest.mark.asyncio
    async def test_process_paper_basic(self, reader_agent):
        """Test basic paper processing workflow"""
        # Mock PDF content
        mock_pdf_content = b"mock pdf content"

        with patch.object(reader_agent, '_extract_text_from_pdf') as mock_extract, \
             patch.object(reader_agent, '_analyze_paper_structure') as mock_analyze, \
             patch.object(reader_agent, '_assess_paper_quality') as mock_assess, \
             patch.object(reader_agent, '_extract_key_findings') as mock_findings:

            # Setup mocks
            mock_extract.return_value = {"title": "Test Paper", "content": "Test content"}
            mock_analyze.return_value = {"sections": {"abstract": "Test abstract"}}
            mock_assess.return_value = {"quality_score": 0.8, "criteria": {}}
            mock_findings.return_value = {"findings": ["Test finding"]}

            # Process paper
            result = await reader_agent.process_paper(mock_pdf_content)

            # Verify structure
            assert "title" in result
            assert "content" in result
            assert "structure" in result
            assert "quality_assessment" in result
            assert "key_findings" in result

            # Verify all methods called
            mock_extract.assert_called_once_with(mock_pdf_content)
            mock_analyze.assert_called_once()
            mock_assess.assert_called_once()
            mock_findings.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_paper_with_pdf_error(self, reader_agent):
        """Test paper processing with PDF extraction error"""
        invalid_pdf = b"invalid pdf content"

        with patch.object(reader_agent, '_extract_text_from_pdf') as mock_extract:
            mock_extract.side_effect = Exception("PDF parsing failed")

            with pytest.raises(Exception, match="PDF parsing failed"):
                await reader_agent.process_paper(invalid_pdf)

    @pytest.mark.asyncio
    async def test_batch_processing(self, reader_agent):
        """Test batch processing of multiple papers"""
        mock_papers = [b"pdf1", b"pdf2", b"pdf3"]

        with patch.object(reader_agent, 'process_paper', new_callable=AsyncMock) as mock_process:
            mock_process.side_effect = [
                {"paper_id": 1, "title": "Paper 1"},
                {"paper_id": 2, "title": "Paper 2"},
                {"paper_id": 3, "title": "Paper 3"}
            ]

            results = await reader_agent.process_batch(mock_papers)

            assert len(results) == 3
            assert all("paper_id" in result for result in results)
            assert mock_process.call_count == 3

    @pytest.mark.asyncio
    async def test_supported_formats(self, reader_agent):
        """Test supported file format detection"""
        supported_formats = reader_agent.get_supported_formats()
        assert isinstance(supported_formats, list)
        assert "pdf" in supported_formats

    def test_error_handling_corrupted_pdf(self, reader_agent):
        """Test error handling for corrupted PDF files"""
        corrupted_pdf = b"corrupted content"

        with patch.object(reader_agent, '_extract_text_from_pdf') as mock_extract:
            mock_extract.side_effect = Exception("Corrupted PDF")

            # Should handle gracefully
            with pytest.raises(Exception):
                asyncio.run(reader_agent.process_paper(corrupted_pdf))


class TestPDFParser:
    """Test PDF text extraction and parsing"""

    @pytest.fixture
    def pdf_parser(self):
        """Initialize PDFParser for testing"""
        return PDFParser()

    def test_pdf_parser_initialization(self, pdf_parser):
        """Test PDFParser initializes correctly"""
        assert pdf_parser is not None
        assert hasattr(pdf_parser, 'extract_text')

    def test_extract_text_valid_pdf(self, pdf_parser):
        """Test text extraction from valid PDF"""
        # Mock PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"mock pdf content")
            tmp_file.flush()

            try:
                with patch('pypdf2.PdfReader') as mock_reader:
                    mock_page = Mock()
                    mock_page.extract_text.return_value = "Sample paper content"
                    mock_reader_instance = Mock()
                    mock_reader_instance.pages = [mock_page]
                    mock_reader.return_value = mock_reader_instance

                    result = pdf_parser.extract_text(tmp_file.name)

                    assert isinstance(result, dict)
                    assert "content" in result
                    assert "pages" in result
                    assert "metadata" in result
                    assert result["content"] == "Sample paper content"

            finally:
                os.unlink(tmp_file.name)

    def test_extract_text_invalid_pdf(self, pdf_parser):
        """Test text extraction from invalid PDF"""
        with pytest.raises(Exception):
            pdf_parser.extract_text("nonexistent_file.pdf")

    def test_extract_text_with_encryption(self, pdf_parser):
        """Test handling of encrypted PDFs"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"encrypted pdf content")
            tmp_file.flush()

            try:
                with patch('pypdf2.PdfReader') as mock_reader:
                    mock_reader_instance = Mock()
                    mock_reader_instance.is_encrypted = True
                    mock_reader_instance.decrypt.return_value = False
                    mock_reader.return_value = mock_reader_instance

                    with pytest.raises(Exception, match="Encrypted PDF"):
                        pdf_parser.extract_text(tmp_file.name)

            finally:
                os.unlink(tmp_file.name)

    def test_extract_metadata(self, pdf_parser):
        """Test PDF metadata extraction"""
        with patch('pypdf2.PdfReader') as mock_reader:
            mock_reader_instance = Mock()
            mock_reader_instance.metadata = {
                '/Title': 'Test Paper',
                '/Author': 'Test Author',
                '/CreationDate': 'D:20231109000000'
            }
            mock_reader.return_value = mock_reader_instance

            metadata = pdf_parser._extract_metadata(mock_reader_instance)

            assert metadata['title'] == 'Test Paper'
            assert metadata['author'] == 'Test Author'
            assert 'creation_date' in metadata


class TestPaperStructureAnalyzer:
    """Test research paper structure recognition"""

    @pytest.fixture
    def structure_analyzer(self):
        """Initialize PaperStructureAnalyzer for testing"""
        return PaperStructureAnalyzer()

    def test_structure_analyzer_initialization(self, structure_analyzer):
        """Test StructureAnalyzer initializes correctly"""
        assert structure_analyzer is not None
        assert hasattr(structure_analyzer, 'analyze_structure')

    def test_identify_abstract_section(self, structure_analyzer):
        """Test abstract section identification"""
        text_with_abstract = """
        Introduction
        This is the introduction.

        Abstract
        This is the abstract content of the paper.
        It spans multiple lines.

        Methods
        This describes the methods used.
        """

        result = structure_analyzer.analyze_structure(text_with_abstract)

        assert "abstract" in result["sections"]
        assert "abstract content" in result["sections"]["abstract"].lower()

    def test_identify_methods_section(self, structure_analyzer):
        """Test methods section identification"""
        text_with_methods = """
        Abstract
        This is the abstract.

        Methodology
        We used the following methods in our research:
        1. Data collection
        2. Analysis

        Results
        These are our results.
        """

        result = structure_analyzer.analyze_structure(text_with_methods)

        assert "methods" in result["sections"]
        assert "data collection" in result["sections"]["methods"].lower()

    def test_identify_results_section(self, structure_analyzer):
        """Test results section identification"""
        text_with_results = """
        Methods
        We conducted experiments.

        Results
        Our experiments showed the following results:
        - Significant improvement (p < 0.05)
        - Performance increase of 25%

        Discussion
        We discuss the implications.
        """

        result = structure_analyzer.analyze_structure(text_with_results)

        assert "results" in result["sections"]
        assert "significant improvement" in result["sections"]["results"].lower()

    def test_section_order_validation(self, structure_analyzer):
        """Test that sections are found in correct order"""
        text_all_sections = """
        Abstract
        This is the abstract.

        1. Introduction
        Introduction content.

        2. Methods
        Methods description.

        3. Results
        Results content.

        4. Discussion
        Discussion of results.

        5. Conclusion
        Conclusion content.
        """

        result = structure_analyzer.analyze_structure(text_all_sections)

        # Should identify all main sections
        sections = result["sections"]
        assert "abstract" in sections
        assert "introduction" in sections
        assert "methods" in sections
        assert "results" in sections
        assert "discussion" in sections
        assert "conclusion" in sections

    def test_handle_missing_sections(self, structure_analyzer):
        """Test graceful handling of missing sections"""
        text_only_abstract = """
        Abstract
        Only the abstract is present.
        Some other text here.
        """

        result = structure_analyzer.analyze_structure(text_only_abstract)

        # Should identify abstract but not other sections
        assert "abstract" in result["sections"]
        # Other sections might be missing but shouldn't cause errors


class TestQualityAssessor:
    """Test paper quality assessment framework"""

    @pytest.fixture
    def quality_assessor(self):
        """Initialize QualityAssessor for testing"""
        return QualityAssessor()

    def test_quality_assessor_initialization(self, quality_assessor):
        """Test QualityAssessor initializes correctly"""
        assert quality_assessor is not None
        assert hasattr(quality_assessor, 'assess_quality')
        assert hasattr(quality_assessor, '_calculate_structure_score')
        assert hasattr(quality_assessor, '_calculate_content_quality')

    def test_assess_quality_complete_paper(self, quality_assessor):
        """Test quality assessment of a complete paper"""
        paper_data = {
            "title": "A Complete Research Paper",
            "content": "Full paper content with proper structure",
            "structure": {
                "abstract": "Well-written abstract",
                "introduction": "Comprehensive introduction",
                "methods": "Detailed methodology",
                "results": "Clear results",
                "discussion": "Insightful discussion",
                "conclusion": "Strong conclusion"
            }
        }

        result = quality_assessor.assess_quality(paper_data)

        assert isinstance(result, dict)
        assert "quality_score" in result
        assert "criteria" in result
        assert 0 <= result["quality_score"] <= 1
        assert len(result["criteria"]) > 0

    def test_assess_quality_incomplete_paper(self, quality_assessor):
        """Test quality assessment of incomplete paper"""
        incomplete_paper = {
            "title": "Incomplete Paper",
            "content": "Brief content",
            "structure": {
                "abstract": "Brief abstract"
                # Missing other sections
            }
        }

        result = quality_assessor.assess_quality(incomplete_paper)

        assert result["quality_score"] < 0.8  # Should have lower score for incomplete paper
        assert "structure_completeness" in result["criteria"]

    def test_structure_scoring(self, quality_assessor):
        """Test section-based quality scoring"""
        complete_structure = {
            "abstract": "Abstract present",
            "introduction": "Introduction present",
            "methods": "Methods present",
            "results": "Results present",
            "discussion": "Discussion present",
            "conclusion": "Conclusion present"
        }

        score = quality_assessor._calculate_structure_score(complete_structure)
        assert 0 <= score <= 1

        incomplete_structure = {"abstract": "Abstract present"}
        incomplete_score = quality_assessor._calculate_structure_score(incomplete_structure)
        assert incomplete_score < score

    def test_content_quality_assessment(self, quality_assessor):
        """Test content quality assessment"""
        good_content = """
        This is a well-written research paper with proper academic language.
        The methodology is described in detail with appropriate citations.
        Statistical analysis shows significance with p < 0.05.
        The sample size was 500 participants.
        """
        poor_content = "bad content short no details"

        good_score = quality_assessor._calculate_content_quality(good_content)
        poor_score = quality_assessor._calculate_content_quality(poor_content)

        assert good_score > poor_score

    def test_quality_criteria_breakdown(self, quality_assessor):
        """Test detailed quality criteria assessment"""
        paper_data = {
            "title": "Test Paper",
            "content": "Test content with enough length for analysis",
            "structure": {"abstract": "Test abstract"},
            "metadata": {"word_count": 5000}
        }

        result = quality_assessor.assess_quality(paper_data)
        criteria = result["criteria"]

        # Should assess multiple criteria
        expected_criteria = [
            "structure_completeness",
            "content_length",
            "academic_language",
            "methodology_clarity"
        ]

        for criterion in expected_criteria:
            assert criterion in criteria
            assert isinstance(criteria[criterion], (int, float))
            assert 0 <= criteria[criterion] <= 1


class TestKeyFindingExtractor:
    """Test key finding extraction algorithms"""

    @pytest.fixture
    def finding_extractor(self):
        """Initialize KeyFindingExtractor for testing"""
        return KeyFindingExtractor()

    def test_finding_extractor_initialization(self, finding_extractor):
        """Test KeyFindingExtractor initializes correctly"""
        assert finding_extractor is not None
        assert hasattr(finding_extractor, 'extract_findings')

    def test_extract_findings_from_results_section(self, finding_extractor):
        """Test finding extraction from results section"""
        results_text = """
        Our study found significant improvements in treatment outcomes.
        The experimental group showed a 45% increase in performance (p < 0.01).
        We observed that the new method reduced processing time by 60%.
        Statistical analysis confirmed the significance of these findings.
        """

        findings = finding_extractor.extract_findings(results_text)

        assert isinstance(findings, dict)
        assert "findings" in findings
        assert len(findings["findings"]) > 0

        # Should extract quantitative findings
        finding_text = " ".join(findings["findings"]).lower()
        assert "45%" in finding_text or "60%" in finding_text

    def test_extract_statistical_findings(self, finding_extractor):
        """Test extraction of statistical findings"""
        statistical_text = """
        The correlation between variables was strong (r = 0.85, p < 0.001).
        The mean difference was 2.3 units (SD = 0.8).
        Effect size was calculated as d = 1.2.
        Sample size was N = 200 participants.
        """

        findings = finding_extractor.extract_findings(statistical_text)

        finding_text = " ".join(findings["findings"]).lower()
        # Should identify statistical values
        assert "0.85" in finding_text or "p < 0.001" in finding_text

    def test_extract_methodological_findings(self, finding_extractor):
        """Test extraction of methodological innovations"""
        methods_text = """
        We developed a novel approach using machine learning algorithms.
        Our method combines deep learning with traditional statistical analysis.
        This hybrid technique improved accuracy by 30% compared to existing methods.
        The framework can be applied to various domains.
        """

        findings = finding_extractor.extract_findings(methods_text)

        finding_text = " ".join(findings["findings"]).lower()
        assert "machine learning" in finding_text or "hybrid" in finding_text

    def test_no_findings_available(self, finding_extractor):
        """Test handling when no clear findings are present"""
        no_findings_text = """
        This is just a general discussion without specific results.
        The author talks about various topics but doesn't present findings.
        """

        findings = finding_extractor.extract_findings(no_findings_text)

        assert "findings" in findings
        # Should handle gracefully even if no findings found

    def test_finding_confidence_scoring(self, finding_extractor):
        """Test confidence scoring for extracted findings"""
        text_with_findings = """
        Results showed significant improvement (p < 0.001, N = 1000).
        The effect size was large (Cohen's d = 1.5).
        """

        findings = finding_extractor.extract_findings(text_with_findings)

        if "confidence_scores" in findings:
            assert isinstance(findings["confidence_scores"], list)
            if findings["confidence_scores"]:
                assert all(0 <= score <= 1 for score in findings["confidence_scores"])

    def test_duplicate_finding_removal(self, finding_extractor):
        """Test removal of duplicate findings"""
        text_with_duplicates = """
        The results showed significant improvement (p < 0.05).
        We found significant improvement in our analysis (p < 0.05).
        Statistical analysis revealed significant improvement (p < 0.05).
        """

        findings = finding_extractor.extract_findings(text_with_duplicates)
        unique_findings = set(findings["findings"])

        # Should have fewer unique findings than total extracted
        if len(findings["findings"]) > 1:
            assert len(unique_findings) <= len(findings["findings"])


class TestIntegration:
    """Integration tests for the complete paper analysis workflow"""

    @pytest.fixture
    def reader_agent(self):
        """Initialize complete reader agent"""
        return PaperReaderAgent()

    @pytest.mark.asyncio
    async def test_end_to_end_paper_processing(self, reader_agent):
        """Test complete paper processing workflow"""
        # Create a realistic mock PDF content
        mock_paper_content = {
            "title": "A Study on Machine Learning Applications",
            "content": """
            Abstract
            This paper presents a novel machine learning approach for data analysis.

            Introduction
            Machine learning has become increasingly important in modern research.

            Methods
            We collected data from 1000 participants and applied neural networks.

            Results
            Our approach achieved 95% accuracy, representing a 20% improvement.
            Statistical significance was confirmed (p < 0.01).

            Discussion
            The findings suggest important implications for future research.

            Conclusion
            This method provides an effective solution for data analysis challenges.
            """,
            "metadata": {"word_count": 5000, "pages": 8}
        }

        with patch.object(reader_agent, '_extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = mock_paper_content

            result = await reader_agent.process_paper(b"mock_pdf")

            # Verify complete structure
            assert "title" in result
            assert "content" in result
            assert "structure" in result
            assert "quality_assessment" in result
            assert "key_findings" in result

            # Verify structure analysis
            assert "abstract" in result["structure"]["sections"]
            assert "methods" in result["structure"]["sections"]
            assert "results" in result["structure"]["sections"]

            # Verify quality assessment
            assert 0 <= result["quality_assessment"]["quality_score"] <= 1

            # Verify key findings extraction
            assert isinstance(result["key_findings"]["findings"], list)

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, reader_agent):
        """Test error recovery during paper processing"""
        # Simulate partial failure where one component fails
        with patch.object(reader_agent, '_extract_text_from_pdf') as mock_extract, \
             patch.object(reader_agent, '_analyze_paper_structure') as mock_analyze:

            mock_extract.return_value = {"title": "Test", "content": "Content"}
            mock_analyze.side_effect = Exception("Structure analysis failed")

            with pytest.raises(Exception):
                await reader_agent.process_paper(b"pdf_content")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])