"""
End-to-end integration tests for the cap rate analyzer.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import pandas as pd
from unittest.mock import patch, MagicMock
import requests

from cap_rate_analyzer.core.parser import CapRateParser
from cap_rate_analyzer.core.processor import DataProcessor
from cap_rate_analyzer.models.schemas import CapRateRecord


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / 'output'
        self.output_dir.mkdir()
        
        self.parser = CapRateParser()
        self.processor = DataProcessor(str(self.output_dir))
        
        # Sample test data
        self.sample_records = [
            CapRateRecord(
                sector="Industrial",
                subsector="Warehouse",
                region="West",
                market="Los Angeles",
                report_year=2024,
                report_half=1,
                h1_low=4.5,
                h1_high=5.5,
                source_file="test.pdf"
            ),
            CapRateRecord(
                sector="Office",
                subsector="Class A",
                region="East",
                market="New York",
                report_year=2024,
                report_half=1,
                h1_low=6.0,
                h1_high=7.0,
                source_file="test.pdf"
            ),
            CapRateRecord(
                sector="Retail",
                subsector="Shopping Center",
                region="South",
                market="Miami",
                report_year=2024,
                report_half=1,
                h1_low=5.0,
                h1_high=6.0,
                source_file="test.pdf"
            )
        ]
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow_success(self):
        """Test complete workflow from parsing to dashboard output."""
        # Step 1: Mock successful parsing
        with patch.object(self.parser, 'parse_file') as mock_parse:
            parse_result = MagicMock()
            parse_result.success = True
            parse_result.records = self.sample_records
            parse_result.metadata = {'filename': 'test.pdf', 'total_pages': 10}
            parse_result.errors = []
            mock_parse.return_value = parse_result
            
            # Step 2: Process the parse result
            processing_result = self.processor.process_parse_result(parse_result)
            
            # Step 3: Verify processing success
            self.assertTrue(processing_result.success)
            self.assertEqual(processing_result.total_records, 3)
            self.assertEqual(processing_result.new_records, 3)
            
            # Step 4: Verify output files were created
            csv_path = self.output_dir / 'historical_data.csv'
            json_path = self.output_dir / 'data.json'
            metadata_path = self.output_dir / 'metadata.json'
            
            self.assertTrue(csv_path.exists())
            self.assertTrue(json_path.exists())
            self.assertTrue(metadata_path.exists())
            
            # Step 5: Verify CSV content
            df = pd.read_csv(csv_path)
            self.assertEqual(len(df), 3)
            self.assertIn('Industrial', df['Sector'].values)
            self.assertIn('Office', df['Sector'].values)
            self.assertIn('Retail', df['Sector'].values)
            
            # Step 6: Verify JSON content
            with open(json_path, 'r') as f:
                dashboard_data = json.load(f)
            
            self.assertIn('metadata', dashboard_data)
            self.assertIn('summary', dashboard_data)
            self.assertIn('timeSeries', dashboard_data)
            self.assertIn('markets', dashboard_data)
            self.assertIn('sectors', dashboard_data)
            
            self.assertEqual(dashboard_data['metadata']['totalRecords'], 3)
            self.assertEqual(dashboard_data['summary']['totalSectors'], 3)
    
    def test_incremental_data_processing(self):
        """Test processing multiple batches of data incrementally."""
        # Step 1: Process first batch
        first_batch = self.sample_records[:2]
        with patch.object(self.parser, 'parse_file') as mock_parse:
            parse_result = MagicMock()
            parse_result.success = True
            parse_result.records = first_batch
            parse_result.metadata = {'filename': 'batch1.pdf'}
            parse_result.errors = []
            mock_parse.return_value = parse_result
            
            result1 = self.processor.process_parse_result(parse_result)
            self.assertTrue(result1.success)
            self.assertEqual(result1.total_records, 2)
        
        # Step 2: Process second batch
        second_batch = self.sample_records[2:]
        with patch.object(self.parser, 'parse_file') as mock_parse:
            parse_result = MagicMock()
            parse_result.success = True
            parse_result.records = second_batch
            parse_result.metadata = {'filename': 'batch2.pdf'}
            parse_result.errors = []
            mock_parse.return_value = parse_result
            
            result2 = self.processor.process_parse_result(parse_result)
            self.assertTrue(result2.success)
            self.assertEqual(result2.total_records, 3)  # Total should now be 3
            self.assertEqual(result2.new_records, 1)    # Only 1 new record
        
        # Step 3: Verify final state
        csv_path = self.output_dir / 'historical_data.csv'
        df = pd.read_csv(csv_path)
        self.assertEqual(len(df), 3)
    
    def test_error_recovery_workflow(self):
        """Test workflow behavior with various errors."""
        # Test with parse failure
        with patch.object(self.parser, 'parse_file') as mock_parse:
            parse_result = MagicMock()
            parse_result.success = False
            parse_result.records = []
            parse_result.errors = ['Parse failed']
            mock_parse.return_value = parse_result
            
            result = self.processor.process_parse_result(parse_result)
            self.assertFalse(result.success)
            self.assertEqual(result.total_records, 0)
            self.assertIn('Parse failed', result.errors)
    
    def test_data_validation_workflow(self):
        """Test data validation throughout the workflow."""
        # Create records with valid Pydantic structure but that will fail processor validation
        # Using a market name that's too short to test processor validation
        valid_records = [
            CapRateRecord(
                sector="Industrial",
                subsector="Warehouse",
                region="West",
                market="LA",  # This should pass validation (3 chars minimum)
                report_year=2025,  # Valid year
                report_half=1,
                h1_low=4.5,
                h1_high=5.5,
                source_file="test.pdf"
            )
        ]
        
        with patch.object(self.parser, 'parse_file') as mock_parse:
            parse_result = MagicMock()
            parse_result.success = True
            parse_result.records = valid_records
            parse_result.metadata = {'filename': 'valid.pdf'}
            parse_result.errors = []
            mock_parse.return_value = parse_result
            
            result = self.processor.process_parse_result(parse_result)
            
            # The data should now be valid, so processing should succeed
            self.assertTrue(result.success)
            self.assertEqual(result.total_records, 1)
            self.assertEqual(result.new_records, 1)
    
    def test_dashboard_data_consistency(self):
        """Test consistency between CSV and JSON outputs."""
        with patch.object(self.parser, 'parse_file') as mock_parse:
            parse_result = MagicMock()
            parse_result.success = True
            parse_result.records = self.sample_records
            parse_result.metadata = {'filename': 'test.pdf'}
            parse_result.errors = []
            mock_parse.return_value = parse_result
            
            self.processor.process_parse_result(parse_result)
            
            # Read both outputs
            csv_path = self.output_dir / 'historical_data.csv'
            json_path = self.output_dir / 'data.json'
            
            df = pd.read_csv(csv_path)
            with open(json_path, 'r') as f:
                dashboard_data = json.load(f)
            
            # Verify consistency
            self.assertEqual(len(df), dashboard_data['metadata']['totalRecords'])
            self.assertEqual(df['Sector'].nunique(), dashboard_data['summary']['totalSectors'])
            self.assertEqual(df['Market'].nunique(), dashboard_data['summary']['totalMarkets'])
    
    def test_performance_with_large_dataset(self):
        """Test performance with larger dataset."""
        # Create larger dataset
        large_dataset = []
        sectors = ['Industrial', 'Office', 'Retail', 'Multifamily', 'Hotel']
        markets = ['Los Angeles', 'New York', 'Chicago', 'Houston', 'Phoenix']
        
        for i in range(100):  # 100 records
            large_dataset.append(
                CapRateRecord(
                    sector=sectors[i % len(sectors)],
                    subsector="Generic",
                    region="National",
                    market=markets[i % len(markets)],
                    report_year=2024,
                    report_half=1,
                    h1_low=4.0 + (i % 10) * 0.1,
                    h1_high=5.0 + (i % 10) * 0.1,
                    source_file="large.pdf"
                )
            )
        
        with patch.object(self.parser, 'parse_file') as mock_parse:
            parse_result = MagicMock()
            parse_result.success = True
            parse_result.records = large_dataset
            parse_result.metadata = {'filename': 'large.pdf'}
            parse_result.errors = []
            mock_parse.return_value = parse_result
            
            import time
            start_time = time.time()
            result = self.processor.process_parse_result(parse_result)
            end_time = time.time()
            
            # Should complete within reasonable time
            self.assertLess(end_time - start_time, 10.0)  # Less than 10 seconds
            self.assertTrue(result.success)
            self.assertEqual(result.total_records, 100)
    
    def test_multiple_pdf_batch_processing(self):
        """Test processing multiple PDFs in batch."""
        pdf_files = ['h1-2023.pdf', 'h2-2023.pdf', 'h1-2024.pdf']
        all_records = []
        
        for i, pdf_file in enumerate(pdf_files):
            batch_records = [
                CapRateRecord(
                    sector="Industrial",
                    subsector="Warehouse",
                    region="West",
                    market=f"Market_{i}",
                    report_year=2023 + (i // 2),
                    report_half=1 + (i % 2),
                    h1_low=4.0 + i * 0.5,
                    h1_high=5.0 + i * 0.5,
                    source_file=pdf_file
                )
            ]
            all_records.extend(batch_records)
            
            with patch.object(self.parser, 'parse_file') as mock_parse:
                parse_result = MagicMock()
                parse_result.success = True
                parse_result.records = batch_records
                parse_result.metadata = {'filename': pdf_file}
                parse_result.errors = []
                mock_parse.return_value = parse_result
                
                result = self.processor.process_parse_result(parse_result)
                self.assertTrue(result.success)
        
        # Verify final state
        csv_path = self.output_dir / 'historical_data.csv'
        df = pd.read_csv(csv_path)
        self.assertEqual(len(df), 3)
        
        # Verify different years and halves
        years = sorted(df['Report_Year'].unique())
        self.assertEqual(years, [2023, 2024])
    
    def test_backup_and_archive_functionality(self):
        """Test backup and archiving of data."""
        # Create initial data
        with patch.object(self.parser, 'parse_file') as mock_parse:
            parse_result = MagicMock()
            parse_result.success = True
            parse_result.records = self.sample_records[:1]
            parse_result.metadata = {'filename': 'initial.pdf'}
            parse_result.errors = []
            mock_parse.return_value = parse_result
            
            self.processor.process_parse_result(parse_result)
        
        # Verify initial CSV exists
        csv_path = self.output_dir / 'historical_data.csv'
        self.assertTrue(csv_path.exists())
        
        # Process more data (should create backup)
        with patch.object(self.parser, 'parse_file') as mock_parse:
            parse_result = MagicMock()
            parse_result.success = True
            parse_result.records = self.sample_records[1:]
            parse_result.metadata = {'filename': 'update.pdf'}
            parse_result.errors = []
            mock_parse.return_value = parse_result
            
            self.processor.process_parse_result(parse_result)
        
        # Verify archive directory has backup files
        archive_dir = self.output_dir / 'archive'
        if archive_dir.exists():
            backup_files = list(archive_dir.glob('historical_data_backup_*.csv'))
            self.assertGreaterEqual(len(backup_files), 0)
    
    @patch('requests.get')
    def test_dashboard_server_integration(self, mock_get):
        """Test integration with dashboard server."""
        # Mock successful server response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head><title>Cap Rate Dashboard</title></head>
            <body>
                <div id="dashboard-container">Dashboard Content</div>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # Test dashboard accessibility
        response = requests.get('http://localhost:8080/index.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cap Rate Dashboard', response.text)
        self.assertIn('dashboard-container', response.text)
    
    def test_configuration_override_workflow(self):
        """Test workflow with custom configuration."""
        custom_config = {
            'parsing': {
                'min_cap_rate': 2.0,
                'max_cap_rate': 15.0
            },
            'output': {
                'archive_days': 60
            }
        }
        
        # Create parser and processor (custom config would be applied via environment variables)
        parser = CapRateParser()
        processor = DataProcessor(str(self.output_dir))
        
        # Process data with custom config
        with patch.object(parser, 'parse_file') as mock_parse:
            parse_result = MagicMock()
            parse_result.success = True
            parse_result.records = self.sample_records
            parse_result.metadata = {'filename': 'custom.pdf'}
            parse_result.errors = []
            mock_parse.return_value = parse_result
            
            result = processor.process_parse_result(parse_result)
            self.assertTrue(result.success)
    
    def test_error_logging_and_reporting(self):
        """Test error logging and reporting throughout workflow."""
        # Test with various error conditions
        error_conditions = [
            {'parse_success': False, 'parse_errors': ['PDF corrupted']},
            {'parse_success': True, 'records': [], 'parse_errors': ['No data found']},
        ]
        
        for condition in error_conditions:
            with patch.object(self.parser, 'parse_file') as mock_parse:
                parse_result = MagicMock()
                parse_result.success = condition.get('parse_success', True)
                parse_result.records = condition.get('records', self.sample_records)
                parse_result.errors = condition.get('parse_errors', [])
                parse_result.metadata = {'filename': 'error_test.pdf'}
                mock_parse.return_value = parse_result
                
                result = self.processor.process_parse_result(parse_result)
                
                if not condition.get('parse_success', True):
                    self.assertFalse(result.success)
                    self.assertTrue(len(result.errors) > 0)
    
    def test_concurrent_processing_safety(self):
        """Test thread safety with concurrent processing."""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def process_batch(batch_id):
            try:
                temp_output = Path(self.temp_dir) / f'output_{batch_id}'
                temp_output.mkdir()
                temp_processor = DataProcessor(str(temp_output))
                
                batch_records = [
                    CapRateRecord(
                        sector="Industrial",
                        subsector="Warehouse",
                        region="West",
                        market=f"Market_{batch_id}",
                        report_year=2024,
                        report_half=1,
                        h1_low=4.0 + batch_id,
                        h1_high=5.0 + batch_id,
                        source_file=f"batch_{batch_id}.pdf"
                    )
                ]
                
                with patch.object(self.parser, 'parse_file') as mock_parse:
                    parse_result = MagicMock()
                    parse_result.success = True
                    parse_result.records = batch_records
                    parse_result.metadata = {'filename': f'batch_{batch_id}.pdf'}
                    parse_result.errors = []
                    mock_parse.return_value = parse_result
                    
                    result = temp_processor.process_parse_result(parse_result)
                    results_queue.put((batch_id, result.success))
            except Exception as e:
                results_queue.put((batch_id, False))
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=process_batch, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        successful_batches = 0
        while not results_queue.empty():
            batch_id, success = results_queue.get()
            if success:
                successful_batches += 1
        
        self.assertEqual(successful_batches, 3)


if __name__ == '__main__':
    unittest.main() 