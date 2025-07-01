/**
 * DealModel - Handles all deal calculations and data management
 */
class DealModel {
    constructor(propertyValue, annualNOI, loanAmount, interestRate, amortizationYears, sofrRate) {
        this.propertyValue = propertyValue;
        this.annualNOI = annualNOI;
        this.loanAmount = loanAmount;
        this.interestRate = interestRate;
        this.amortizationYears = amortizationYears;
        this.sofrRate = sofrRate;
        
        this._calculations = null;
    }

    /**
     * Calculate all deal metrics
     */
    calculate() {
        if (this._calculations) {
            return this._calculations;
        }

        const actualCapRate = (this.annualNOI / this.propertyValue) * 100;
        const actualLTV = (this.loanAmount / this.propertyValue) * 100;
        
        // Calculate monthly payment using amortization formula
        const monthlyRate = (this.interestRate / 100) / 12;
        const totalPayments = this.amortizationYears * 12;
        
        let monthlyPayment;
        if (monthlyRate === 0) {
            monthlyPayment = this.loanAmount / totalPayments;
        } else {
            monthlyPayment = this.loanAmount * 
                (monthlyRate * Math.pow(1 + monthlyRate, totalPayments)) / 
                (Math.pow(1 + monthlyRate, totalPayments) - 1);
        }
        
        const annualDebtService = monthlyPayment * 12;
        const dscr = this.annualNOI / annualDebtService;
        const debtConstant = (annualDebtService / this.loanAmount) * 100;
        const spread = (this.interestRate - this.sofrRate) * 100; // basis points over SOFR
        const breakEvenNOI = annualDebtService;

        this._calculations = {
            actualCapRate,
            actualLTV,
            dscr,
            annualDebtService,
            debtConstant,
            spread,
            breakEvenNOI,
            monthlyPayment
        };

        return this._calculations;
    }

    /**
     * Get credit decision based on calculated metrics
     */
    getCreditDecision() {
        const { dscr, actualLTV, actualCapRate } = this.calculate();
        
        // Enhanced credit decision matrix for commercial real estate
        // Strong deals: High DSCR, Conservative LTV, Attractive Cap Rate
        if (dscr >= 1.40 && actualLTV <= 70 && actualCapRate >= 6.0) {
            return { decision: '✅ STRONG APPROVE', color: '#1ECD7D', risk: 'LOW' };
        }
        // Standard approval: Good metrics across the board
        else if (dscr >= 1.30 && actualLTV <= 75 && actualCapRate >= 5.5) {
            return { decision: '✅ APPROVE', color: '#1ECD7D', risk: 'LOW' };
        }
        // Conditional approval: Acceptable metrics with conditions
        else if (dscr >= 1.25 && actualLTV <= 80 && actualCapRate >= 4.5) {
            return { decision: '⚠️ CONDITIONAL', color: '#C17B42', risk: 'MEDIUM' };
        }
        // Review required: Marginal metrics need deeper analysis
        else if (dscr >= 1.20 && actualLTV <= 85 && actualCapRate >= 4.0) {
            return { decision: '🔍 REVIEW REQUIRED', color: '#371CA1', risk: 'HIGH' };
        }
        // Weak metrics: High risk but might be acceptable with mitigants
        else if (dscr >= 1.15 && actualLTV <= 90) {
            return { decision: '⚡ HIGH RISK', color: '#DC3545', risk: 'VERY_HIGH' };
        }
        // Decline: Metrics don't meet minimum standards
        else {
            return { decision: '❌ DECLINE', color: '#DC3545', risk: 'UNACCEPTABLE' };
        }
    }

