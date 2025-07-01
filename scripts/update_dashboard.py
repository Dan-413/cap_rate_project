#!/usr/bin/env python3
"""
Update dashboard with all PDF data from semi_annual_reports directory.

This script processes all PDF reports in the semi_annual_reports directory 
and updates the dashboard CSV file with complete historical data.
Usage: python scripts/update_dashboard.py [--verbose]
"""

import argparse
import logging
import shutil
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cap_rate_analyzer.core.parser import CapRateParser
from cap_rate_analyzer.core.processor import DataProcessor


def setup_logging() -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('processing.log')
        ]
    )


def main():
    """Main processing function."""
    parser = argparse.ArgumentParser(description='Update dashboard with all cap rate reports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--reports-dir', default='semi_annual_reports', 
                       help='Directory containing PDF reports (default: semi_annual_reports)')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    setup_logging()
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get project paths
        project_root = Path(__file__).parent.parent
        reports_dir = project_root / args.reports_dir
        temp_output_dir = project_root / "temp_output"
        dashboard_dir = project_root / "dashboard"
        
        # Validate reports directory
        if not reports_dir.exists():
            logger.error(f"Reports directory not found: {reports_dir}")
            return 1
        
        # Find all PDF files
        pdf_files = list(reports_dir.glob("*.pdf"))
        if not pdf_files:
            logger.error(f"No PDF files found in: {reports_dir}")
            return 1
        
        # Sort PDF files by name for consistent processing order
        pdf_files.sort()
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Create temporary output directory
        temp_output_dir.mkdir(exist_ok=True)
        
        # Initialize parser and processor
        cap_parser = CapRateParser()
        processor = DataProcessor(output_dir=str(temp_output_dir))
        
        # Process all PDFs
        total_records = 0
        successful_files = 0
        all_parse_results = []
        
        for pdf_file in pdf_files:
            logger.info(f"Processing: {pdf_file.name}")
            
            try:
                # Parse PDF
                parse_result = cap_parser.parse_file(str(pdf_file))
                
                if not parse_result.success:
                    logger.error(f"Failed to parse {pdf_file.name}:")
                    for error in parse_result.errors:
                        logger.error(f"  - {error}")
                    continue
                
                logger.info(f"  Parsed {len(parse_result.records)} records")
                logger.info(f"  Report period: {parse_result.metadata.get('report_year')}-H{parse_result.metadata.get('report_half')}")
                
                all_parse_results.append(parse_result)
                total_records += len(parse_result.records)
                successful_files += 1
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
                continue
        
        if not all_parse_results:
            logger.error("No PDF files were successfully processed")
            return 1
        
        logger.info(f"Successfully processed {successful_files}/{len(pdf_files)} files")
        logger.info(f"Total records parsed: {total_records}")
        
        # Combine all results and process
        logger.info("Combining and processing all data...")
        combined_result = processor.combine_parse_results(all_parse_results)
        
        if not combined_result.success:
            logger.error("Data processing failed:")
            for error in combined_result.errors:
                logger.error(f"  - {error}")
            return 1
        
        # Update dashboard files
        logger.info("Updating dashboard files...")
        
        # Copy updated CSV to both root and dashboard
        output_csv = temp_output_dir / "historical_cap_rates.csv"
        if output_csv.exists():
            # Update root CSV file
            shutil.copy2(output_csv, project_root / "historical_cap_rates.csv")
            # Update dashboard CSV file
            shutil.copy2(output_csv, dashboard_dir / "historical_cap_rates.csv")
            logger.info("Dashboard data files updated")
        else:
            logger.error("Output CSV file not found")
            return 1
        
        # Clean up temp directory
        shutil.rmtree(temp_output_dir)
        
        # Report results
        logger.info("Dashboard update completed successfully!")
        logger.info(f"Total records in dataset: {combined_result.total_records}")
        logger.info(f"Files processed: {successful_files}")
        
        # Calculate unique time periods
        time_periods = set()
        for r in all_parse_results:
            year = r.metadata.get('report_year')
            half = r.metadata.get('report_half')
            time_periods.add(f"{year}-H{half}")
        
        logger.info(f"Time periods covered: {len(time_periods)}")
        logger.info(f"Dashboard ready at: {dashboard_dir / 'index.html'}")
        
        return 0
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 