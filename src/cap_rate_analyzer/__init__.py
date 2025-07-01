"""
Cap Rate Analyzer - Static Dashboard System

A streamlined solution for processing semi-annual cap rate reports
and generating static dashboards for SharePoint deployment.
"""

__version__ = "2.0.0"
__author__ = "Live Oak Bank"

from .core.parser import CapRateParser
from .core.processor import DataProcessor
from .models.schemas import CapRateRecord, ParseResult, ProcessingResult

__all__ = [
    "CapRateParser", 
    "DataProcessor", 
    "CapRateRecord", 
    "ParseResult", 
    "ProcessingResult"
] 