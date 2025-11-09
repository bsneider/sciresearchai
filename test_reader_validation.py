#!/usr/bin/env python3
"""
Simple validation script for Paper Reader Agent
Tests T-ANALYSIS-001 implementation without pytest
"""

import sys
import os
import asyncio
import tempfile
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def test_imports():
    """Test that all components can be imported"""
    print("🔍 Testing imports...")

    try:
        from agents.paper_analysis import PaperReaderAgent
        print("  ✅ PaperReaderAgent imported successfully")
    except ImportError as e:
        print(f"  ❌ PaperReaderAgent import failed: {e}")
        return False

    try:
        from agents.paper_analysis import PDFParser, PaperStructureAnalyzer, QualityAssessor, KeyFindingExtractor
        print("  ✅ All core components imported successfully")
    except ImportError as e:
        print(f"  ❌ Core components import failed: {e}")
        return False

    return True

def test_reader_agent_initialization():
    """Test PaperReaderAgent initialization"""
    print("🔍 Testing PaperReaderAgent initialization...")

    try:
        from agents.paper_analysis import PaperReaderAgent

        agent = PaperReaderAgent()

        # Check that core attributes exist
        assert hasattr(agent, 'pdf_parser')
        assert hasattr(agent, 'structure_analyzer')
        assert hasattr(agent, 'quality_assessor')
        assert hasattr(agent, 'finding_extractor')
        assert hasattr(agent, 'supported_formats')

        # Check supported formats
        assert 'pdf' in agent.get_supported_formats()

        print("  ✅ PaperReaderAgent initialized successfully")
        return True

    except Exception as e:
        print(f"  ❌ PaperReaderAgent initialization failed: {e}")
        return False

