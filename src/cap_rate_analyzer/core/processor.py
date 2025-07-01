"""Data processor for merging and validating cap rate data."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from ..models.schemas import CapRateRecord, ParseResult, ProcessingResult
from ..utils.config import get_config


class DataProcessor:
    """Process and merge cap rate data."""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize the processor."""
        self.config = get_config()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # File paths
        self.csv_path = self.output_dir / "historical_data.csv"
        self.json_path = self.output_dir / "data.json"
        self.metadata_path = self.output_dir / "metadata.json"
        self.archive_dir = self.output_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)
    
    def process_parse_result(self, parse_result: ParseResult) -> ProcessingResult:
        """Process a parse result and merge with existing data."""
        if not parse_result.success:
            return ProcessingResult(
                success=False,
                total_records=0,
                new_records=0,
                updated_records=0,
                errors=parse_result.errors,
                metadata={}
            )
        
        try:
            # Load existing data
            existing_df = self._load_existing_data()
            
            # Convert parse result to DataFrame
            new_df = self._records_to_dataframe(parse_result.records)
            
            # Validate new data
            validation_errors = self._validate_data(new_df)
            if validation_errors:
                return ProcessingResult(
                    success=False,
                    total_records=0,
                    new_records=0,
                    updated_records=0,
                    errors=validation_errors,
                    metadata={}
                )
            
            # Merge data
            merged_df, new_count, updated_count = self._merge_data(existing_df, new_df)
            
            # Save results
            self._save_csv(merged_df)
            self._save_json(merged_df)
            self._save_metadata(parse_result.metadata, len(merged_df), new_count, updated_count)
            
            return ProcessingResult(
                success=True,
                total_records=len(merged_df),
                new_records=new_count,
                updated_records=updated_count,
                metadata=parse_result.metadata
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                total_records=0,
                new_records=0,
                updated_records=0,
                errors=[f"Processing failed: {str(e)}"],
                metadata={}
            )
    
    def _load_existing_data(self) -> pd.DataFrame:
        """Load existing historical data."""
        if self.csv_path.exists():
            return pd.read_csv(self.csv_path)
        else:
            # Create empty DataFrame with correct columns
            return pd.DataFrame(columns=self.config['output']['csv_columns'])
    
    def _records_to_dataframe(self, records: List[CapRateRecord]) -> pd.DataFrame:
        """Convert records to DataFrame."""
        data = []
        for record in records:
            data.append({
                'Sector': record.sector,
                'Subsector': record.subsector,
                'Region': record.region,
                'Market': record.market,
                'Report_Year': record.report_year,
                'Report_Half': record.report_half,
                'H1_Low': record.h1_low,
                'H1_High': record.h1_high,
                'H2_Low': record.h2_low,
                'H2_High': record.h2_high,
                'H1_Alt_Low': record.h1_alt_low,
                'H1_Alt_High': record.h1_alt_high,
                'H2_Alt_Low': record.h2_alt_low,
                'H2_Alt_High': record.h2_alt_high
            })
        
        return pd.DataFrame(data)
    
    def _validate_data(self, df: pd.DataFrame) -> List[str]:
        """Validate data quality."""
        errors = []
        
        # Check required columns
        required_cols = ['Sector', 'Market', 'Report_Year', 'Report_Half']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
        
        # Check data types and ranges
        if 'Report_Year' in df.columns:
            invalid_years = df[~df['Report_Year'].between(2020, 2030)]
            if not invalid_years.empty:
                errors.append(f"Invalid years found: {invalid_years['Report_Year'].tolist()}")
        
        if 'Report_Half' in df.columns:
            invalid_halves = df[~df['Report_Half'].isin([1, 2])]
            if not invalid_halves.empty:
                errors.append(f"Invalid halves found: {invalid_halves['Report_Half'].tolist()}")
        
        # Check cap rate ranges
        rate_columns = ['H1_Low', 'H1_High', 'H2_Low', 'H2_High', 
                       'H1_Alt_Low', 'H1_Alt_High', 'H2_Alt_Low', 'H2_Alt_High']
        
        for col in rate_columns:
            if col in df.columns:
                invalid_rates = df[
                    df[col].notna() & 
                    (~df[col].between(self.config['parsing']['min_cap_rate'], 
                                     self.config['parsing']['max_cap_rate']))
                ]
                if not invalid_rates.empty:
                    errors.append(f"Invalid cap rates in {col}: {invalid_rates[col].tolist()}")
        
        return errors
    
    def _merge_data(self, existing_df: pd.DataFrame, new_df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
        """Merge new data with existing data."""
        if existing_df.empty:
            return new_df, len(new_df), 0
        
        # Create merge keys
        merge_cols = ['Sector', 'Market', 'Report_Year', 'Report_Half']
        
        # Find new records (not in existing data)
        existing_keys = existing_df[merge_cols].apply(lambda x: tuple(x), axis=1).tolist()
        new_keys = new_df[merge_cols].apply(lambda x: tuple(x), axis=1).tolist()
        
        new_records = new_df[~new_df[merge_cols].apply(lambda x: tuple(x), axis=1).isin(existing_keys)]
        
        # For simplicity, we'll append new records and remove duplicates
        # In a more sophisticated system, we might track updates
        merged_df = pd.concat([existing_df, new_records], ignore_index=True)
        
        # Remove duplicates, keeping the last occurrence (newest data)
        merged_df = merged_df.drop_duplicates(subset=merge_cols, keep='last')
        
        # Sort by year, half, sector, market
        merged_df = merged_df.sort_values(['Report_Year', 'Report_Half', 'Sector', 'Market'])
        
        new_count = len(new_records)
        updated_count = 0  # For simplicity, not tracking updates in this version
        
        return merged_df, new_count, updated_count
    
    def _save_csv(self, df: pd.DataFrame) -> None:
        """Save data to CSV."""
        # Create backup if file exists
        if self.csv_path.exists():
            backup_path = self.archive_dir / f"historical_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.csv_path.rename(backup_path)
        
        # Save new data
        df.to_csv(self.csv_path, index=False)
    
    def _save_json(self, df: pd.DataFrame) -> None:
        """Save data to JSON for dashboard consumption."""
        # Create summary statistics
        summary = self._create_summary_stats(df)
        
        # Create time series data
        time_series = self._create_time_series_data(df)
        
        # Create market data
        market_data = self._create_market_data(df)
        
        # Create sector data
        sector_data = self._create_sector_data(df)
        
        # Combine into dashboard JSON
        dashboard_data = {
            'metadata': {
                'lastUpdated': datetime.utcnow().isoformat(),
                'totalRecords': len(df),
                'reportPeriods': sorted(list(set(df['Report_Year'].astype(str) + '-H' + df['Report_Half'].astype(str)))),
                'version': '2.0.0'
            },
            'summary': summary,
            'timeSeries': time_series,
            'markets': market_data,
            'sectors': sector_data
        }
        
        # Save JSON
        with open(self.json_path, 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
    
    def _create_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Create summary statistics."""
        return {
            'totalMarkets': df['Market'].nunique(),
            'totalSectors': df['Sector'].nunique(),
            'totalRecords': len(df),
            'dateRange': {
                'start': f"{df['Report_Year'].min()}-H{df['Report_Half'].min()}",
                'end': f"{df['Report_Year'].max()}-H{df['Report_Half'].max()}"
            },
            'sectorBreakdown': df['Sector'].value_counts().to_dict()
        }
    
    def _create_time_series_data(self, df: pd.DataFrame) -> List[Dict]:
        """Create time series data for charts."""
        # Group by period and sector
        time_series = []
        
        for (year, half, sector), group in df.groupby(['Report_Year', 'Report_Half', 'Sector']):
            # Calculate average rates (using H1 rates as primary)
            avg_low = group['H1_Low'].mean() if group['H1_Low'].notna().any() else None
            avg_high = group['H1_High'].mean() if group['H1_High'].notna().any() else None
            
            time_series.append({
                'period': f"{year}-H{half}",
                'year': year,
                'half': half,
                'sector': sector,
                'avgLow': round(avg_low, 2) if avg_low else None,
                'avgHigh': round(avg_high, 2) if avg_high else None,
                'avgRate': round((avg_low + avg_high) / 2, 2) if avg_low and avg_high else None,
                'recordCount': len(group)
            })
        
        return sorted(time_series, key=lambda x: (x['year'], x['half'], x['sector']))
    
    def _create_market_data(self, df: pd.DataFrame) -> List[Dict]:
        """Create market-level data."""
        market_data = []
        
        for market, group in df.groupby('Market'):
            # Get latest data for this market
            latest = group.loc[group['Report_Year'].idxmax()]
            
            # Calculate average rate
            rates = [latest['H1_Low'], latest['H1_High']]
            rates = [r for r in rates if pd.notna(r)]
            avg_rate = sum(rates) / len(rates) if rates else None
            
            market_data.append({
                'market': market,
                'sector': latest['Sector'],
                'region': latest['Region'],
                'latestRate': round(avg_rate, 2) if avg_rate else None,
                'latestPeriod': f"{latest['Report_Year']}-H{latest['Report_Half']}",
                'recordCount': len(group)
            })
        
        return sorted(market_data, key=lambda x: x['latestRate'] or 0, reverse=True)
    
    def _create_sector_data(self, df: pd.DataFrame) -> List[Dict]:
        """Create sector-level data."""
        sector_data = []
        
        for sector, group in df.groupby('Sector'):
            # Calculate overall statistics
            all_rates = []
            for col in ['H1_Low', 'H1_High', 'H2_Low', 'H2_High']:
                if col in group.columns:
                    all_rates.extend(group[col].dropna().tolist())
            
            sector_data.append({
                'sector': sector,
                'avgRate': round(sum(all_rates) / len(all_rates), 2) if all_rates else None,
                'minRate': round(min(all_rates), 2) if all_rates else None,
                'maxRate': round(max(all_rates), 2) if all_rates else None,
                'marketCount': group['Market'].nunique(),
                'recordCount': len(group)
            })
        
        return sorted(sector_data, key=lambda x: x['avgRate'] or 0)
    
    def _save_metadata(self, parse_metadata: Dict, total_records: int, new_records: int, updated_records: int) -> None:
        """Save processing metadata."""
        metadata = {
            'processing': {
                'processedAt': datetime.utcnow().isoformat(),
                'totalRecords': total_records,
                'newRecords': new_records,
                'updatedRecords': updated_records,
                'processor_version': '2.0.0'
            },
            'source': parse_metadata
        }
        
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str) 
    
    def combine_parse_results(self, parse_results: List[ParseResult]) -> ProcessingResult:
        """Combine multiple parse results and process them together."""
        if not parse_results:
            return ProcessingResult(
                success=False,
                total_records=0,
                new_records=0,
                updated_records=0,
                errors=["No parse results provided"],
                metadata={}
            )
        
        # Check for any failed parse results
        failed_results = [r for r in parse_results if not r.success]
        if failed_results:
            all_errors = []
            for result in failed_results:
                all_errors.extend(result.errors)
            return ProcessingResult(
                success=False,
                total_records=0,
                new_records=0,
                updated_records=0,
                errors=all_errors,
                metadata={}
            )
        
        try:
            # Combine all records from all parse results
            all_records = []
            combined_metadata = {
                'report_periods': [],
                'files_processed': [],
                'total_files': len(parse_results)
            }
            
            for result in parse_results:
                all_records.extend(result.records)
                year = result.metadata.get('report_year')
                half = result.metadata.get('report_half')
                filename = result.metadata.get('filename', 'unknown')
                
                if year and half:
                    combined_metadata['report_periods'].append(f"{year}-H{half}")
                combined_metadata['files_processed'].append(filename)
            
            # Convert all records to DataFrame
            combined_df = self._records_to_dataframe(all_records)
            
            # Validate combined data
            validation_errors = self._validate_data(combined_df)
            if validation_errors:
                return ProcessingResult(
                    success=False,
                    total_records=0,
                    new_records=0,
                    updated_records=0,
                    errors=validation_errors,
                    metadata=combined_metadata
                )
            
            # Remove duplicates and sort
            merge_cols = ['Sector', 'Market', 'Report_Year', 'Report_Half']
            combined_df = combined_df.drop_duplicates(subset=merge_cols, keep='last')
            combined_df = combined_df.sort_values(['Report_Year', 'Report_Half', 'Sector', 'Market'])
            
            # Save results with corrected filename
            self.csv_path = self.output_dir / "historical_cap_rates.csv"
            self._save_csv(combined_df)
            self._save_json(combined_df)
            
            # Save combined metadata
            combined_metadata['unique_periods'] = sorted(list(set(combined_metadata['report_periods'])))
            self._save_metadata(combined_metadata, len(combined_df), len(combined_df), 0)
            
            return ProcessingResult(
                success=True,
                total_records=len(combined_df),
                new_records=len(combined_df),  # All records are "new" in this context
                updated_records=0,
                metadata=combined_metadata
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                total_records=0,
                new_records=0,
                updated_records=0,
                errors=[f"Combining results failed: {str(e)}"],
                metadata={}
            ) 