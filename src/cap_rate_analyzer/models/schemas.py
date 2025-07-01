"""Data schemas and models for cap rate analysis."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CapRateRecord(BaseModel):
    """Individual cap rate record."""
    
    sector: str
    subsector: Optional[str] = None
    region: Optional[str] = None
    market: str
    report_year: int = Field(ge=2000, le=2030)
    report_half: int = Field(ge=1, le=2)
    h1_low: Optional[float] = Field(None, ge=0, le=20)
    h1_high: Optional[float] = Field(None, ge=0, le=20)
    h2_low: Optional[float] = Field(None, ge=0, le=20)
    h2_high: Optional[float] = Field(None, ge=0, le=20)
    h1_alt_low: Optional[float] = Field(None, ge=0, le=20)
    h1_alt_high: Optional[float] = Field(None, ge=0, le=20)
    h2_alt_low: Optional[float] = Field(None, ge=0, le=20)
    h2_alt_high: Optional[float] = Field(None, ge=0, le=20)
    source_file: str
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class ParseResult(BaseModel):
    """Result of parsing a PDF file."""
    
    records: List[CapRateRecord]
    metadata: Dict
    success: bool = True
    errors: List[str] = []


class ProcessingResult(BaseModel):
    """Result of data processing."""
    
    success: bool
    total_records: int
    new_records: int
    updated_records: int
    errors: List[str] = []
    metadata: Dict 