    /**
     * Get comprehensive deal analysis
     */
    getDealAnalysis() {
        const calculations = this.calculate();
        const creditDecision = this.getCreditDecision();
        
        const analysis = {
            calculations,
            creditDecision,
            risks: [],
            strengths: [],
            recommendations: []
        };

        // Risk assessment
        if (calculations.dscr < 1.25) {
            analysis.risks.push('Low DSCR indicates tight cash flow coverage');
        }
        if (calculations.actualLTV > 80) {
            analysis.risks.push('High LTV increases credit risk');
        }
        if (calculations.actualCapRate < 5.0) {
            analysis.risks.push('Low cap rate may indicate overvaluation');
        }

        // Strength assessment
        if (calculations.dscr >= 1.35) {
            analysis.strengths.push('Strong debt service coverage');
        }
        if (calculations.actualLTV <= 70) {
            analysis.strengths.push('Conservative loan-to-value ratio');
        }
        if (calculations.actualCapRate >= 6.0) {
            analysis.strengths.push('Attractive cap rate provides good returns');
        }

        // Recommendations
        if (calculations.actualLTV > 75) {
            analysis.recommendations.push('Consider requiring additional equity injection');
        }
        if (calculations.dscr < 1.30) {
            analysis.recommendations.push('Review operating expense assumptions');
        }

        return analysis;
    }

    /**
     * Validate inputs before calculation
     */
    validateInputs() {
        const errors = [];
        
        if (this.propertyValue <= 0) errors.push('Property value must be positive');
        if (this.annualNOI <= 0) errors.push('Annual NOI must be positive');
        if (this.loanAmount <= 0) errors.push('Loan amount must be positive');
        if (this.interestRate <= 0 || this.interestRate > 20) errors.push('Interest rate must be between 0% and 20%');
        if (this.amortizationYears < 1 || this.amortizationYears > 50) errors.push('Amortization must be between 1 and 50 years');
        if (this.sofrRate < 0 || this.sofrRate > 10) errors.push('SOFR rate must be between 0% and 10%');
        
        // Logical validations
        if (this.loanAmount > this.propertyValue) errors.push('Loan amount cannot exceed property value');
        if (this.annualNOI > this.propertyValue * 0.2) errors.push('NOI seems unusually high relative to property value');
        if (this.interestRate < this.sofrRate) errors.push('Interest rate should be higher than SOFR rate');
        
        return errors;
    }

    /**
     * Get risk scoring for DSCR
     */
    getDSCRRisk(dscr) {
        if (dscr >= 1.35) return { color: '#1ECD7D', level: 'STRONG' };
        if (dscr >= 1.25) return { color: '#371CA1', level: 'ACCEPTABLE' };
        if (dscr >= 1.15) return { color: '#C17B42', level: 'MARGINAL' };
        return { color: '#DC3545', level: 'WEAK' };
    }

    /**
     * Get risk scoring for LTV
     */
    getLTVRisk(ltv) {
        if (ltv <= 70) return { color: '#1ECD7D', level: 'CONSERVATIVE' };
        if (ltv <= 75) return { color: '#371CA1', level: 'STANDARD' };
        if (ltv <= 80) return { color: '#C17B42', level: 'AGGRESSIVE' };
        return { color: '#DC3545', level: 'HIGH_RISK' };
    }

    /**
     * Export deal data for analysis
     */
    toJSON() {
        return {
            inputs: {
                propertyValue: this.propertyValue,
                annualNOI: this.annualNOI,
                loanAmount: this.loanAmount,
                interestRate: this.interestRate,
                amortizationYears: this.amortizationYears,
                sofrRate: this.sofrRate
            },
            calculations: this.calculate(),
            creditDecision: this.getCreditDecision()
        };
    }

    /**
     * Calculate metrics with derived property value from market data
     */
    calculateWithDerivedValue(derivedPropertyValue) {
        // Create temporary instance with derived value
        const tempModel = new DealModel(
            derivedPropertyValue,
            this.annualNOI,
            this.loanAmount,
            this.interestRate,
            this.amortizationYears,
            this.sofrRate
        );
        
        const calculations = tempModel.calculate();
        
        return {
            ...calculations,
            isDerived: true,
            derivedPropertyValue: derivedPropertyValue,
            originalPropertyValue: this.propertyValue
        };
    }

