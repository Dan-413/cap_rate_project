/**
 * Unit Tests for DataService
 * Run with: npm test or node --test test_data_service.test.js
 */

import { describe, it, assert, beforeEach } from 'node:test';
import DataService from '../../js/services/DataService.js';

describe('DataService', () => {
    let dataService;
    let mockCSVData;

    beforeEach(() => {
        dataService = new DataService();
        
        // Mock CSV data for testing
        mockCSVData = `Sector,Subsector,Region,Market,H1_Low,H1_High,H2_Low,H2_High,Report_Year,Report_Half
Industrial,Warehouse,West,Los Angeles,4.5,5.5,4.2,5.2,2024,H1
Multifamily,Garden,East,New York,3.8,4.8,3.5,4.5,2024,H1
Office,Class A,South,Dallas,6.0,7.0,5.8,6.8,2024,H1
Retail,Shopping Center,North,Chicago,5.5,6.5,5.2,6.2,2024,H1
Hotel,Full Service,West,San Francisco,7.0,8.0,6.8,7.8,2024,H1`;
    });

    describe('parseCSV()', () => {
        it('should parse CSV text correctly', () => {
            const result = dataService.parseCSV(mockCSVData);
            
            assert.strictEqual(result.length, 5);
            assert.strictEqual(result[0].Sector, 'Industrial');
            assert.strictEqual(result[0].Market, 'Los Angeles');
            assert.strictEqual(result[0].H1_Low, '4.5');
        });

        it('should handle empty CSV', () => {
            const result = dataService.parseCSV('');
            assert.strictEqual(result.length, 0);
        });

        it('should handle CSV with only headers', () => {
            const result = dataService.parseCSV('Sector,Market');
            assert.strictEqual(result.length, 0);
        });
    });

    describe('isValidCapRate()', () => {
        it('should validate cap rates correctly', () => {
            assert.strictEqual(dataService.isValidCapRate('5.5'), true);
            assert.strictEqual(dataService.isValidCapRate('1.0'), true);
            assert.strictEqual(dataService.isValidCapRate('15.0'), true);
            
            assert.strictEqual(dataService.isValidCapRate('0.5'), false);
            assert.strictEqual(dataService.isValidCapRate('16.0'), false);
            assert.strictEqual(dataService.isValidCapRate('abc'), false);
            assert.strictEqual(dataService.isValidCapRate(''), false);
        });
    });

    describe('isValidMarket()', () => {
        it('should validate market names correctly', () => {
            assert.strictEqual(dataService.isValidMarket('New York'), true);
            assert.strictEqual(dataService.isValidMarket('Los Angeles'), true);
            assert.strictEqual(dataService.isValidMarket('Chicago'), true);
            
            assert.strictEqual(dataService.isValidMarket('xy'), false);
            assert.strictEqual(dataService.isValidMarket(''), false);
            assert.strictEqual(dataService.isValidMarket(null), false);
        });
    });

    describe('calculateAverage()', () => {
        it('should calculate average correctly', () => {
            assert.strictEqual(dataService.calculateAverage('4.0', '6.0'), 5.0);
            assert.strictEqual(dataService.calculateAverage('3.5', '4.5'), 4.0);
        });

        it('should handle missing values', () => {
            assert.strictEqual(dataService.calculateAverage('', '6.0'), 6.0);
            assert.strictEqual(dataService.calculateAverage('4.0', ''), 4.0);
            assert.strictEqual(dataService.calculateAverage('', ''), null);
        });

        it('should handle invalid values', () => {
            assert.strictEqual(dataService.calculateAverage('abc', '6.0'), 6.0);
            assert.strictEqual(dataService.calculateAverage('4.0', 'xyz'), 4.0);
        });
    });

    describe('processData()', () => {
        it('should process raw data correctly', () => {
            const rawData = dataService.parseCSV(mockCSVData);
            const processed = dataService.processData(rawData);
            
            assert.strictEqual(processed.length, 5);
            
            // Check calculated fields
            assert.strictEqual(processed[0].h1_avg, 5.0); // (4.5 + 5.5) / 2
            assert.strictEqual(processed[0].h2_avg, 4.7); // (4.2 + 5.2) / 2
            assert.strictEqual(processed[0].period_key, '2024_H1');
            assert.strictEqual(processed[0].is_valid_market, true);
        });

        it('should filter out invalid data', () => {
            const invalidData = `Sector,Market,H1_Low,H1_High,H2_Low,H2_High,Report_Year,Report_Half
Industrial,Los Angeles,abc,xyz,def,ghi,2024,H1`;
            
            const rawData = dataService.parseCSV(invalidData);
            const processed = dataService.processData(rawData);
            
            assert.strictEqual(processed.length, 0);
        });
    });

    describe('getSectors()', () => {
        it('should return unique sectors', () => {
            const rawData = dataService.parseCSV(mockCSVData);
            dataService.processedData = dataService.processData(rawData);
            
            const sectors = dataService.getSectors();
            
            assert.strictEqual(sectors.length, 5);
            assert.ok(sectors.includes('Industrial'));
            assert.ok(sectors.includes('Multifamily'));
            assert.ok(sectors.includes('Office'));
        });

        it('should handle empty data', () => {
            const sectors = dataService.getSectors();
            assert.strictEqual(sectors.length, 0);
        });
    });

    describe('getMarkets()', () => {
        it('should return valid markets only', () => {
            const rawData = dataService.parseCSV(mockCSVData);
            dataService.processedData = dataService.processData(rawData);
            
            const markets = dataService.getMarkets();
            
            assert.ok(markets.length > 0);
            assert.ok(markets.includes('Los Angeles'));
            assert.ok(markets.includes('New York'));
        });
    });

    describe('filterData()', () => {
        beforeEach(() => {
            const rawData = dataService.parseCSV(mockCSVData);
            dataService.processedData = dataService.processData(rawData);
        });

        it('should filter by sector', () => {
            const filtered = dataService.filterData({ sector: 'Industrial' });
            
            assert.strictEqual(filtered.length, 1);
            assert.strictEqual(filtered[0].Sector, 'Industrial');
        });

        it('should filter by market', () => {
            const filtered = dataService.filterData({ market: 'Los Angeles' });
            
            assert.strictEqual(filtered.length, 1);
            assert.strictEqual(filtered[0].Market, 'Los Angeles');
        });

        it('should filter by multiple criteria', () => {
            const filtered = dataService.filterData({ 
                sector: 'Industrial', 
                market: 'Los Angeles' 
            });
            
            assert.strictEqual(filtered.length, 1);
            assert.strictEqual(filtered[0].Sector, 'Industrial');
            assert.strictEqual(filtered[0].Market, 'Los Angeles');
        });

        it('should return empty array for non-matching criteria', () => {
            const filtered = dataService.filterData({ sector: 'NonExistent' });
            assert.strictEqual(filtered.length, 0);
        });
    });

    describe('getTimeSeriesData()', () => {
        beforeEach(() => {
            const timeSeriesCSV = `Sector,Market,H1_Low,H1_High,H2_Low,H2_High,Report_Year,Report_Half
Industrial,Los Angeles,4.5,5.5,4.2,5.2,2023,H1
Industrial,Los Angeles,4.8,5.8,4.5,5.5,2023,H2
Industrial,Los Angeles,5.0,6.0,4.8,5.8,2024,H1`;
            
            const rawData = dataService.parseCSV(timeSeriesCSV);
            dataService.processedData = dataService.processData(rawData);
        });

        it('should return time series data', () => {
            const timeSeries = dataService.getTimeSeriesData('Industrial', 'Los Angeles');
            
            assert.strictEqual(timeSeries.length, 3);
            assert.strictEqual(timeSeries[0].period, '2023_H1');
            assert.ok(timeSeries[0].avgRate > 0);
        });

        it('should handle no filters', () => {
            const timeSeries = dataService.getTimeSeriesData();
            
            assert.ok(timeSeries.length > 0);
        });
    });

    describe('getSectorComparison()', () => {
        beforeEach(() => {
            const rawData = dataService.parseCSV(mockCSVData);
            dataService.processedData = dataService.processData(rawData);
        });

        it('should return sector comparison data', () => {
            const comparison = dataService.getSectorComparison();
            
            assert.ok(comparison.length > 0);
            assert.ok(comparison[0].sector);
            assert.ok(comparison[0].avgRate > 0);
            assert.ok(comparison[0].count > 0);
        });
    });

    describe('getMarketRanking()', () => {
        beforeEach(() => {
            const rawData = dataService.parseCSV(mockCSVData);
            dataService.processedData = dataService.processData(rawData);
        });

        it('should return market ranking data', () => {
            const ranking = dataService.getMarketRanking(3);
            
            assert.ok(ranking.length <= 3);
            
            if (ranking.length > 1) {
                // Should be sorted by avgRate descending
                assert.ok(ranking[0].avgRate >= ranking[1].avgRate);
            }
        });

        it('should limit results correctly', () => {
            const ranking = dataService.getMarketRanking(2);
            assert.ok(ranking.length <= 2);
        });
    });
});

// Export for Node.js test runner
export { describe, it, assert, beforeEach }; 