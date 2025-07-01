"""Unit tests for TextProcessor class."""

import pytest
from cap_rate_analyzer.utils.text_processing import TextProcessor


class TestTextProcessor:
    """Test suite for TextProcessor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = TextProcessor()
    
    def test_clean_text_basic(self):
        """Test basic text cleaning functionality."""
        # Test normal text
        assert self.processor.clean_text("Hello World") == "Hello World"
        
        # Test empty text
        assert self.processor.clean_text("") == ""
        assert self.processor.clean_text(None) == ""
    
    def test_unicode_character_replacement(self):
        """Test Unicode character replacement."""
        # Test dash characters
        test_cases = [
            ("Hotel – Luxury", "Hotel - Luxury"),
            ("5.5%—6.0%", "5.5%-6.0%"),
            ("Cap Rate−Survey", "Cap Rate-Survey"),
        ]
        
        for input_text, expected in test_cases:
            result = self.processor.clean_text(input_text)
            assert result == expected, f"Expected '{expected}', got '{result}'"
    
    def test_quotation_mark_replacement(self):
        """Test quotation mark normalization."""
        test_cases = [
            ('"Hello World"', '"Hello World"'),
            ("'Test'", "'Test'"),
        ]
        
        for input_text, expected in test_cases:
            result = self.processor.clean_text(input_text)
            assert result == expected
    
    def test_whitespace_normalization(self):
        """Test whitespace normalization."""
        test_cases = [
            ("Hello    World", "Hello World"),
            ("Test\u00a0Space", "Test Space"),  # Non-breaking space
            ("Multiple\n\nLines", "Multiple Lines"),
        ]
        
        for input_text, expected in test_cases:
            result = self.processor.clean_text(input_text)
            assert result == expected
    
    def test_extract_numbers(self):
        """Test number extraction from text."""
        test_cases = [
            ("Cap rate: 5.5% - 6.0%", [5.5, 6.0]),
            ("No numbers here", []),
            ("123.45 and 67.89", [123.45, 67.89]),
            ("Single number: 42", [42.0]),
        ]
        
        for input_text, expected in test_cases:
            result = self.processor.extract_numbers(input_text)
            assert result == expected
    
    def test_extract_percentages(self):
        """Test percentage extraction from text."""
        test_cases = [
            ("Cap rate: 5.5%", [5.5]),
            ("Range: 4.5% - 6.0%", [4.5, 6.0]),
            ("No percentages", []),
            ("Multiple: 3.5%, 4.0%, 5.5%", [3.5, 4.0, 5.5]),
        ]
        
        for input_text, expected in test_cases:
            result = self.processor.extract_percentages(input_text)
            assert result == expected
    
    def test_normalize_market_name(self):
        """Test market name normalization."""
        test_cases = [
            ("atlanta", "Atlanta"),
            ("new york", "New York"),
            ("washington dc", "Washington DC"),
            ("st. louis", "St Louis"),
            ("", ""),
        ]
        
        for input_text, expected in test_cases:
            result = self.processor.normalize_market_name(input_text)
            assert result == expected
    
    def test_clean_punctuation(self):
        """Test punctuation cleaning."""
        test_cases = [
            ("Test!!!!", "Test!"),
            ("What???", "What?"),
            ("Normal text.", "Normal text."),
        ]
        
        for input_text, expected in test_cases:
            result = self.processor.clean_text(input_text)
            assert result == expected


class TestTextProcessorEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = TextProcessor()
    
    def test_very_long_text(self):
        """Test processing of very long text."""
        long_text = "A" * 10000
        result = self.processor.clean_text(long_text)
        assert len(result) == 10000
        assert result == long_text
    
    def test_special_unicode_characters(self):
        """Test handling of special Unicode characters."""
        # Test various Unicode categories
        text_with_unicode = "Test\u2028Line\u2029Paragraph\u00a0Space"
        result = self.processor.clean_text(text_with_unicode)
        # Should normalize to regular spaces and newlines
        assert "\u2028" not in result
        assert "\u2029" not in result
        assert "\u00a0" not in result
    
    def test_mixed_content(self):
        """Test processing of mixed content types."""
        mixed_text = 'Hotel – Luxury 5.5%—6.0% "Market Data" $1,000,000'
        result = self.processor.clean_text(mixed_text)
        
        # Should normalize dashes and quotes
        assert "–" not in result
        assert "—" not in result
        assert """ not in result
        assert """ not in result
    
    @pytest.mark.parametrize("input_text,expected_clean", [
        ("", ""),
        ("   ", ""),
        ("\n\n\n", ""),
        ("Test\t\tTab", "Test Tab"),
        ("Multiple   spaces", "Multiple spaces"),
    ])
    def test_whitespace_edge_cases(self, input_text, expected_clean):
        """Test various whitespace scenarios."""
        result = self.processor.clean_text(input_text)
        assert result == expected_clean 