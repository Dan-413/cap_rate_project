/**
 * MarketValidationService - Handles market data validation and property value derivation
 */
class MarketValidationService {
    constructor(dataService) {
        this.dataService = dataService;
    }

    /**
     * Get market cap rate for specific sector, market, and time period
     */
    getMarketCapRate(sector, market, period) {
        if (!sector || !market || !period) {
            return null;
        }

        const filteredData = this.dataService.filterData({
            sector: sector,
            market: market,
            period: period,
            validMarketOnly: true
        });

        if (filteredData.length === 0) {
            return null;
        }

        // Calculate average cap rate for the filtered data
        const rates = [];
        filteredData.forEach(row => {
            if (row.h1_avg) rates.push(row.h1_avg);
            if (row.h2_avg) rates.push(row.h2_avg);
        });

        if (rates.length === 0) {
            return null;
        }

        const avgRate = rates.reduce((sum, rate) => sum + rate, 0) / rates.length;
        const minRate = Math.min(...rates);
        const maxRate = Math.max(...rates);

        return {
            avgRate: parseFloat(avgRate.toFixed(2)),
            minRate: parseFloat(minRate.toFixed(2)),
            maxRate: parseFloat(maxRate.toFixed(2)),
            dataPoints: rates.length,
            sector: sector,
            market: market,
            period: period
        };
    }

    /**
     * Derive property value from NOI and market cap rate
     */
    derivePropertyValue(annualNOI, marketCapRate) {
        if (!annualNOI || !marketCapRate || marketCapRate <= 0) {
            return null;
        }

        // Property Value = NOI / Cap Rate
        const derivedValue = annualNOI / (marketCapRate / 100);
        
        return {
            derivedValue: Math.round(derivedValue),
            marketCapRate: marketCapRate,
            annualNOI: annualNOI,
            calculation: `$${annualNOI.toLocaleString()} ÷ ${marketCapRate}% = $${Math.round(derivedValue).toLocaleString()}`
        };
    }

    /**
     * Validate property value against market data
     */
    validatePropertyValue(propertyValue, annualNOI, sector, market, period) {
        const marketData = this.getMarketCapRate(sector, market, period);
        if (!marketData) {
            return {
                isValid: false,
                reason: 'No market data available for selected criteria',
                marketData: null
            };
        }

        const dealCapRate = (annualNOI / propertyValue) * 100;
        const marketRange = {
            min: marketData.minRate,
            max: marketData.maxRate,
            avg: marketData.avgRate
        };

        // Determine if deal cap rate is within reasonable market range
        const isWithinRange = dealCapRate >= (marketRange.min * 0.8) && dealCapRate <= (marketRange.max * 1.2);
        const variance = Math.abs(dealCapRate - marketRange.avg);
        const variancePercent = (variance / marketRange.avg) * 100;

        let validation = 'WITHIN_RANGE';
        let message = 'Property value aligns with market data';

        if (dealCapRate < marketRange.min * 0.8) {
            validation = 'OVERVALUED';
            message = 'Property may be overvalued relative to market cap rates';
        } else if (dealCapRate > marketRange.max * 1.2) {
            validation = 'UNDERVALUED';
            message = 'Property may be undervalued relative to market cap rates';
        } else if (variancePercent > 15) {
            validation = 'REVIEW_REQUIRED';
            message = 'Significant variance from market average - review recommended';
        }

        return {
            isValid: isWithinRange,
            validation: validation,
            message: message,
            dealCapRate: parseFloat(dealCapRate.toFixed(2)),
            marketData: marketData,
            variance: parseFloat(variance.toFixed(2)),
            variancePercent: parseFloat(variancePercent.toFixed(1))
        };
    }

    /**
     * Calculate implied LTV based on loan amount and derived property value
     */
    calculateImpliedLTV(loanAmount, derivedPropertyValue) {
        if (!loanAmount || !derivedPropertyValue || derivedPropertyValue <= 0) {
            return null;
        }

        const impliedLTV = (loanAmount / derivedPropertyValue) * 100;
        
        let riskLevel = 'CONSERVATIVE';
        let message = 'Conservative LTV ratio';

        if (impliedLTV > 85) {
            riskLevel = 'HIGH_RISK';
            message = 'High LTV ratio - increased credit risk';
        } else if (impliedLTV > 80) {
            riskLevel = 'AGGRESSIVE';
            message = 'Aggressive LTV ratio';
        } else if (impliedLTV > 75) {
            riskLevel = 'STANDARD';
            message = 'Standard LTV ratio';
        }

        return {
            impliedLTV: parseFloat(impliedLTV.toFixed(1)),
            riskLevel: riskLevel,
            message: message,
            loanAmount: loanAmount,
            derivedPropertyValue: derivedPropertyValue
        };
    }

    /**
     * Comprehensive market validation analysis
     */
    performMarketValidation(inputs) {
        const {
            annualNOI,
            loanAmount,
            sector,
            market,
            period,
            propertyValue = null // Optional - if provided, validates; if not, derives
        } = inputs;

        const results = {
            marketData: null,
            derivedValue: null,
            validation: null,
            impliedLTV: null,
            recommendations: []
        };

        // Get market data
        results.marketData = this.getMarketCapRate(sector, market, period);
        if (!results.marketData) {
            return {
                ...results,
                error: 'No market data available for selected criteria'
            };
        }

        // If property value provided, validate it; otherwise derive it
        if (propertyValue) {
            results.validation = this.validatePropertyValue(propertyValue, annualNOI, sector, market, period);
            results.impliedLTV = this.calculateImpliedLTV(loanAmount, propertyValue);
        } else {
            results.derivedValue = this.derivePropertyValue(annualNOI, results.marketData.avgRate);
            if (results.derivedValue) {
                results.impliedLTV = this.calculateImpliedLTV(loanAmount, results.derivedValue.derivedValue);
            }
        }

        // Generate recommendations
        results.recommendations = this.generateRecommendations(results);

        return results;
    }

    /**
     * Generate actionable recommendations based on validation results
     */
    generateRecommendations(results) {
        const recommendations = [];

        if (results.validation) {
            switch (results.validation.validation) {
                case 'OVERVALUED':
                    recommendations.push('Consider reducing loan amount or requiring additional equity');
                    recommendations.push('Review appraisal methodology and comparables');
                    break;
                case 'UNDERVALUED':
                    recommendations.push('Opportunity for higher loan amount or better pricing');
                    recommendations.push('Verify property condition and market positioning');
                    break;
                case 'REVIEW_REQUIRED':
                    recommendations.push('Conduct detailed market analysis');
                    recommendations.push('Consider third-party valuation review');
                    break;
            }
        }

        if (results.impliedLTV) {
            switch (results.impliedLTV.riskLevel) {
                case 'HIGH_RISK':
                    recommendations.push('Require additional equity injection to reduce LTV');
                    recommendations.push('Consider enhanced loan terms or guarantees');
                    break;
                case 'AGGRESSIVE':
                    recommendations.push('Review cash flow stability and tenant quality');
                    recommendations.push('Consider debt service reserve requirements');
                    break;
            }
        }

        return recommendations;
    }
}

// Export for global use
window.MarketValidationService = MarketValidationService; 