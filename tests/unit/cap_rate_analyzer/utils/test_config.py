"""
Unit tests for configuration module.
"""

import unittest
import os
from unittest.mock import patch

from cap_rate_analyzer.utils.config import Config, get_config


class TestConfig(unittest.TestCase):
    """Test configuration functionality."""
    
    def test_config_initialization_defaults(self):
        """Test Config initialization with default values."""
        config = Config()
        
        self.assertEqual(config.min_cap_rate, 0.5)
        self.assertEqual(config.max_cap_rate, 15.0)
        self.assertEqual(config.min_market_length, 3)
        self.assertEqual(config.valid_halves, [1, 2])
        self.assertIsInstance(config.valid_years, list)
        self.assertIsInstance(config.valid_markets, list)
        self.assertIsInstance(config.csv_columns, list)
        self.assertIsInstance(config.brand_colors, dict)
    
    def test_config_custom_values(self):
        """Test Config initialization with custom values."""
        config = Config(
            min_cap_rate=2.0,
            max_cap_rate=12.0,
            min_market_length=5
        )
        
        self.assertEqual(config.min_cap_rate, 2.0)
        self.assertEqual(config.max_cap_rate, 12.0)
        self.assertEqual(config.min_market_length, 5)
        # Should still have defaults for other values
        self.assertEqual(config.valid_halves, [1, 2])
    
    def test_config_post_init_years(self):
        """Test that valid_years is properly initialized."""
        config = Config()
        
        self.assertIn(2020, config.valid_years)
        self.assertIn(2030, config.valid_years)
        self.assertNotIn(2019, config.valid_years)
        self.assertNotIn(2031, config.valid_years)
    
    def test_config_post_init_markets(self):
        """Test that valid_markets contains expected cities."""
        config = Config()
        
        expected_markets = ['Atlanta', 'Boston', 'Chicago', 'Los Angeles', 'New York']
        for market in expected_markets:
            self.assertIn(market, config.valid_markets)
    
    def test_config_post_init_csv_columns(self):
        """Test that CSV columns are properly initialized."""
        config = Config()
        
        expected_columns = [
            'Sector', 'Market', 'Report_Year', 'Report_Half',
            'H1_Low', 'H1_High'
        ]
        for column in expected_columns:
            self.assertIn(column, config.csv_columns)
    
    def test_config_post_init_brand_colors(self):
        """Test that brand colors are properly initialized."""
        config = Config()
        
        expected_colors = ['primary', 'secondary', 'accent', 'light', 'background']
        for color_key in expected_colors:
            self.assertIn(color_key, config.brand_colors)
            self.assertIsInstance(config.brand_colors[color_key], str)
            self.assertTrue(config.brand_colors[color_key].startswith('#'))
    
    @patch.dict(os.environ, {'MIN_CAP_RATE': '1.5', 'MAX_CAP_RATE': '10.0', 'MIN_MARKET_LENGTH': '4'})
    def test_config_from_env(self):
        """Test Config.from_env() with environment variables."""
        config = Config.from_env()
        
        self.assertEqual(config.min_cap_rate, 1.5)
        self.assertEqual(config.max_cap_rate, 10.0)
        self.assertEqual(config.min_market_length, 4)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_from_env_defaults(self):
        """Test Config.from_env() with no environment variables."""
        config = Config.from_env()
        
        self.assertEqual(config.min_cap_rate, 0.5)
        self.assertEqual(config.max_cap_rate, 15.0)
        self.assertEqual(config.min_market_length, 3)
    
    @patch.dict(os.environ, {'MIN_CAP_RATE': 'invalid'})
    def test_config_from_env_invalid_values(self):
        """Test Config.from_env() with invalid environment values."""
        with self.assertRaises(ValueError):
            Config.from_env()
    
    def test_get_config_structure(self):
        """Test get_config() returns proper structure."""
        config_dict = get_config()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn('parsing', config_dict)
        self.assertIn('validation', config_dict)
        self.assertIn('output', config_dict)
        self.assertIn('brand_colors', config_dict)
    
    def test_get_config_parsing_section(self):
        """Test parsing section of get_config()."""
        config_dict = get_config()
        parsing = config_dict['parsing']
        
        self.assertIn('min_cap_rate', parsing)
        self.assertIn('max_cap_rate', parsing)
        self.assertIn('valid_years', parsing)
        self.assertIn('valid_halves', parsing)
        
        self.assertIsInstance(parsing['min_cap_rate'], float)
        self.assertIsInstance(parsing['max_cap_rate'], float)
        self.assertIsInstance(parsing['valid_years'], list)
        self.assertIsInstance(parsing['valid_halves'], list)
    
    def test_get_config_validation_section(self):
        """Test validation section of get_config()."""
        config_dict = get_config()
        validation = config_dict['validation']
        
        self.assertIn('min_market_length', validation)
        self.assertIn('valid_markets', validation)
        
        self.assertIsInstance(validation['min_market_length'], int)
        self.assertIsInstance(validation['valid_markets'], list)
    
    def test_get_config_output_section(self):
        """Test output section of get_config()."""
        config_dict = get_config()
        output = config_dict['output']
        
        self.assertIn('csv_columns', output)
        self.assertIsInstance(output['csv_columns'], list)
    
    def test_get_config_brand_colors_section(self):
        """Test brand_colors section of get_config()."""
        config_dict = get_config()
        colors = config_dict['brand_colors']
        
        self.assertIsInstance(colors, dict)
        self.assertIn('primary', colors)
        self.assertIn('secondary', colors)
    
    @patch.dict(os.environ, {'MIN_CAP_RATE': '2.5'})
    def test_get_config_with_env_vars(self):
        """Test get_config() respects environment variables."""
        config_dict = get_config()
        
        self.assertEqual(config_dict['parsing']['min_cap_rate'], 2.5)
    
    def test_config_dataclass_attributes(self):
        """Test that Config has all expected attributes."""
        config = Config()
        
        attributes = [
            'min_cap_rate', 'max_cap_rate', 'valid_years', 'valid_halves',
            'min_market_length', 'valid_markets', 'csv_columns', 'brand_colors'
        ]
        
        for attr in attributes:
            self.assertTrue(hasattr(config, attr))
    
    def test_config_immutability(self):
        """Test that config values can be modified (dataclass is mutable)."""
        config = Config()
        original_min = config.min_cap_rate
        
        config.min_cap_rate = 5.0
        self.assertEqual(config.min_cap_rate, 5.0)
        self.assertNotEqual(config.min_cap_rate, original_min)
    
    def test_valid_years_range(self):
        """Test that valid_years contains the expected range."""
        config = Config()
        
        self.assertEqual(min(config.valid_years), 2020)
        self.assertEqual(max(config.valid_years), 2030)
        self.assertEqual(len(config.valid_years), 11)  # 2020-2030 inclusive
    
    def test_valid_markets_length(self):
        """Test that valid_markets has reasonable number of markets."""
        config = Config()
        
        # Should have major US markets
        self.assertGreater(len(config.valid_markets), 20)
        self.assertLess(len(config.valid_markets), 100)
    
    def test_csv_columns_completeness(self):
        """Test that CSV columns cover all necessary fields."""
        config = Config()
        
        required_fields = [
            'Sector', 'Market', 'Report_Year', 'Report_Half',
            'H1_Low', 'H1_High'
        ]
        
        for field in required_fields:
            self.assertIn(field, config.csv_columns)
    
    def test_brand_colors_hex_format(self):
        """Test that brand colors are in hex format."""
        config = Config()
        
        for color_name, color_value in config.brand_colors.items():
            self.assertIsInstance(color_value, str)
            self.assertTrue(color_value.startswith('#'))
            self.assertEqual(len(color_value), 7)  # #RRGGBB format
    
    def test_config_validation_ranges(self):
        """Test that configuration values are in valid ranges."""
        config = Config()
        
        # Cap rates should be reasonable
        self.assertGreater(config.min_cap_rate, 0)
        self.assertLess(config.max_cap_rate, 50)
        self.assertLess(config.min_cap_rate, config.max_cap_rate)
        
        # Market length should be reasonable
        self.assertGreater(config.min_market_length, 0)
        self.assertLess(config.min_market_length, 20)
    
    def test_config_types(self):
        """Test that configuration values have correct types."""
        config = Config()
        
        self.assertIsInstance(config.min_cap_rate, float)
        self.assertIsInstance(config.max_cap_rate, float)
        self.assertIsInstance(config.min_market_length, int)
        self.assertIsInstance(config.valid_years, list)
        self.assertIsInstance(config.valid_halves, list)
        self.assertIsInstance(config.valid_markets, list)
        self.assertIsInstance(config.csv_columns, list)
        self.assertIsInstance(config.brand_colors, dict)


if __name__ == '__main__':
    unittest.main() 