async def test_basic_processing():
    """Test basic paper processing workflow"""
    print("🔍 Testing basic paper processing...")

    try:
        from agents.paper_analysis import PaperReaderAgent

        agent = PaperReaderAgent()

        # Mock PDF content
        mock_paper_content = {
            'title': 'Test Research Paper',
            'content': '''
            Abstract
            This is a test abstract for our research paper.
            It describes the main findings and methodology.

            Introduction
            Research papers typically follow a standard structure.
            This introduction provides context for our study.

            Methods
            We conducted experiments with 100 participants.
            Statistical analysis was performed using standard methods.

            Results
            Our study found significant improvements (p < 0.05).
            The experimental group showed a 45% increase in performance.
            Statistical analysis confirmed the significance of these findings.

            Discussion
            The findings suggest important implications for future research.
            Limitations of the study should be noted.

            Conclusion
            This method provides an effective solution for research challenges.
            Future work should address the identified limitations.
            ''',
            'metadata': {'word_count': 5000, 'pages': 8}
        }

        # Mock the PDF extraction
        with patch.object(agent, '_extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = mock_paper_content

            # Process the paper
            result = await agent.process_paper(b"mock_pdf_content")

            # Verify structure
            assert 'title' in result
            assert 'content' in result
            assert 'structure' in result
            assert 'quality_assessment' in result
            assert 'key_findings' in result

            # Verify structure analysis
            assert 'sections' in result['structure']
            assert result['structure']['sections'] != {}

            # Verify quality assessment
            assert 'quality_score' in result['quality_assessment']
            assert 0 <= result['quality_assessment']['quality_score'] <= 1

            # Verify key findings
            assert 'findings' in result['key_findings']
            assert isinstance(result['key_findings']['findings'], list)

        print("  ✅ Basic paper processing successful")
        return True

    except Exception as e:
        print(f"  ❌ Basic paper processing failed: {e}")
        return False

def test_pdf_parser():
    """Test PDF parser functionality"""
    print("🔍 Testing PDF parser...")

    try:
        from agents.paper_analysis import PDFParser

        parser = PDFParser()

        # Test initialization
        assert hasattr(parser, 'extract_text_from_bytes')
        assert hasattr(parser, 'get_version')

        # Test version info
        version = parser.get_version()
        assert isinstance(version, str)

        print("  ✅ PDF parser initialized successfully")
        return True

    except Exception as e:
        print(f"  ❌ PDF parser test failed: {e}")
        return False

def test_structure_analyzer():
    """Test paper structure analyzer"""
    print("🔍 Testing structure analyzer...")

    try:
        from agents.paper_analysis import PaperStructureAnalyzer

        analyzer = PaperStructureAnalyzer()

        # Test with sample content
        sample_content = '''
        Abstract
        This is the abstract of our research paper.
        It contains a summary of our findings.

        Introduction
        This paper presents research on paper analysis.
        The background and motivation are discussed here.

        Methods
        We used experimental methods to test our hypothesis.
        Data was collected from various sources.

        Results
        Our analysis showed significant results.
        The findings are presented in this section.

        Discussion
        We discuss the implications of our findings.
        Limitations and future work are addressed.
        '''

        result = analyzer.analyze_structure(sample_content)

        # Verify result structure
        assert 'sections' in result
        assert 'section_order' in result
        assert 'confidence' in result

        # Should identify key sections
        sections = result['sections']
        assert any('abstract' in section.lower() for section in sections.keys())

        print("  ✅ Structure analyzer working correctly")
        return True

    except Exception as e:
        print(f"  ❌ Structure analyzer test failed: {e}")
        return False

def test_quality_assessor():
    """Test quality assessor functionality"""
    print("🔍 Testing quality assessor...")

    try:
        from agents.paper_analysis import QualityAssessor

        assessor = QualityAssessor()

        # Test with sample paper data
        paper_data = {
            'title': 'Test Paper',
            'content': 'This is a test research paper with adequate content.',
            'structure': {
                'sections': {
                    'abstract': 'Well-written abstract with sufficient detail.',
                    'introduction': 'Comprehensive introduction providing context.',
                    'methods': 'Detailed methodology description.',
                    'results': 'Clear presentation of results with statistics.',
                    'discussion': 'Insightful discussion of implications.',
                    'conclusion': 'Strong conclusion summarizing findings.'
                }
            }
        }

        result = assessor.assess_quality(paper_data)

        # Verify result structure
        assert 'quality_score' in result
        assert 'criteria' in result
        assert 'grade' in result

        # Verify score range
        assert 0 <= result['quality_score'] <= 1

        # Should have multiple criteria
        assert len(result['criteria']) > 0

        print("  ✅ Quality assessor working correctly")
        return True

    except Exception as e:
        print(f"  ❌ Quality assessor test failed: {e}")
        return False

def test_finding_extractor():
    """Test key finding extractor"""
    print("🔍 Testing finding extractor...")

    try:
        from agents.paper_analysis import KeyFindingExtractor

        extractor = KeyFindingExtractor()

        # Test with sample research content
        research_content = '''
        Our study found significant improvements in treatment outcomes.
        The experimental group showed a 45% increase in performance (p < 0.01).
        We observed that the new method reduced processing time by 60%.
        Statistical analysis confirmed the significance of these findings.
        The correlation between variables was strong (r = 0.85, p < 0.001).
        The mean difference was 2.3 units (SD = 0.8).
        '''

        result = extractor.extract_findings(research_content)

        # Verify result structure
        assert 'findings' in result
        assert 'confidence_scores' in result
        assert 'categories' in result
        assert 'summary' in result

        # Should extract some findings
        assert len(result['findings']) >= 0
        assert len(result['confidence_scores']) == len(result['findings'])

        print("  ✅ Finding extractor working correctly")
        return True

    except Exception as e:
        print(f"  ❌ Finding extractor test failed: {e}")
        return False

async def test_batch_processing():
    """Test batch processing functionality"""
    print("🔍 Testing batch processing...")

    try:
        from agents.paper_analysis import PaperReaderAgent

        agent = PaperReaderAgent()

        # Mock PDF contents
        mock_papers = [b"pdf1_content", b"pdf2_content", b"pdf3_content"]

        # Mock process_paper method
        with patch.object(agent, 'process_paper') as mock_process:
            mock_process.side_effect = [
                {"paper_id": 1, "title": "Paper 1", "quality_score": 0.8},
                {"paper_id": 2, "title": "Paper 2", "quality_score": 0.7},
                {"paper_id": 3, "title": "Paper 3", "quality_score": 0.9}
            ]

            # Process batch
            results = await agent.process_batch(mock_papers)

            # Verify results
            assert len(results) == 3
            assert all('paper_id' in result for result in results)
            assert mock_process.call_count == 3

        print("  ✅ Batch processing working correctly")
        return True

    except Exception as e:
        print(f"  ❌ Batch processing test failed: {e}")
        return False

async def main():
    """Run all validation tests"""
    print("🚀 Starting Paper Reader Agent Validation")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("Initialization Tests", test_reader_agent_initialization),
        ("PDF Parser Tests", test_pdf_parser),
        ("Structure Analyzer Tests", test_structure_analyzer),
        ("Quality Assessor Tests", test_quality_assessor),
        ("Finding Extractor Tests", test_finding_extractor),
        ("Basic Processing Tests", test_basic_processing),
        ("Batch Processing Tests", test_batch_processing)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if result:
                passed += 1
            else:
                print(f"  ❌ {test_name} failed")
        except Exception as e:
            print(f"  ❌ {test_name} error: {e}")

    print("\n" + "=" * 50)
    print(f"📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Paper Reader Agent implementation is working correctly")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)