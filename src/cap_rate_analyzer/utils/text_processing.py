"""Text processing utilities for PDF content cleaning and normalization."""

import re
import unicodedata
from typing import Dict, List


class TextProcessor:
    """Text processing utility for cleaning and normalizing PDF content."""
    
    def __init__(self):
        """Initialize text processor with cleaning patterns."""
        self._unicode_replacements = {
            # Various dash characters to ASCII hyphen
            '\u2013': '-',  # en dash
            '\u2014': '-',  # em dash
            '\u2212': '-',  # minus sign
            '\u2010': '-',  # hyphen
            '\u2011': '-',  # non-breaking hyphen
            
            # Quotation marks
            '\u201c': '"',  # left double quotation mark
            '\u201d': '"',  # right double quotation mark
            '\u2018': "'",  # left single quotation mark
            '\u2019': "'",  # right single quotation mark
            
            # Spaces
            '\u00a0': ' ',  # non-breaking space
            '\u2009': ' ',  # thin space
            '\u200a': ' ',  # hair space
            '\u2028': '\n', # line separator
            '\u2029': '\n', # paragraph separator
            
            # Other common characters
            '\u00ae': '(R)', # registered trademark
            '\u2122': '(TM)', # trademark
            '\u00a9': '(C)',  # copyright
        }
        
        # Compile regex patterns for efficiency
        self._whitespace_pattern = re.compile(r'\s+')
        self._special_chars_pattern = re.compile(r'[^\w\s\-\.\,\(\)%/&]')
        self._multiple_spaces_pattern = re.compile(r' {2,}')
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text from PDF extraction."""
        if not text:
            return ""
        
        # Replace Unicode characters
        cleaned = self._replace_unicode_chars(text)
        
        # Normalize Unicode to composed form
        cleaned = unicodedata.normalize('NFC', cleaned)
        
        # Remove control characters
        cleaned = self._remove_control_chars(cleaned)
        
        # Normalize whitespace
        cleaned = self._normalize_whitespace(cleaned)
        
        # Remove excessive punctuation
        cleaned = self._clean_punctuation(cleaned)
        
        return cleaned.strip()
    
    def _replace_unicode_chars(self, text: str) -> str:
        """Replace common Unicode characters with ASCII equivalents."""
        for unicode_char, replacement in self._unicode_replacements.items():
            text = text.replace(unicode_char, replacement)
        return text
    
    def _remove_control_chars(self, text: str) -> str:
        """Remove control characters except common whitespace."""
        # Keep newlines, tabs, and regular spaces
        return ''.join(char for char in text 
                      if not unicodedata.category(char).startswith('C') 
                      or char in '\n\t ')
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace characters."""
        # Replace multiple whitespace with single space
        text = self._whitespace_pattern.sub(' ', text)
        
        # Clean up multiple spaces
        text = self._multiple_spaces_pattern.sub(' ', text)
        
        return text
    
    def _clean_punctuation(self, text: str) -> str:
        """Clean excessive or problematic punctuation."""
        # Remove repeated punctuation (except periods for decimals)
        text = re.sub(r'([!?])\1+', r'\1', text)
        text = re.sub(r'([,;:])\1+', r'\1', text)
        
        # Clean up spacing around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([,.!?;:])\s+', r'\1 ', text)
        
        return text
    
    def extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values from text."""
        # Pattern to match numbers (including decimals and percentages)
        number_pattern = r'\d+\.?\d*'
        matches = re.findall(number_pattern, text)
        
        numbers = []
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
        
        return numbers
    
    def extract_percentages(self, text: str) -> List[float]:
        """Extract percentage values from text."""
        # Pattern to match percentages
        percentage_pattern = r'(\d+\.?\d*)%'
        matches = re.findall(percentage_pattern, text)
        
        percentages = []
        for match in matches:
            try:
                percentages.append(float(match))
            except ValueError:
                continue
        
        return percentages
    
    def normalize_market_name(self, market_name: str) -> str:
        """Normalize market/city names for consistency."""
        if not market_name:
            return ""
        
        # Clean the text first
        cleaned = self.clean_text(market_name)
        
        # Remove trailing dashes and whitespace
        cleaned = re.sub(r'[-\s]+$', '', cleaned)
        
        # Remove leading dashes and whitespace
        cleaned = re.sub(r'^[-\s]+', '', cleaned)
        
        # Fix common OCR errors in market names
        ocr_fixes = {
            # Common OCR misreads - use simple string replacements for better reliability
            'LAs Vegas': 'Las Vegas',
            'Las VegAs': 'Las Vegas', 
            'LAke': 'Lake',
            'Salt LAke City': 'Salt Lake City',
            'Salt LAke': 'Salt Lake',
            'Fort LAuderdale': 'Fort Lauderdale',
            'Ft LAuderdale': 'Fort Lauderdale',
            'LAuderdale': 'Lauderdale',
            'New YOrk': 'New York',
            'Los Angeles': 'Los Angeles',
            'San FrAncisco': 'San Francisco',
            'PhilAdElphia': 'Philadelphia',
            'WashIngton': 'Washington',
            'Southern CAlifornia': 'Southern California',
            
            # Standardize naming variations
            'Dallas/Ft Worth': 'Dallas',
            'Dallas/Fort Worth': 'Dallas', 
            'Minneapolis/St Paul': 'Minneapolis',
            'Minneapolis/Saint Paul': 'Minneapolis',
            'Tampa/St Petersburg': 'Tampa',
            'Miami/Fort Lauderdale': 'Miami',
            'Riverside/San Bernardino': 'Riverside',
        }
        
        # Apply simple string replacements first
        for old_text, new_text in ocr_fixes.items():
            cleaned = cleaned.replace(old_text, new_text)
        
        # Remove invalid entries with regex
        invalid_patterns = [
            r'^Market$',
            r'^Looking Forward To.*',
            r'^Figure.*',
            r'^After.*',
            r'^But fortune.*',
            r'^the$',
            r'^\d{4}$',  # Years
            r'^\d+%$',   # Percentages
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, cleaned, re.IGNORECASE):
                return ""
        
        # Skip if empty after cleaning
        if not cleaned.strip():
            return ""
        
        # Title case for proper names
        cleaned = cleaned.title()
        
        # Handle common abbreviations and special cases
        replacements = {
            'Dc': 'DC',
            'Nyc': 'NYC', 
            'Sf': 'SF',
            'St.': 'St',
            'Mt.': 'Mt',
            'Ft.': 'Ft',
            'Ft ': 'Fort ',
            ' Dc': ' DC',
            ' Ny': ' NY',
            ' Ca': ' CA',
            ' Tx': ' TX',
            ' Fl': ' FL',
        }
        
        # Handle LA specifically - only replace if it's Los Angeles, not Las Vegas
        if cleaned == 'Los Angeles':
            cleaned = 'Los Angeles'  # Already correct
        elif cleaned.startswith('La ') and 'Vegas' not in cleaned:
            cleaned = cleaned.replace('La ', 'LA ', 1)  # Only first occurrence
        elif cleaned.endswith(' La') and 'Vegas' not in cleaned:
            cleaned = cleaned.replace(' La', ' LA')
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Final validation - must be at least 3 characters and look like a city name
        if len(cleaned) < 3 or cleaned.isdigit():
            return ""
        
        return cleaned.strip() 