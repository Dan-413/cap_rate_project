"""Integration tests for the full cap rate processing workflow."""

import pytest
import tempfile
from pathlib import Path

from cap_rate_analyzer.core.parser import CapRateParser
from cap_rate_analyzer.core.processor import DataProcessor


class TestFullWorkflow:
    """Test the complete PDF processing workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CapRateParser()
        self.temp_dir = tempfile.mkdtemp()
        self.processor = DataProcessor(self.temp_dir)
    
    def test_process_sample_pdf(self):
        """Test processing a sample PDF from semi_annual_reports."""
        # Find a sample PDF file
        pdf_dir = Path("semi_annual_reports")
        
        if not pdf_dir.exists():
            pytest.skip("semi_annual_reports directory not found")
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No PDF files found in semi_annual_reports")
        
        # Use the first PDF file found
        sample_pdf = pdf_files[0]
        
        # Parse the PDF
        parse_result = self.parser.parse_file(str(sample_pdf))
        
        # Verify parsing succeeded
        assert parse_result.success, f"Parsing failed: {parse_result.errors}"
        assert len(parse_result.records) > 0, "No records extracted"
        
        # Process the results
        processing_result = self.processor.process_parse_result(parse_result)
        
        # Verify processing succeeded
        assert processing_result.success, f"Processing failed: {processing_result.errors}"
        assert processing_result.total_records > 0
        assert processing_result.new_records > 0
        
        # Verify output files were created
        csv_path = Path(self.temp_dir) / "historical_data.csv"
        json_path = Path(self.temp_dir) / "data.json"
        
        assert csv_path.exists(), "CSV file not created"
        assert json_path.exists(), "JSON file not created"
        
        # Verify CSV has correct structure
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        expected_columns = [
            'Sector', 'Subsector', 'Region', 'Market', 'Report_Year', 'Report_Half',
            'H1_Low', 'H1_High', 'H2_Low', 'H2_High',
            'H1_Alt_Low', 'H1_Alt_High', 'H2_Alt_Low', 'H2_Alt_High'
        ]
        
        for col in expected_columns:
            assert col in df.columns, f"Missing column: {col}"
        
        # Verify data quality
        assert not df['Sector'].isna().all(), "All sectors are null"
        assert not df['Market'].isna().all(), "All markets are null"
        assert df['Report_Year'].between(2020, 2030).all(), "Invalid years found"
        assert df['Report_Half'].isin([1, 2]).all(), "Invalid halves found"
    
    def test_multiple_pdf_processing(self):
        """Test processing multiple PDFs."""
        pdf_dir = Path("semi_annual_reports")
        
        if not pdf_dir.exists():
            pytest.skip("semi_annual_reports directory not found")
        
        pdf_files = list(pdf_dir.glob("*.pdf"))[:2]  # Test with first 2 PDFs
        
        if len(pdf_files) < 2:
            pytest.skip("Need at least 2 PDF files for this test")
        
        total_records = 0
        
        for pdf_file in pdf_files:
            # Parse each PDF
            parse_result = self.parser.parse_file(str(pdf_file))
            assert parse_result.success, f"Failed to parse {pdf_file}"
            
            # Process results
            processing_result = self.processor.process_parse_result(parse_result)
            assert processing_result.success, f"Failed to process {pdf_file}"
            
            total_records = processing_result.total_records
        
        # Verify final CSV contains data from all PDFs
        csv_path = Path(self.temp_dir) / "historical_data.csv"
        assert csv_path.exists()
        
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        # Should have records from multiple time periods
        unique_periods = df[['Report_Year', 'Report_Half']].drop_duplicates()
        assert len(unique_periods) >= 2, "Should have multiple time periods"
        
        print(f"Processed {len(pdf_files)} PDFs, total records: {total_records}")
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test non-existent file
        parse_result = self.parser.parse_file("nonexistent.pdf")
        assert not parse_result.success
        assert len(parse_result.errors) > 0
        
        # Test processing failed parse result
        processing_result = self.processor.process_parse_result(parse_result)
        assert not processing_result.success
        assert processing_result.total_records == 0 