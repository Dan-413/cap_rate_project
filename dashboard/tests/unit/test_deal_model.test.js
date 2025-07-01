/**
 * Unit Tests for DealModel
 * Run with: npm test or node --test test_deal_model.test.js
 */

import { describe, it, assert } from 'node:test';
import DealModel from '../../js/models/DealModel.js';

describe('DealModel', () => {
    describe('constructor', () => {
        it('should initialize with correct properties', () => {
            const deal = new DealModel(1000000, 80000, 750000, 5.5, 25, 4.2);
            
            assert.strictEqual(deal.propertyValue, 1000000);
            assert.strictEqual(deal.annualNOI, 80000);
            assert.strictEqual(deal.loanAmount, 750000);
            assert.strictEqual(deal.interestRate, 5.5);
            assert.strictEqual(deal.amortizationYears, 25);
            assert.strictEqual(deal.treasuryRate, 4.2);
        });
    });

    describe('calculate()', () => {
        it('should calculate basic metrics correctly', () => {
            const deal = new DealModel(1000000, 80000, 750000, 5.5, 25, 4.2);
            const results = deal.calculate();
            
            // Cap Rate = NOI / Property Value * 100
            assert.strictEqual(results.actualCapRate, 8.0);
            
            // LTV = Loan Amount / Property Value * 100
            assert.strictEqual(results.actualLTV, 75.0);
            
            // DSCR should be positive
            assert.ok(results.dscr > 0);
            
            // Annual debt service should be positive
            assert.ok(results.annualDebtService > 0);
        });

        it('should handle zero interest rate', () => {
            const deal = new DealModel(1000000, 80000, 750000, 0, 25, 4.2);
            const results = deal.calculate();
            
            // With 0% interest, monthly payment = loan / total payments
            const expectedMonthlyPayment = 750000 / (25 * 12);
            assert.strictEqual(results.monthlyPayment, expectedMonthlyPayment);
        });

        it('should cache calculations', () => {
            const deal = new DealModel(1000000, 80000, 750000, 5.5, 25, 4.2);
            
            const results1 = deal.calculate();
            const results2 = deal.calculate();
            
            // Should return the same object (cached)
            assert.strictEqual(results1, results2);
        });
    });

    describe('getCreditDecision()', () => {
        it('should approve strong deals', () => {
            // Strong deal: High DSCR, Low LTV, Good Cap Rate
            const deal = new DealModel(1000000, 100000, 600000, 5.0, 25, 4.0);
            const decision = deal.getCreditDecision();
            
            assert.strictEqual(decision.decision, '✅ APPROVE');
            assert.strictEqual(decision.risk, 'LOW');
        });

        it('should decline weak deals', () => {
            // Weak deal: Low DSCR, High LTV, Low Cap Rate
            const deal = new DealModel(1000000, 40000, 900000, 7.0, 25, 4.0);
            const decision = deal.getCreditDecision();
            
            assert.strictEqual(decision.decision, '❌ DECLINE');
            assert.strictEqual(decision.risk, 'VERY_HIGH');
        });

        it('should provide conditional approval for marginal deals', () => {
            // Marginal deal: Moderate metrics
            const deal = new DealModel(1000000, 70000, 800000, 5.5, 25, 4.0);
            const decision = deal.getCreditDecision();
            
            assert.ok(['⚠️ CONDITIONAL', '🔍 REVIEW'].includes(decision.decision));
        });
    });

    describe('getDSCRRisk()', () => {
        it('should categorize DSCR risk levels correctly', () => {
            const deal = new DealModel(1000000, 80000, 750000, 5.5, 25, 4.2);
            
            assert.strictEqual(deal.getDSCRRisk(1.5).level, 'STRONG');
            assert.strictEqual(deal.getDSCRRisk(1.3).level, 'ACCEPTABLE');
            assert.strictEqual(deal.getDSCRRisk(1.2).level, 'MARGINAL');
            assert.strictEqual(deal.getDSCRRisk(1.0).level, 'WEAK');
        });
    });

    describe('getLTVRisk()', () => {
        it('should categorize LTV risk levels correctly', () => {
            const deal = new DealModel(1000000, 80000, 750000, 5.5, 25, 4.2);
            
            assert.strictEqual(deal.getLTVRisk(65).level, 'CONSERVATIVE');
            assert.strictEqual(deal.getLTVRisk(75).level, 'STANDARD');
            assert.strictEqual(deal.getLTVRisk(80).level, 'AGGRESSIVE');
            assert.strictEqual(deal.getLTVRisk(90).level, 'HIGH_RISK');
        });
    });

    describe('toJSON()', () => {
        it('should export complete deal data', () => {
            const deal = new DealModel(1000000, 80000, 750000, 5.5, 25, 4.2);
            const json = deal.toJSON();
            
            assert.ok(json.inputs);
            assert.ok(json.calculations);
            assert.ok(json.creditDecision);
            
            assert.strictEqual(json.inputs.propertyValue, 1000000);
            assert.strictEqual(json.calculations.actualCapRate, 8.0);
        });
    });

    describe('edge cases', () => {
        it('should handle very small values', () => {
            const deal = new DealModel(100, 10, 50, 5.5, 25, 4.2);
            const results = deal.calculate();
            
            assert.ok(results.actualCapRate > 0);
            assert.ok(results.dscr > 0);
        });

        it('should handle very large values', () => {
            const deal = new DealModel(100000000, 8000000, 75000000, 5.5, 25, 4.2);
            const results = deal.calculate();
            
            assert.strictEqual(results.actualCapRate, 8.0);
            assert.strictEqual(results.actualLTV, 75.0);
        });
    });
});

// Export for Node.js test runner
export { describe, it, assert }; 