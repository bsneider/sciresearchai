"""
Paper Reader Subagent Core Infrastructure
Implements T-ANALYSIS-001: Implement Paper Reader Subagent Infrastructure

Provides comprehensive paper analysis capabilities including:
- PDF text extraction and parsing
- Research paper structure recognition
- Quality assessment framework
- Key finding extraction algorithms
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .pdf_parser import PDFParser
from .structure_analyzer import PaperStructureAnalyzer
from .quality_assessor import QualityAssessor
from .finding_extractor import KeyFindingExtractor


class PaperReaderAgent:
    """
    Core PaperReaderAgent for comprehensive scientific paper analysis

    Integrates PDF parsing, structure analysis, quality assessment,
    and key finding extraction into a unified workflow.
    """

    def __init__(self):
        """Initialize PaperReaderAgent with all analysis components"""
        self.logger = logging.getLogger(__name__)

        # Initialize core components
        self.pdf_parser = PDFParser()
        self.structure_analyzer = PaperStructureAnalyzer()
        self.quality_assessor = QualityAssessor()
        self.finding_extractor = KeyFindingExtractor()

        # Configuration
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        self.supported_formats = ['pdf']

        self.logger.info("PaperReaderAgent initialized successfully")

    async def process_paper(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Process a scientific paper from PDF content to structured analysis

        Args:
            pdf_content: Raw PDF file content as bytes

        Returns:
            Dictionary containing complete paper analysis including:
            - title: Paper title
            - content: Extracted text content
            - structure: Identified paper sections
            - quality_assessment: Quality scores and criteria
            - key_findings: Extracted key findings

        Raises:
            Exception: If PDF processing or analysis fails
        """
        try:
            self.logger.info("Starting paper processing")

            # Step 1: Extract text and metadata from PDF
            paper_data = await self._extract_text_from_pdf(pdf_content)
            self.logger.debug(f"PDF extraction completed: {paper_data.get('title', 'Unknown title')}")

            # Step 2: Analyze paper structure
            structure_analysis = await self._analyze_paper_structure(paper_data)
            paper_data['structure'] = structure_analysis
            self.logger.debug("Structure analysis completed")

            # Step 3: Assess paper quality
            quality_assessment = await self._assess_paper_quality(paper_data)
            paper_data['quality_assessment'] = quality_assessment
            self.logger.debug(f"Quality assessment completed: {quality_assessment.get('quality_score', 0):.2f}")

            # Step 4: Extract key findings
            key_findings = await self._extract_key_findings(paper_data)
            paper_data['key_findings'] = key_findings
            self.logger.debug(f"Key findings extracted: {len(key_findings.get('findings', []))}")

            # Add processing metadata
            paper_data['processed_at'] = datetime.now().isoformat()
            paper_data['processor_version'] = '1.0.0'

            self.logger.info("Paper processing completed successfully")
            return paper_data

        except Exception as e:
            self.logger.error(f"Paper processing failed: {str(e)}")
            raise Exception(f"Failed to process paper: {str(e)}")

    async def process_batch(self, pdf_contents: List[bytes]) -> List[Dict[str, Any]]:
        """
        Process multiple papers in batch

        Args:
            pdf_contents: List of PDF file contents as bytes

        Returns:
            List of paper analysis results
        """
        self.logger.info(f"Starting batch processing of {len(pdf_contents)} papers")

        # Process papers concurrently with controlled parallelism
        semaphore = asyncio.Semaphore(5)  # Limit concurrent processing

        async def process_single_paper(pdf_content: bytes, index: int) -> Dict[str, Any]:
            async with semaphore:
                try:
                    result = await self.process_paper(pdf_content)
                    result['batch_index'] = index
                    return result
                except Exception as e:
                    self.logger.error(f"Failed to process paper {index}: {str(e)}")
                    return {
                        'batch_index': index,
                        'error': str(e),
                        'processed_at': datetime.now().isoformat()
                    }

        # Process all papers
        tasks = [
            process_single_paper(pdf_content, i)
            for i, pdf_content in enumerate(pdf_contents)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log errors
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Paper {i} processing failed with exception: {result}")
                processed_results.append({
                    'batch_index': i,
                    'error': str(result),
                    'processed_at': datetime.now().isoformat()
                })
            else:
                processed_results.append(result)

        success_count = sum(1 for r in processed_results if 'error' not in r)
        self.logger.info(f"Batch processing completed: {success_count}/{len(pdf_contents)} papers processed successfully")

        return processed_results

    async def _extract_text_from_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Extract text and metadata from PDF content

        Args:
            pdf_content: Raw PDF file content

        Returns:
            Dictionary with extracted text and metadata
        """
        # Validate file size
        if len(pdf_content) > self.max_file_size:
            raise Exception(f"PDF file too large: {len(pdf_content)} bytes (max: {self.max_file_size})")

        # Use PDFParser to extract content
        extracted_data = await asyncio.get_event_loop().run_in_executor(
            None,
            self.pdf_parser.extract_text_from_bytes,
            pdf_content
        )

        return extracted_data

    async def _analyze_paper_structure(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze paper structure and identify sections

        Args:
            paper_data: Dictionary containing paper content

        Returns:
            Dictionary with structure analysis results
        """
        content = paper_data.get('content', '')

        # Use structure analyzer to identify sections
        structure_analysis = await asyncio.get_event_loop().run_in_executor(
            None,
            self.structure_analyzer.analyze_structure,
            content
        )

        return structure_analysis

    async def _assess_paper_quality(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess paper quality across multiple criteria

        Args:
            paper_data: Dictionary containing paper content and structure

        Returns:
            Dictionary with quality assessment results
        """
        # Use quality assessor to evaluate paper
        quality_assessment = await asyncio.get_event_loop().run_in_executor(
            None,
            self.quality_assessor.assess_quality,
            paper_data
        )

        return quality_assessment

    async def _extract_key_findings(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key findings from paper content

        Args:
            paper_data: Dictionary containing paper content and structure

        Returns:
            Dictionary with extracted key findings
        """
        # Focus on results and discussion sections for finding extraction
        content = paper_data.get('content', '')
        structure = paper_data.get('structure', {})

        # Extract text from relevant sections
        results_text = structure.get('sections', {}).get('results', '')
        discussion_text = structure.get('sections', {}).get('discussion', '')
        conclusion_text = structure.get('sections', {}).get('conclusion', '')

        # Combine relevant sections for finding extraction
        findings_content = '\n'.join(filter(None, [results_text, discussion_text, conclusion_text]))

        if not findings_content:
            findings_content = content  # Fallback to full content

        # Use finding extractor to identify key findings
        key_findings = await asyncio.get_event_loop().run_in_executor(
            None,
            self.finding_extractor.extract_findings,
            findings_content
        )

        return key_findings

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats

        Returns:
            List of supported file format extensions
        """
        return self.supported_formats.copy()

    def get_processing_capabilities(self) -> Dict[str, Any]:
        """
        Get information about processing capabilities

        Returns:
            Dictionary describing processing capabilities
        """
        return {
            'max_file_size_mb': self.max_file_size // (1024 * 1024),
            'supported_formats': self.supported_formats,
            'analysis_features': [
                'text_extraction',
                'structure_recognition',
                'quality_assessment',
                'finding_extraction',
                'batch_processing'
            ],
            'parallel_processing': True,
            'error_recovery': True
        }

    def validate_input(self, pdf_content: bytes) -> bool:
        """
        Validate input PDF content

        Args:
            pdf_content: Raw PDF file content

        Returns:
            True if valid, False otherwise
        """
        # Basic validation checks
        if not pdf_content:
            return False

        if len(pdf_content) > self.max_file_size:
            return False

        # Check PDF header
        if not pdf_content.startswith(b'%PDF'):
            return False

        return True

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all components

        Returns:
            Dictionary with health status of components
        """
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }

        # Check each component
        try:
            # Test PDF parser
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.pdf_parser.get_version()
            )
            health_status['components']['pdf_parser'] = 'healthy'
        except Exception as e:
            health_status['components']['pdf_parser'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'

        try:
            # Test structure analyzer
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.structure_analyzer.get_supported_sections
            )
            health_status['components']['structure_analyzer'] = 'healthy'
        except Exception as e:
            health_status['components']['structure_analyzer'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'

        try:
            # Test quality assessor
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.quality_assessor.get_quality_criteria
            )
            health_status['components']['quality_assessor'] = 'healthy'
        except Exception as e:
            health_status['components']['quality_assessor'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'

        try:
            # Test finding extractor
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.finding_extractor.get_extraction_methods
            )
            health_status['components']['finding_extractor'] = 'healthy'
        except Exception as e:
            health_status['components']['finding_extractor'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'

        return health_status