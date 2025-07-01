/**
 * DataService - Handles all data loading and processing
 */
class DataService {
    constructor() {
        this.data = null;
        this.processedData = null;
    }

    /**
     * Load cap rate data from CSV
     */
    async loadCapRateData() {
        try {
            const response = await fetch('historical_cap_rates.csv');
            const csvText = await response.text();
            this.data = this.parseCSV(csvText);
            this.processedData = this.processData(this.data);
            return this.processedData;
        } catch (error) {
            console.error('Error loading data:', error);
            throw new Error('Failed to load cap rate data');
        }
    }

    /**
     * Parse CSV text into structured data
     */
    parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        
        return lines.slice(1).map(line => {
            const values = line.split(',').map(v => v.trim());
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index];
            });
            return row;
        });
    }

    /**
     * Process raw data for analysis
     */
    processData(rawData) {
        // Filter valid data - must have proper year, half, and cap rates
        const validData = rawData.filter(row => {
            // Must have valid year (2020-2025)
            const year = parseInt(row.Report_Year);
            if (isNaN(year) || year < 2020 || year > 2025) return false;
            
            // Must have valid half (1 or 2)
            const half = parseInt(row.Report_Half);
            if (isNaN(half) || (half !== 1 && half !== 2)) return false;
            
            // Must have valid sector
            if (!row.Sector || row.Sector.length < 3) return false;
            
            // Must have at least one valid cap rate
            return this.isValidCapRate(row.H1_Low) || 
                   this.isValidCapRate(row.H1_High) || 
                   this.isValidCapRate(row.H2_Low) || 
                   this.isValidCapRate(row.H2_High);
        });

        // Add calculated fields
        return validData.map(row => ({
            ...row,
            h1_avg: this.calculateAverage(row.H1_Low, row.H1_High),
            h2_avg: this.calculateAverage(row.H2_Low, row.H2_High),
            period_key: `${row.Report_Year}_${row.Report_Half}`,
            is_valid_market: this.isValidMarket(row.Market)
        }));
    }

    /**
     * Check if a value is a valid cap rate (1-15%)
     */
    isValidCapRate(value) {
        const num = parseFloat(value);
        return !isNaN(num) && num >= 1 && num <= 15;
    }

    /**
     * Check if market name is valid (filter out obvious invalid entries)
     */
    isValidMarket(market) {
        if (!market || market.length < 3) return false;
        
        const trimmed = market.trim();
        
        // Filter out obvious invalid entries
        const invalidPatterns = [
            /^Market$/i,
            /^Looking Forward/i,
            /^Figure/i,
            /^After/i,
            /^But fortune/i,
            /^the$/i,
            /^\d{4}$/,  // Years like "2023"
            /^\d+%$/,   // Percentages like "25%"
            /^[^a-zA-Z]/,  // Starts with non-letter
            /^\s*$/     // Empty or whitespace only
        ];
        
        // Check against invalid patterns
        for (const pattern of invalidPatterns) {
            if (pattern.test(trimmed)) {
                return false;
            }
        }
        
        // Must contain at least one letter and be reasonable length
        if (!/[a-zA-Z]/.test(trimmed) || trimmed.length > 50) {
            return false;
        }
        
        return true;
    }

    /**
     * Calculate average of two cap rates
     */
    calculateAverage(low, high) {
        const lowNum = parseFloat(low);
        const highNum = parseFloat(high);
        
        if (isNaN(lowNum) && isNaN(highNum)) return null;
        if (isNaN(lowNum)) return highNum;
        if (isNaN(highNum)) return lowNum;
        
        return (lowNum + highNum) / 2;
    }

    /**
     * Get unique sectors
     */
    getSectors() {
        if (!this.processedData) return [];
        return [...new Set(this.processedData.map(row => row.Sector))]
            .filter(Boolean)
            .sort();
    }

    /**
     * Get unique markets
     */
    getMarkets() {
        if (!this.processedData) return [];
        return [...new Set(this.processedData
            .filter(row => this.isValidMarket(row.Market))
            .map(row => row.Market)
        )]
            .filter(Boolean)
            .sort();
    }

    /**
     * Get unique time periods
     */
    getPeriods() {
        if (!this.processedData) return [];
        const periods = [...new Set(this.processedData.map(row => row.period_key))];
        
        // Sort periods chronologically (2021_1, 2021_2, 2022_1, etc.)
        return periods.sort((a, b) => {
            const [yearA, halfA] = a.split('_').map(Number);
            const [yearB, halfB] = b.split('_').map(Number);
            
            if (yearA !== yearB) return yearA - yearB;
            return halfA - halfB;
        });
    }

    /**
     * Filter data by criteria
     */
    filterData(criteria = {}) {
        if (!this.processedData) return [];
        
        return this.processedData.filter(row => {
            if (criteria.sector && row.Sector !== criteria.sector) return false;
            if (criteria.market && row.Market !== criteria.market) return false;
            if (criteria.period && row.period_key !== criteria.period) return false;
            if (criteria.validMarketOnly && !row.is_valid_market) return false;
            
            return true;
        });
    }

    /**
     * Get time series data for charts
     */
    getTimeSeriesData(sector = null, market = null) {
        const filtered = this.filterData({ 
            sector, 
            market, 
            validMarketOnly: true 
        });
        
        const periods = this.getPeriods();
        const timeSeriesData = [];
        
        periods.forEach(period => {
            const periodData = filtered.filter(row => row.period_key === period);
            if (periodData.length > 0) {
                const avgRates = periodData
                    .map(row => row.h1_avg || row.h2_avg)
                    .filter(rate => rate !== null);
                
                if (avgRates.length > 0) {
                    const avgRate = avgRates.reduce((sum, rate) => sum + rate, 0) / avgRates.length;
                    timeSeriesData.push({
                        period,
                        avgRate: parseFloat(avgRate.toFixed(2)),
                        count: periodData.length
                    });
                }
            }
        });
        
        return timeSeriesData;
    }

    /**
     * Get sector comparison data
     */
    getSectorComparison() {
        const sectors = this.getSectors();
        return sectors.map(sector => {
            const sectorData = this.filterData({ sector, validMarketOnly: true });
            const rates = sectorData
                .map(row => row.h1_avg || row.h2_avg)
                .filter(rate => rate !== null);
            
            const avgRate = rates.length > 0 
                ? rates.reduce((sum, rate) => sum + rate, 0) / rates.length 
                : 0;
            
            return {
                sector,
                avgRate: parseFloat(avgRate.toFixed(2)),
                count: sectorData.length
            };
        }).filter(item => item.avgRate > 0);
    }

    /**
     * Get market ranking data
     */
    getMarketRanking(limit = 10) {
        const markets = this.getMarkets();
        const marketData = markets.map(market => {
            const data = this.filterData({ market, validMarketOnly: true });
            const rates = data
                .map(row => row.h1_avg || row.h2_avg)
                .filter(rate => rate !== null);
            
            const avgRate = rates.length > 0 
                ? rates.reduce((sum, rate) => sum + rate, 0) / rates.length 
                : 0;
            
            return {
                market,
                avgRate: parseFloat(avgRate.toFixed(2)),
                count: data.length
            };
        }).filter(item => item.avgRate > 0);
        
        return marketData
            .sort((a, b) => b.avgRate - a.avgRate)
            .slice(0, limit);
    }

    /**
     * Get multi-sector time series data for showing all asset classes as separate lines
     */
    getMultiSectorTimeSeriesData(filterSector = null, filterMarket = null) {
        const filtered = this.filterData({ 
            sector: filterSector, 
            market: filterMarket, 
            validMarketOnly: true 
        });
        
        const periods = this.getPeriods();
        const sectors = filterSector ? [filterSector] : this.getSectors();
        
        const result = {
            periods: periods,
            sectors: sectors,
            data: {}
        };
        
        // Initialize data structure for each sector
        sectors.forEach(sector => {
            result.data[sector] = [];
        });
        
        // Calculate average rates for each sector in each period
        periods.forEach(period => {
            sectors.forEach(sector => {
                const sectorPeriodData = filtered.filter(row => 
                    row.period_key === period && row.Sector === sector
                );
                
                if (sectorPeriodData.length > 0) {
                    const rates = sectorPeriodData
                        .map(row => row.h1_avg || row.h2_avg)
                        .filter(rate => rate !== null);
                    
                    if (rates.length > 0) {
                        const avgRate = rates.reduce((sum, rate) => sum + rate, 0) / rates.length;
                        result.data[sector].push(parseFloat(avgRate.toFixed(2)));
                    } else {
                        result.data[sector].push(null);
                    }
                } else {
                    result.data[sector].push(null);
                }
            });
        });
        
        return result;
    }

    /**
     * Get detailed market analysis with trends and comparisons
     */
    getMarketAnalysis(market) {
        if (!market) return null;
        
        const marketData = this.filterData({ market, validMarketOnly: true });
        if (marketData.length === 0) return null;
        
        const periods = this.getPeriods();
        const sectors = this.getSectors();
        
        const analysis = {
            market: market,
            totalRecords: marketData.length,
            sectors: {},
            trends: [],
            summary: {}
        };
        
        // Analyze by sector
        sectors.forEach(sector => {
            const sectorData = marketData.filter(row => row.Sector === sector);
            if (sectorData.length > 0) {
                const rates = sectorData
                    .map(row => row.h1_avg || row.h2_avg)
                    .filter(rate => rate !== null);
                
                if (rates.length > 0) {
                    const avgRate = rates.reduce((sum, rate) => sum + rate, 0) / rates.length;
                    const minRate = Math.min(...rates);
                    const maxRate = Math.max(...rates);
                    
                    analysis.sectors[sector] = {
                        avgRate: parseFloat(avgRate.toFixed(2)),
                        minRate: parseFloat(minRate.toFixed(2)),
                        maxRate: parseFloat(maxRate.toFixed(2)),
                        count: rates.length,
                        spread: parseFloat((maxRate - minRate).toFixed(2))
                    };
                }
            }
        });
        
        // Calculate trends over time
        periods.forEach(period => {
            const periodData = marketData.filter(row => row.period_key === period);
            if (periodData.length > 0) {
                const rates = periodData
                    .map(row => row.h1_avg || row.h2_avg)
                    .filter(rate => rate !== null);
                
                if (rates.length > 0) {
                    const avgRate = rates.reduce((sum, rate) => sum + rate, 0) / rates.length;
                    analysis.trends.push({
                        period: period,
                        avgRate: parseFloat(avgRate.toFixed(2)),
                        count: rates.length
                    });
                }
            }
        });
        
        // Calculate summary statistics
        const allRates = marketData
            .map(row => row.h1_avg || row.h2_avg)
            .filter(rate => rate !== null);
        
        if (allRates.length > 0) {
            analysis.summary = {
                overallAvg: parseFloat((allRates.reduce((sum, rate) => sum + rate, 0) / allRates.length).toFixed(2)),
                overallMin: parseFloat(Math.min(...allRates).toFixed(2)),
                overallMax: parseFloat(Math.max(...allRates).toFixed(2)),
                volatility: this.calculateVolatility(allRates)
            };
        }
        
        return analysis;
    }

    /**
     * Calculate volatility (standard deviation) of rates
     */
    calculateVolatility(rates) {
        if (rates.length < 2) return 0;
        
        const mean = rates.reduce((sum, rate) => sum + rate, 0) / rates.length;
        const squaredDiffs = rates.map(rate => Math.pow(rate - mean, 2));
        const variance = squaredDiffs.reduce((sum, diff) => sum + diff, 0) / rates.length;
        
        return parseFloat(Math.sqrt(variance).toFixed(2));
    }

    /**
     * Get sector performance comparison with rankings
     */
    getSectorPerformanceRanking() {
        const sectors = this.getSectors();
        const performance = sectors.map(sector => {
            const sectorData = this.filterData({ sector, validMarketOnly: true });
            const rates = sectorData
                .map(row => row.h1_avg || row.h2_avg)
                .filter(rate => rate !== null);
            
            if (rates.length === 0) return null;
            
            const avgRate = rates.reduce((sum, rate) => sum + rate, 0) / rates.length;
            const volatility = this.calculateVolatility(rates);
            
            return {
                sector: sector,
                avgRate: parseFloat(avgRate.toFixed(2)),
                volatility: volatility,
                count: rates.length,
                riskAdjustedReturn: parseFloat((avgRate / (volatility || 1)).toFixed(2))
            };
        }).filter(Boolean);
        
        return performance.sort((a, b) => b.avgRate - a.avgRate);
    }

    /**
     * Get advanced statistics for dashboard
     */
    getAdvancedStatistics() {
        const data = this.filterData({ validMarketOnly: true });
        const allRates = data
            .map(row => row.h1_avg || row.h2_avg)
            .filter(rate => rate !== null);
        
        if (allRates.length === 0) return null;
        
        const sorted = [...allRates].sort((a, b) => a - b);
        const mean = allRates.reduce((sum, rate) => sum + rate, 0) / allRates.length;
        
        return {
            mean: parseFloat(mean.toFixed(2)),
            median: parseFloat(sorted[Math.floor(sorted.length / 2)].toFixed(2)),
            q1: parseFloat(sorted[Math.floor(sorted.length * 0.25)].toFixed(2)),
            q3: parseFloat(sorted[Math.floor(sorted.length * 0.75)].toFixed(2)),
            min: parseFloat(sorted[0].toFixed(2)),
            max: parseFloat(sorted[sorted.length - 1].toFixed(2)),
            stdDev: this.calculateVolatility(allRates),
            count: allRates.length
        };
    }
}

// Export for global use
window.DataService = DataService; 