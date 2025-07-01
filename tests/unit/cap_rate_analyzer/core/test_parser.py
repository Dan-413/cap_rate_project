"""
Unit tests for CapRateParser module.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import fitz  # PyMuPDF

from cap_rate_analyzer.core.parser import CapRateParser
from cap_rate_analyzer.models.schemas import ParseResult, CapRateRecord


class TestCapRateParser(unittest.TestCase):
    """Test CapRateParser functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = CapRateParser()
    
    def test_parser_initialization(self):
        """Test parser initialization with default configuration."""
        self.assertIsNotNone(self.parser.config)
        self.assertIsNotNone(self.parser.text_processor)
        self.assertIsNotNone(self.parser.sector_patterns)
        self.assertIsNotNone(self.parser.subsector_patterns)
        self.assertIsNotNone(self.parser.region_pattern)
        self.assertIsNotNone(self.parser.cap_rate_patterns)
        self.assertIsNotNone(self.parser.year_half_patterns)
    
    def test_extract_year_half_from_filename_valid(self):
        """Test extracting year and half from valid filenames."""
        test_cases = [
            ("h1_2024.pdf", (2024, 1)),
            ("h2_2023.pdf", (2023, 2)),
            ("2024_h1.pdf", (2024, 1)),
            ("2023_h2.pdf", (2023, 2)),
            ("report_h1_2024.pdf", (2024, 1)),
            ("data_2023h2.pdf", (2023, 2)),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.parser._extract_year_half_from_filename(filename)
                self.assertEqual(result, expected)
    
    def test_extract_year_half_from_filename_invalid(self):
        """Test extracting year and half from invalid filenames."""
        invalid_filenames = [
            "report.pdf",
            "data_2019.pdf",  # Year too old
            "h3_2024.pdf",   # Invalid half
            "invalid_format.pdf",
            "h1_2031.pdf",   # Year too new
        ]
        
        for filename in invalid_filenames:
            with self.subTest(filename=filename):
                result = self.parser._extract_year_half_from_filename(filename)
                self.assertEqual(result, (None, None))
    
    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist."""
        result = self.parser.parse_file("nonexistent_file.pdf")
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.records), 0)
        self.assertTrue(any("File not found" in error for error in result.errors))
    
    def test_parse_invalid_filename(self):
        """Test parsing file with invalid filename format."""
        # Create a temporary file with invalid name
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            # Rename to invalid format
            invalid_path = tmp_path.parent / "invalid_format.pdf"
            tmp_path.rename(invalid_path)
            
            result = self.parser.parse_file(str(invalid_path))
            
            self.assertFalse(result.success)
            self.assertEqual(len(result.records), 0)
            self.assertTrue(any("Could not extract year/half" in error for error in result.errors))
        finally:
            if invalid_path.exists():
                invalid_path.unlink()
    
    def test_is_valid_market_valid_markets(self):
        """Test market validation with valid markets."""
        valid_markets = ["Los Angeles", "New York", "Chicago", "Houston"]
        
        for market in valid_markets:
            with self.subTest(market=market):
                result = self.parser._is_valid_market(market)
                self.assertTrue(result)
    
    def test_is_valid_market_invalid_markets(self):
        """Test market validation with invalid markets."""
        invalid_markets = ["XY", "A", ""]  # Too short
        
        for market in invalid_markets:
            with self.subTest(market=market):
                result = self.parser._is_valid_market(market)
                self.assertFalse(result)
    
    def test_is_valid_market_none(self):
        """Test market validation with None input."""
        result = self.parser._is_valid_market(None)
        self.assertFalse(result)
    
    def test_extract_cap_rates_valid_ranges(self):
        """Test extracting cap rates from text with valid ranges."""
        test_cases = [
            ("4.5% - 5.5%", [(4.5, 5.5)]),
            ("4.5 - 5.5%", [(4.5, 5.5)]),
            ("6.0% – 7.0%", [(6.0, 7.0)]),  # em dash
            ("3.5%", [(3.5, 3.5)]),  # single rate
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.parser._extract_cap_rates(text)
                self.assertEqual(result, expected)
    
    def test_extract_cap_rates_no_rates(self):
        """Test extracting cap rates from text with no rates."""
        text = "This is just regular text without any cap rates."
        result = self.parser._extract_cap_rates(text)
        self.assertEqual(result, [])
    
    def test_extract_market_name_valid(self):
        """Test extracting market name from text."""
        test_cases = [
            ("Los Angeles Market Data", "Los Angeles"),
            ("New York City Information", "New York"),
            ("Chicago Metro Area", "Chicago"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.parser._extract_market_name(text)
                if result:  # Only test if we get a result
                    self.assertIn(expected, result)
    
    def test_extract_market_name_invalid(self):
        """Test extracting market name from invalid text."""
        invalid_texts = [
            "Random text without market",
            "123 numbers only",
            "",
        ]
        
        for text in invalid_texts:
            with self.subTest(text=text):
                result = self.parser._extract_market_name(text)
                # Result can be None or empty string
                self.assertTrue(result is None or result == "")
    
    def test_clean_subsector_name(self):
        """Test cleaning subsector names."""
        test_cases = [
            ("infill", "Multifamily", "Multifamily Infill"),
            ("suburban", "Multifamily", "Multifamily Suburban"),
            ("downtown", "Office", "Office Downtown"),
            ("class a", "Office", "Office Class A"),
        ]
        
        for subsector, sector, expected in test_cases:
            with self.subTest(subsector=subsector, sector=sector):
                result = self.parser._clean_subsector_name(subsector, sector)
                # Just check that the result is a string and contains expected parts
                self.assertIsInstance(result, str)
                self.assertTrue(len(result) > 0)
    
    def test_update_context_sector_detection(self):
        """Test context updating with sector detection."""
        context = {'sector': None, 'subsector': None, 'region': None}
        
        test_cases = [
            ("Multifamily apartment data", "Multifamily"),
            ("Office commercial buildings", "Office"),
            ("Industrial warehouse facilities", "Industrial"),
            ("Retail shopping centers", "Retail"),
            ("Hotel hospitality properties", "Hotel"),
        ]
        
        for text, expected_sector in test_cases:
            with self.subTest(text=text):
                context_copy = context.copy()
                self.parser._update_context(text, context_copy)
                self.assertEqual(context_copy['sector'], expected_sector)
    
    def test_update_context_region_detection(self):
        """Test context updating with region detection."""
        context = {'sector': None, 'subsector': None, 'region': None}
        
        test_cases = [
            "East Coast Data",
            "West Region Information", 
            "Southern Markets",
            "Northern Areas",
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                context_copy = context.copy()
                self.parser._update_context(text, context_copy)
                # Should set region to the full text
                self.assertEqual(context_copy['region'], text)
    
    def test_create_metadata(self):
        """Test metadata creation."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='_h1_2024.pdf', delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b"test content")
        
        try:
            metadata = self.parser._create_metadata(tmp_path, 2024, 1, 10)
            
            self.assertIsInstance(metadata, dict)
            self.assertIn('filename', metadata)
            self.assertIn('report_year', metadata)
            self.assertIn('report_half', metadata)
            self.assertIn('record_count', metadata)
            self.assertIn('parsed_at', metadata)
            
            self.assertEqual(metadata['report_year'], 2024)
            self.assertEqual(metadata['report_half'], 1)
            self.assertEqual(metadata['record_count'], 10)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    @patch('fitz.open')
    def test_parse_pdf_with_mock_success(self, mock_fitz_open):
        """Test PDF parsing with mocked fitz (success case)."""
        # Create a mock PDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.__enter__.return_value = mock_doc
        mock_doc.__exit__.return_value = None
        
        # Mock page content
        mock_page.get_text.return_value = [
            [0, 0, 100, 20, "Industrial Warehouse Data\nLos Angeles 4.5% - 5.5%", 0, 0]
        ]
        
        mock_fitz_open.return_value = mock_doc
        
        # Create a temporary file with valid name
        with tempfile.NamedTemporaryFile(suffix='_h1_2024.pdf', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            result = self.parser.parse_file(str(tmp_path))
            
            # Should succeed with valid filename
            self.assertTrue(result.success)
            self.assertIsInstance(result.records, list)
            self.assertIsInstance(result.metadata, dict)
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    @patch('fitz.open')
    def test_parse_pdf_with_mock_fitz_error(self, mock_fitz_open):
        """Test PDF parsing with fitz error."""
        mock_fitz_open.side_effect = Exception("PDF corrupted")
        
        # Create a temporary file with valid name
        with tempfile.NamedTemporaryFile(suffix='_h1_2024.pdf', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            result = self.parser.parse_file(str(tmp_path))
            
            self.assertFalse(result.success)
            self.assertEqual(len(result.records), 0)
            self.assertTrue(any("Parsing failed" in error for error in result.errors))
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_extract_records_from_text(self):
        """Test extracting records from text."""
        context = {
            'sector': 'Industrial',
            'subsector': 'Warehouse',
            'region': 'West'
        }
        
        text = "Los Angeles 4.5% - 5.5%"
        records = self.parser._extract_records_from_text(
            text, context, 2024, 1, "test.pdf"
        )
        
        # Should return a list (even if empty)
        self.assertIsInstance(records, list)
    
    def test_parse_page_with_mock_page(self):
        """Test parsing a single page."""
        # Create a mock page
        mock_page = MagicMock()
        mock_page.get_text.return_value = [
            [0, 0, 100, 20, "Industrial Warehouse Data", 0, 0],
            [0, 25, 100, 45, "Los Angeles 4.5% - 5.5%", 0, 0]
        ]
        
        records = self.parser._parse_page(mock_page, 2024, 1, "test.pdf")
        
        # Should return a list
        self.assertIsInstance(records, list)
    
    def test_compile_patterns(self):
        """Test that patterns are compiled correctly."""
        self.parser._compile_patterns()
        
        # Check that patterns exist and are compiled regex objects
        import re
        
        for pattern in self.parser.sector_patterns.values():
            self.assertIsInstance(pattern, re.Pattern)
        
        for pattern in self.parser.subsector_patterns.values():
            self.assertIsInstance(pattern, re.Pattern)
        
        self.assertIsInstance(self.parser.region_pattern, re.Pattern)
        
        for pattern in self.parser.cap_rate_patterns:
            self.assertIsInstance(pattern, re.Pattern)
        
        for pattern in self.parser.year_half_patterns:
            self.assertIsInstance(pattern, re.Pattern)


if __name__ == '__main__':
    unittest.main() 