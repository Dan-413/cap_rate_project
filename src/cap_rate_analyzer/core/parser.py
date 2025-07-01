"""Enhanced PDF parser for cap rate reports."""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import pandas as pd

from ..models.schemas import CapRateRecord, ParseResult
from ..utils.text_processing import TextProcessor
from ..utils.config import get_config


class CapRateParser:
    """Enhanced cap rate parser for semi-annual reports."""
    
    def __init__(self):
        """Initialize the parser."""
        self.config = get_config()
        self.text_processor = TextProcessor()
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for performance."""
        self.sector_patterns = {
            'Multifamily': re.compile(r'multifamily|apartment|residential', re.IGNORECASE),
            'Office': re.compile(r'office|commercial', re.IGNORECASE),
            'Industrial': re.compile(r'industrial|warehouse|logistics', re.IGNORECASE),
            'Retail': re.compile(r'retail|shopping|strip', re.IGNORECASE),
            'Hotel': re.compile(r'hotel|hospitality|lodging', re.IGNORECASE)
        }
        
        self.subsector_patterns = {
            'Multifamily': re.compile(r'(infill|suburban|class\s*[ab]|luxury|affordable)', re.IGNORECASE),
            'Office': re.compile(r'(downtown|suburban|cbd|class\s*[ab])', re.IGNORECASE),
            'Hotel': re.compile(r'(luxury|destination\s*resort|city\s*center|limited\s*service|full\s*service)', re.IGNORECASE)
        }
        
        self.region_pattern = re.compile(
            r'(east|west|south|north|midwest|central|northeast|southeast|southwest|northwest)', 
            re.IGNORECASE
        )
        
        self.cap_rate_patterns = [
            re.compile(r'(\d+\.?\d*)%?\s*[-–—]\s*(\d+\.?\d*)%?'),
            re.compile(r'(\d+\.?\d*)\s*[-–—]\s*(\d+\.?\d*)%'),
            re.compile(r'(\d+\.?\d*)%'),
        ]
        
        self.year_half_patterns = [
            re.compile(r'[hH]([12])[\s_\-]*(\d{4})', re.IGNORECASE),
            re.compile(r'(\d{4})[\s_\-]*[hH]([12])', re.IGNORECASE),
            re.compile(r'[hH]([12])[\s_\-]+(\d{4})', re.IGNORECASE),
            re.compile(r'(\d{4})[hH]([12])', re.IGNORECASE),
        ]
    
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse a PDF file and return structured data."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return ParseResult(
                records=[], 
                metadata={},
                success=False,
                errors=[f"File not found: {file_path}"]
            )
        
        try:
            # Extract year and half from filename
            year, half = self._extract_year_half_from_filename(str(file_path))
            if not year or not half:
                return ParseResult(
                    records=[],
                    metadata={},
                    success=False,
                    errors=[f"Could not extract year/half from filename: {file_path.name}"]
                )
            
            # Parse PDF content
            records = self._parse_pdf_content(file_path, year, half)
            
            # Create metadata
            metadata = self._create_metadata(file_path, year, half, len(records))
            
            return ParseResult(
                records=records,
                metadata=metadata,
                success=True
            )
            
        except Exception as e:
            return ParseResult(
                records=[],
                metadata={},
                success=False,
                errors=[f"Parsing failed: {str(e)}"]
            )
    
    def _extract_year_half_from_filename(self, filename: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract year and half from filename."""
        filename = Path(filename).stem
        
        for pattern in self.year_half_patterns:
            match = pattern.search(filename)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    try:
                        if len(groups[0]) == 4:  # Year first
                            year = int(groups[0])
                            half = int(groups[1]) if groups[1] in ['1', '2'] else None
                        else:  # Half first
                            half = int(groups[0]) if groups[0] in ['1', '2'] else None
                            year = int(groups[1])
                        
                        if year and 2000 <= year <= 2030 and half in [1, 2]:
                            return year, half
                    except ValueError:
                        continue
        
        return None, None
    
    def _parse_pdf_content(self, file_path: Path, year: int, half: int) -> List[CapRateRecord]:
        """Parse PDF content and extract cap rate data."""
        doc = fitz.open(str(file_path))
        records = []
        
        try:
            for page_num in range(len(doc)):
                page_records = self._parse_page(doc[page_num], year, half, str(file_path))
                records.extend(page_records)
        finally:
            doc.close()
        
        return records
    
    def _parse_page(self, page, year: int, half: int, source_file: str) -> List[CapRateRecord]:
        """Parse a single page and extract records."""
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[1], b[0]))  # Sort by position
        
        records = []
        current_context = {
            'sector': None,
            'subsector': None,
            'region': None
        }
        
        for block in blocks:
            text = block[4].strip()
            if not text:
                continue
            
            # Clean text
            cleaned_text = self.text_processor.clean_text(text)
            
            # Update context
            self._update_context(cleaned_text, current_context)
            
            # Extract records
            page_records = self._extract_records_from_text(
                cleaned_text, current_context, year, half, source_file
            )
            records.extend(page_records)
        
        return records
    
    def _update_context(self, text: str, context: Dict) -> None:
        """Update parsing context based on text."""
        # Check for sector
        for sector_name, pattern in self.sector_patterns.items():
            if pattern.search(text):
                context['sector'] = sector_name
                context['subsector'] = None  # Reset subsector
                break
        
        # Check for subsector
        if context['sector'] and context['sector'] in self.subsector_patterns:
            match = self.subsector_patterns[context['sector']].search(text)
            if match:
                context['subsector'] = self._clean_subsector_name(
                    match.group(0), context['sector']
                )
        
        # Check for region
        if self.region_pattern.search(text):
            context['region'] = text.strip()
    
    def _clean_subsector_name(self, subsector: str, sector: str) -> str:
        """Clean and standardize subsector names."""
        subsector = subsector.strip().title()
        
        # Sector-specific cleaning
        if sector == 'Multifamily':
            if 'infill' in subsector.lower():
                return 'Multifamily Infill'
            elif 'suburban' in subsector.lower():
                return 'Multifamily Suburban'
        elif sector == 'Office':
            if 'downtown' in subsector.lower() or 'cbd' in subsector.lower():
                return 'Office Downtown'
            elif 'suburban' in subsector.lower():
                return 'Office Suburban'
        elif sector == 'Hotel':
            if 'luxury' in subsector.lower():
                return 'Hotel - Luxury'
            elif 'destination' in subsector.lower():
                return 'Hotel - Destination Resort'
            elif 'city' in subsector.lower():
                return 'Hotel - City Center'
        
        return subsector
    
    def _extract_records_from_text(
        self, 
        text: str, 
        context: Dict, 
        year: int, 
        half: int, 
        source_file: str
    ) -> List[CapRateRecord]:
        """Extract cap rate records from text."""
        if not context['sector']:
            return []
        
        records = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract market name
            market = self._extract_market_name(line)
            if not market or not self._is_valid_market(market):
                continue
            
            # Extract cap rates
            cap_rates = self._extract_cap_rates(line)
            if not cap_rates:
                continue
            
            # Create record
            try:
                record = CapRateRecord(
                    sector=context['sector'],
                    subsector=context.get('subsector'),
                    region=context.get('region'),
                    market=market,
                    report_year=year,
                    report_half=half,
                    h1_low=cap_rates[0][0] if cap_rates else None,
                    h1_high=cap_rates[0][1] if cap_rates else None,
                    h1_alt_low=cap_rates[1][0] if len(cap_rates) > 1 else None,
                    h1_alt_high=cap_rates[1][1] if len(cap_rates) > 1 else None,
                    source_file=source_file
                )
                records.append(record)
            except Exception:
                continue  # Skip invalid records
        
        return records
    
    def _extract_market_name(self, text: str) -> Optional[str]:
        """Extract market name from text."""
        # Look for city-like patterns at the start of lines with cap rates
        # Must have cap rates in the same line to be considered valid
        if not any(pattern.search(text) for pattern in self.cap_rate_patterns):
            return None
        
        # Extract potential market name (first 1-3 words)
        match = re.match(r'^([A-Za-z\s\.\-/&()]{3,30})(?:\s+[\d\.])', text)
        if match:
            raw_market = match.group(1).strip()
            
            # Skip if it looks like survey text (too many words or common phrases)
            words = raw_market.split()
            if len(words) > 3:
                return None
            
            # Skip common survey phrases
            survey_phrases = [
                'respective markets', 'becomes more', 'integrated into', 'investment strategies',
                'gap between', 'intentions and', 'action likely', 'survey across',
                'pricing was', 'most consistent', 'largest disconnect', 'high street'
            ]
            
            if any(phrase in raw_market.lower() for phrase in survey_phrases):
                return None
            
            # Use text processor to normalize the market name
            normalized_market = self.text_processor.normalize_market_name(raw_market)
            return normalized_market if normalized_market else None
        return None
    
    def _is_valid_market(self, market: str) -> bool:
        """Validate market name."""
        if not market or len(market) < 3:
            return False
        
        # Check against known valid markets
        valid_markets = [
            "Atlanta", "Austin", "Boston", "Charlotte", "Chicago", "Dallas", 
            "Denver", "Houston", "Los Angeles", "Miami", "Nashville", 
            "New York", "Orlando", "Phoenix", "Raleigh", "San Francisco", 
            "Seattle", "Tampa", "Washington DC"
        ]
        
        if any(vm.lower() in market.lower() for vm in valid_markets):
            return True
        
        # Exclude common non-market words
        exclude_words = ['the', 'and', 'or', 'but', 'after', 'before', 'during']
        if market.lower() in exclude_words:
            return False
        
        # Exclude mostly numbers
        if re.match(r'^[\d\s%\.]+$', market):
            return False
        
        return True
    
    def _extract_cap_rates(self, text: str) -> List[Tuple[float, float]]:
        """Extract cap rate ranges from text."""
        rates = []
        
        # Try patterns in order of preference, return first match
        for pattern in self.cap_rate_patterns:
            matches = pattern.findall(text)
            if matches:
                for match in matches:
                    try:
                        if isinstance(match, tuple) and len(match) == 2:
                            low = float(match[0])
                            high = float(match[1])
                        else:
                            low = high = float(match)
                        
                        # Validate rates
                        if 0.5 <= low <= 15.0 and 0.5 <= high <= 15.0:
                            rates.append((low, high))
                    except (ValueError, TypeError):
                        continue
                # Return after first successful pattern match to avoid duplicates
                if rates:
                    break
        
        return rates
    
    def _create_metadata(self, file_path: Path, year: int, half: int, record_count: int) -> Dict:
        """Create metadata for the parsing result."""
        file_content = file_path.read_bytes()
        
        return {
            'filename': file_path.name,
            'file_size': len(file_content),
            'file_hash': hashlib.sha256(file_content).hexdigest(),
            'report_year': year,
            'report_half': half,
            'record_count': record_count,
            'parsed_at': datetime.utcnow().isoformat(),
            'parser_version': '2.0.0'
        } 