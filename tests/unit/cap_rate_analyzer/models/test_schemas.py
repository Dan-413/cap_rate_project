"""Unit tests for data schemas."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from cap_rate_analyzer.models.schemas import CapRateRecord, ParseResult, ProcessingResult


class TestCapRateRecord:
    """Test CapRateRecord schema."""
    
    def test_valid_record_creation(self):
        """Test creating a valid cap rate record."""
        record = CapRateRecord(
            sector="Multifamily",
            subsector="Infill",
            region="Southeast",
            market="Atlanta",
            report_year=2024,
            report_half=1,
            h1_low=5.0,
            h1_high=6.0,
            source_file="test.pdf"
        )
        
        assert record.sector == "Multifamily"
        assert record.market == "Atlanta"
        assert record.report_year == 2024
        assert record.report_half == 1
        assert isinstance(record.extracted_at, datetime)
    
    def test_invalid_year_validation(self):
        """Test year validation."""
        with pytest.raises(ValidationError):
            CapRateRecord(
                sector="Office",
                market="Chicago",
                report_year=1999,  # Too early
                report_half=1,
                source_file="test.pdf"
            )
        
        with pytest.raises(ValidationError):
            CapRateRecord(
                sector="Office",
                market="Chicago",
                report_year=2031,  # Too late
                report_half=1,
                source_file="test.pdf"
            )
    
    def test_invalid_half_validation(self):
        """Test half validation."""
        with pytest.raises(ValidationError):
            CapRateRecord(
                sector="Office",
                market="Chicago",
                report_year=2024,
                report_half=3,  # Invalid half
                source_file="test.pdf"
            )
    
    def test_cap_rate_validation(self):
        """Test cap rate validation."""
        with pytest.raises(ValidationError):
            CapRateRecord(
                sector="Office",
                market="Chicago",
                report_year=2024,
                report_half=1,
                h1_low=-1.0,  # Negative rate
                source_file="test.pdf"
            )
        
        with pytest.raises(ValidationError):
            CapRateRecord(
                sector="Office",
                market="Chicago",
                report_year=2024,
                report_half=1,
                h1_high=25.0,  # Too high
                source_file="test.pdf"
            )
    
    def test_optional_fields(self):
        """Test that optional fields work correctly."""
        record = CapRateRecord(
            sector="Industrial",
            market="Dallas",
            report_year=2024,
            report_half=2,
            source_file="test.pdf"
        )
        
        assert record.subsector is None
        assert record.region is None
        assert record.h1_low is None


class TestParseResult:
    """Test ParseResult schema."""
    
    def test_successful_parse_result(self):
        """Test creating a successful parse result."""
        records = [
            CapRateRecord(
                sector="Office",
                market="New York",
                report_year=2024,
                report_half=1,
                source_file="test.pdf"
            )
        ]
        
        result = ParseResult(
            records=records,
            metadata={"file_size": 1024, "pages": 10}
        )
        
        assert result.success is True
        assert len(result.records) == 1
        assert len(result.errors) == 0
    
    def test_failed_parse_result(self):
        """Test creating a failed parse result."""
        result = ParseResult(
            records=[],
            metadata={},
            success=False,
            errors=["File not found", "Invalid format"]
        )
        
        assert result.success is False
        assert len(result.records) == 0
        assert len(result.errors) == 2


class TestProcessingResult:
    """Test ProcessingResult schema."""
    
    def test_successful_processing_result(self):
        """Test creating a successful processing result."""
        result = ProcessingResult(
            success=True,
            total_records=100,
            new_records=25,
            updated_records=5,
            metadata={"processing_time": 30.5}
        )
        
        assert result.success is True
        assert result.total_records == 100
        assert result.new_records == 25
        assert result.updated_records == 5
        assert len(result.errors) == 0
    
    def test_failed_processing_result(self):
        """Test creating a failed processing result."""
        result = ProcessingResult(
            success=False,
            total_records=0,
            new_records=0,
            updated_records=0,
            errors=["Database connection failed"],
            metadata={}
        )
        
        assert result.success is False
        assert len(result.errors) == 1 