"""
PDF Text Extraction and Parsing System
Implements PDF text extraction capabilities with error handling and metadata extraction
"""

import logging
import tempfile
import os
from typing import Dict, Any, List, Optional
from io import BytesIO

# Try to import PyPDF2, handle if not available
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logging.warning("PyPDF2 not available. PDF parsing will be disabled.")

try:
    import pypdf2
    PYPDF2_V3_AVAILABLE = True
except ImportError:
    PYPDF2_V3_AVAILABLE = False


class PDFParser:
    """
    PDF text extraction and parsing with comprehensive error handling

    Features:
    - Text extraction from PDF files
    - Metadata extraction (title, author, creation date)
    - Encryption handling
    - Error recovery for corrupted files
    - Page-by-page processing
    """

    def __init__(self):
        """Initialize PDF parser"""
        self.logger = logging.getLogger(__name__)
        self.max_pages = 1000  # Prevent memory issues with very large PDFs
        self.min_text_length = 10  # Minimum characters to consider a page valid

        if not PYPDF2_AVAILABLE:
            self.logger.error("PyPDF2 is required for PDF parsing but is not installed")

    def extract_text_from_bytes(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Extract text and metadata from PDF content bytes

        Args:
            pdf_content: Raw PDF file content as bytes

        Returns:
            Dictionary containing:
            - content: Extracted text content
            - pages: List of page-by-page text
            - metadata: PDF metadata dictionary
            - page_count: Number of pages processed

        Raises:
            Exception: If PDF parsing fails
        """
        if not PYPDF2_AVAILABLE:
            raise Exception("PyPDF2 is not available for PDF parsing")

        # Create temporary file for PyPDF2 processing
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(pdf_content)
            tmp_file.flush()

            try:
                return self.extract_text(tmp_file.name)
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file.name)
                except OSError:
                    pass

    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text and metadata from PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary with extracted content and metadata
        """
        if not PYPDF2_AVAILABLE:
            raise Exception("PyPDF2 is not available for PDF parsing")

        if not os.path.exists(file_path):
            raise Exception(f"PDF file not found: {file_path}")

        try:
            # Read PDF file
            with open(file_path, 'rb') as file:
                pdf_reader = self._create_pdf_reader(file)

                # Handle encryption
                if pdf_reader.is_encrypted:
                    if not self._handle_encryption(pdf_reader):
                        raise Exception("Encrypted PDF - password required or decryption failed")

                # Extract metadata
                metadata = self._extract_metadata(pdf_reader)

                # Extract text from all pages
                pages_text = self._extract_pages_text(pdf_reader)
                full_content = '\n\n'.join(pages_text)

                return {
                    'content': full_content,
                    'pages': pages_text,
                    'metadata': metadata,
                    'page_count': len(pages_text),
                    'extraction_method': 'PyPDF2'
                }

        except Exception as e:
            self.logger.error(f"Failed to extract text from PDF {file_path}: {str(e)}")
            raise Exception(f"PDF text extraction failed: {str(e)}")

    def _create_pdf_reader(self, file_obj) -> 'PyPDF2.PdfReader':
        """
        Create PDF reader object with fallback for different PyPDF2 versions

        Args:
            file_obj: File-like object containing PDF data

        Returns:
            PdfReader object
        """
        try:
            # Try PyPDF2 v3+ interface first
            if PYPDF2_V3_AVAILABLE:
                return pypdf2.PdfReader(file_obj)
            else:
                return PyPDF2.PdfReader(file_obj)
        except Exception as e:
            self.logger.error(f"Failed to create PDF reader: {str(e)}")
            raise Exception(f"PDF reader creation failed: {str(e)}")

    def _handle_encryption(self, pdf_reader) -> bool:
        """
        Handle encrypted PDF files

        Args:
            pdf_reader: PdfReader object

        Returns:
            True if decryption successful, False otherwise
        """
        try:
            # Try common passwords
            common_passwords = ['', 'password', 'admin', '123456']

            for password in common_passwords:
                if pdf_reader.decrypt(password):
                    self.logger.info(f"PDF decrypted with password: '{password}'")
                    return True

            self.logger.warning("PDF is encrypted and could not be decrypted")
            return False

        except Exception as e:
            self.logger.error(f"Error handling PDF encryption: {str(e)}")
            return False

    def _extract_metadata(self, pdf_reader) -> Dict[str, Any]:
        """
        Extract metadata from PDF

        Args:
            pdf_reader: PdfReader object

        Returns:
            Dictionary with PDF metadata
        """
        metadata = {}

        try:
            if hasattr(pdf_reader, 'metadata') and pdf_reader.metadata:
                pdf_metadata = pdf_reader.metadata

                # Extract common metadata fields
                metadata = {
                    'title': self._clean_metadata_string(pdf_metadata.get('/Title', '')),
                    'author': self._clean_metadata_string(pdf_metadata.get('/Author', '')),
                    'subject': self._clean_metadata_string(pdf_metadata.get('/Subject', '')),
                    'creator': self._clean_metadata_string(pdf_metadata.get('/Creator', '')),
                    'producer': self._clean_metadata_string(pdf_metadata.get('/Producer', '')),
                    'creation_date': self._parse_date(pdf_metadata.get('/CreationDate')),
                    'modification_date': self._parse_date(pdf_metadata.get('/ModDate')),
                }

            # Add page count
            metadata['page_count'] = len(pdf_reader.pages)

        except Exception as e:
            self.logger.warning(f"Failed to extract PDF metadata: {str(e)}")
            metadata = {'page_count': len(pdf_reader.pages) if hasattr(pdf_reader, 'pages') else 0}

        return metadata

    def _extract_pages_text(self, pdf_reader) -> List[str]:
        """
        Extract text from individual pages

        Args:
            pdf_reader: PdfReader object

        Returns:
            List of text content for each page
        """
        pages_text = []
        page_count = min(len(pdf_reader.pages), self.max_pages)

        for page_num in range(page_count):
            try:
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                # Clean and validate page text
                cleaned_text = self._clean_page_text(text)

                if len(cleaned_text) >= self.min_text_length:
                    pages_text.append(cleaned_text)
                else:
                    self.logger.debug(f"Page {page_num + 1} has insufficient text, skipping")

            except Exception as e:
                self.logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
                pages_text.append(f"[Page {page_num + 1}: Text extraction failed]")

        return pages_text

    def _clean_page_text(self, text: str) -> str:
        """
        Clean and normalize extracted page text

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        cleaned = ' '.join(text.split())

        # Remove common PDF artifacts
        artifacts = [
            '\x00',  # Null bytes
            '\x0c',  # Form feed
            '\x0b',  # Vertical tab
        ]

        for artifact in artifacts:
            cleaned = cleaned.replace(artifact, '')

        return cleaned.strip()

    def _clean_metadata_string(self, value: Any) -> str:
        """
        Clean metadata string values

        Args:
            value: Raw metadata value

        Returns:
            Cleaned string
        """
        if value is None:
            return ""

        # Handle different data types
        if isinstance(value, str):
            return value.strip()
        elif hasattr(value, 'get'):
            return str(value.get('content', '')).strip()
        else:
            return str(value).strip()

    def _parse_date(self, date_obj: Any) -> Optional[str]:
        """
        Parse PDF date object

        Args:
            date_obj: PDF date object

        Returns:
            ISO formatted date string or None
        """
        if not date_obj:
            return None

        try:
            # Handle PyPDF2 date objects
            if hasattr(date_obj, 'get'):
                date_str = date_obj.get('content', '')
            else:
                date_str = str(date_obj)

            # Convert to standard format (basic implementation)
            if date_str.startswith('D:'):
                date_str = date_str[2:]

            return date_str.strip()

        except Exception as e:
            self.logger.warning(f"Failed to parse PDF date {date_obj}: {str(e)}")
            return None

    def validate_pdf_file(self, file_path: str) -> bool:
        """
        Validate that file is a valid PDF

        Args:
            file_path: Path to file to validate

        Returns:
            True if valid PDF, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                return False

            with open(file_path, 'rb') as file:
                header = file.read(4)
                return header == b'%PDF'

        except Exception as e:
            self.logger.error(f"PDF validation failed for {file_path}: {str(e)}")
            return False

    def get_pdf_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic information about PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary with PDF information
        """
        try:
            file_size = os.path.getsize(file_path)

            with open(file_path, 'rb') as file:
                pdf_reader = self._create_pdf_reader(file)
                page_count = len(pdf_reader.pages)
                is_encrypted = pdf_reader.is_encrypted

                metadata = self._extract_metadata(pdf_reader)

            return {
                'file_path': file_path,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'page_count': page_count,
                'is_encrypted': is_encrypted,
                'has_metadata': bool(metadata.get('title') or metadata.get('author')),
                'metadata': metadata
            }

        except Exception as e:
            self.logger.error(f"Failed to get PDF info for {file_path}: {str(e)}")
            return {
                'file_path': file_path,
                'error': str(e),
                'file_size_bytes': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }

    def get_version(self) -> str:
        """
        Get PDF parser version information

        Returns:
            Version string
        """
        if PYPDF2_AVAILABLE:
            try:
                if PYPDF2_V3_AVAILABLE:
                    return f"PyPDF2 v3+ ({pypdf2.__version__})"
                else:
                    return f"PyPDF2 v2.x ({PyPDF2.__version__})"
            except:
                return "PyPDF2 (version unknown)"
        else:
            return "PyPDF2 not available"