    /**
     * Calculate what property value would be needed for target LTV
     */
    calculateRequiredPropertyValue(targetLTV) {
        if (targetLTV <= 0 || targetLTV > 100) {
            return null;
        }
        
        // Property Value = Loan Amount / (Target LTV / 100)
        const requiredValue = this.loanAmount / (targetLTV / 100);
        
        // Calculate what cap rate this would imply
        const impliedCapRate = (this.annualNOI / requiredValue) * 100;
        
        return {
            requiredPropertyValue: Math.round(requiredValue),
            targetLTV: targetLTV,
            impliedCapRate: parseFloat(impliedCapRate.toFixed(2)),
            loanAmount: this.loanAmount,
            annualNOI: this.annualNOI
        };
    }

    /**
     * Calculate what loan amount would be needed for target LTV
     */
    calculateRequiredLoanAmount(targetLTV) {
        if (targetLTV <= 0 || targetLTV > 100) {
            return null;
        }
        
        // Loan Amount = Property Value * (Target LTV / 100)
        const requiredLoanAmount = this.propertyValue * (targetLTV / 100);
        
        return {
            requiredLoanAmount: Math.round(requiredLoanAmount),
            targetLTV: targetLTV,
            propertyValue: this.propertyValue,
            currentLoanAmount: this.loanAmount,
            difference: Math.round(requiredLoanAmount - this.loanAmount)
        };
    }

    /**
     * Perform scenario analysis with different cap rates
     */
    scenarioAnalysis(capRateRange) {
        const scenarios = [];
        const { minRate, maxRate, avgRate } = capRateRange;
        
        const rates = [minRate, avgRate, maxRate];
        const labels = ['Conservative', 'Average', 'Aggressive'];
        
        rates.forEach((rate, index) => {
            if (rate > 0) {
                // Calculate property value at this cap rate
                const scenarioValue = this.annualNOI / (rate / 100);
                const scenarioLTV = (this.loanAmount / scenarioValue) * 100;
                
                scenarios.push({
                    label: labels[index],
                    capRate: rate,
                    propertyValue: Math.round(scenarioValue),
                    impliedLTV: parseFloat(scenarioLTV.toFixed(1)),
                    variance: Math.round(scenarioValue - this.propertyValue),
                    variancePercent: parseFloat(((scenarioValue - this.propertyValue) / this.propertyValue * 100).toFixed(1))
                });
            }
        });
        
        return scenarios;
    }

    /**
     * Get market validation summary
     */
    getMarketValidationSummary(marketData, validationResults) {
        const summary = {
            dealMetrics: this.calculate(),
            marketComparison: {
                dealCapRate: (this.annualNOI / this.propertyValue) * 100,
                marketAvgRate: marketData.avgRate,
                marketRange: `${marketData.minRate}% - ${marketData.maxRate}%`,
                variance: null,
                position: null
            },
            riskAssessment: {
                level: 'UNKNOWN',
                factors: [],
                recommendations: []
            }
        };

        // Calculate variance from market
        const dealCapRate = summary.marketComparison.dealCapRate;
        const variance = dealCapRate - marketData.avgRate;
        summary.marketComparison.variance = parseFloat(variance.toFixed(2));

        // Determine market position
        if (dealCapRate < marketData.minRate) {
            summary.marketComparison.position = 'BELOW_MARKET';
        } else if (dealCapRate > marketData.maxRate) {
            summary.marketComparison.position = 'ABOVE_MARKET';
        } else {
            summary.marketComparison.position = 'WITHIN_MARKET';
        }

        // Risk assessment
        if (validationResults && validationResults.validation) {
            switch (validationResults.validation.validation) {
                case 'OVERVALUED':
                    summary.riskAssessment.level = 'HIGH';
                    summary.riskAssessment.factors.push('Property appears overvalued vs market');
                    break;
                case 'UNDERVALUED':
                    summary.riskAssessment.level = 'LOW';
                    summary.riskAssessment.factors.push('Property appears undervalued vs market');
                    break;
                case 'WITHIN_RANGE':
                    summary.riskAssessment.level = 'MODERATE';
                    summary.riskAssessment.factors.push('Property value aligns with market');
                    break;
                default:
                    summary.riskAssessment.level = 'REVIEW';
                    summary.riskAssessment.factors.push('Market variance requires review');
            }
        }

        return summary;
    }
}

// Export for global use
window.DealModel = DealModel; 