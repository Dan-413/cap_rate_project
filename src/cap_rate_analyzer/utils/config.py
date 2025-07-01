"""Configuration management for the cap rate analyzer."""

import os
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration settings for the cap rate analyzer."""
    
    # Parsing settings
    min_cap_rate: float = 0.5
    max_cap_rate: float = 15.0
    valid_years: List[int] = None
    valid_halves: List[int] = None
    
    # Validation settings
    min_market_length: int = 3
    valid_markets: List[str] = None
    
    # Output settings
    csv_columns: List[str] = None
    
    # Brand colors
    brand_colors: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.valid_years is None:
            self.valid_years = list(range(2020, 2031))
        
        if self.valid_halves is None:
            self.valid_halves = [1, 2]
        
        if self.valid_markets is None:
            self.valid_markets = [
                "Atlanta", "Austin", "Boston", "Charlotte", "Chicago", "Dallas",
                "Denver", "Houston", "Los Angeles", "Miami", "Nashville",
                "New York", "Orlando", "Phoenix", "Raleigh", "San Francisco",
                "Seattle", "Tampa", "Washington DC", "Baltimore", "Cincinnati",
                "Cleveland", "Columbus", "Detroit", "Indianapolis", "Kansas City",
                "Las Vegas", "Memphis", "Milwaukee", "Minneapolis", "Pittsburgh",
                "Portland", "Sacramento", "Salt Lake City", "San Antonio",
                "San Diego", "St. Louis", "Virginia Beach", "Fort Lauderdale",
                "Jacksonville", "Richmond", "Tucson", "Albuquerque", "Birmingham",
                "Buffalo", "Charleston", "Grand Rapids", "Greenville", "Hartford",
                "Honolulu", "Louisville", "Oklahoma City", "Omaha", "Providence",
                "Rochester", "Spokane", "Syracuse", "Tulsa", "Fresno"
            ]
        
        if self.csv_columns is None:
            self.csv_columns = [
                'Sector', 'Subsector', 'Region', 'Market', 'Report_Year', 'Report_Half',
                'H1_Low', 'H1_High', 'H2_Low', 'H2_High',
                'H1_Alt_Low', 'H1_Alt_High', 'H2_Alt_Low', 'H2_Alt_High'
            ]
        
        if self.brand_colors is None:
            self.brand_colors = {
            'primary': '#371CA1',
            'secondary': '#1C0E52',
            'accent': '#1ECD7D',
            'tertiary': '#C17B42',
            'light': '#E8DCC1',
            'background': '#F6F4EF'
        }
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables."""
        return cls(
            min_cap_rate=float(os.getenv('MIN_CAP_RATE', '0.5')),
            max_cap_rate=float(os.getenv('MAX_CAP_RATE', '15.0')),
            min_market_length=int(os.getenv('MIN_MARKET_LENGTH', '3'))
        )


def get_config() -> Dict:
    """Get configuration settings (legacy compatibility)."""
    config = Config.from_env()
    return {
        'parsing': {
            'min_cap_rate': config.min_cap_rate,
            'max_cap_rate': config.max_cap_rate,
            'valid_years': config.valid_years,
            'valid_halves': config.valid_halves
        },
        'validation': {
            'min_market_length': config.min_market_length,
            'valid_markets': config.valid_markets
        },
        'output': {
            'csv_columns': config.csv_columns
        },
        'brand_colors': config.brand_colors
    } 