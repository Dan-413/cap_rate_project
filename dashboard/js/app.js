/**
 * Main Application Entry Point
 */

// Modules are loaded via script tags and available globally

/**
 * Application class that manages the entire dashboard
 */
class CapRateDashboardApp {
    constructor() {
        this.dashboardController = null;
        this.isInitialized = false;
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('Initializing Cap Rate Dashboard...');
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }

            // Initialize dashboard controller
            this.dashboardController = new DashboardController();
            await this.dashboardController.initialize();

            // Set up global error handling
            this.setupErrorHandling();

            // Set up additional features
            this.setupKeyboardShortcuts();
            this.setupDealCalculator();

            this.isInitialized = true;
            console.log('Cap Rate Dashboard initialized successfully');

        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showCriticalError(error);
        }
    }

    /**
     * Set up global error handling
     */
    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showError('An unexpected error occurred. Please refresh the page.');
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showError('A network or data error occurred. Please check your connection.');
        });
    }

    /**
     * Set up keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            // Ctrl/Cmd + R: Reset filters
            if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
                event.preventDefault();
                if (this.dashboardController) {
                    this.dashboardController.resetFilters();
                }
            }

            // Ctrl/Cmd + E: Export data
            if ((event.ctrlKey || event.metaKey) && event.key === 'e') {
                event.preventDefault();
                if (this.dashboardController) {
                    this.dashboardController.exportData();
                }
            }

            // Escape: Clear current selection/focus
            if (event.key === 'Escape') {
                document.activeElement.blur();
            }
        });
    }

    /**
     * Set up deal calculator (if elements exist)
     */
    setupDealCalculator() {
        const calculatorSection = document.getElementById('dealCalculator');
        if (!calculatorSection) return;

        const calculateButton = document.getElementById('calculateDeal');
        if (calculateButton) {
            calculateButton.addEventListener('click', () => {
                this.calculateDeal();
            });
        }

        // Auto-calculate on input change
        const inputs = calculatorSection.querySelectorAll('input[type="number"]');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                this.debouncedCalculate();
            });
        });
    }

    /**
     * Calculate deal metrics
     */
    calculateDeal() {
        try {
            // Get input values
            const propertyValue = parseFloat(document.getElementById('propertyValue')?.value) || 0;
            const annualNOI = parseFloat(document.getElementById('annualNOI')?.value) || 0;
            const loanAmount = parseFloat(document.getElementById('loanAmount')?.value) || 0;
            const interestRate = parseFloat(document.getElementById('interestRate')?.value) || 0;
            const amortizationYears = parseFloat(document.getElementById('amortizationYears')?.value) || 0;
            const treasuryRate = parseFloat(document.getElementById('treasuryRate')?.value) || 0;

            // Validate inputs
            if (propertyValue <= 0 || annualNOI <= 0) {
                this.showError('Please enter valid property value and NOI amounts');
                return;
            }

            // Create deal model and calculate
            const deal = new DealModel(
                propertyValue,
                annualNOI,
                loanAmount,
                interestRate,
                amortizationYears,
                treasuryRate
            );

            const results = deal.calculate();
            const creditDecision = deal.getCreditDecision();

            // Update results display
            this.displayDealResults(results, creditDecision);

        } catch (error) {
            console.error('Error calculating deal:', error);
            this.showError('Error calculating deal metrics');
        }
    }

    /**
     * Display deal calculation results
     */
    displayDealResults(results, creditDecision) {
        // Update result elements
        this.updateElement('resultCapRate', `${results.actualCapRate.toFixed(2)}%`);
        this.updateElement('resultLTV', `${results.actualLTV.toFixed(1)}%`);
        this.updateElement('resultDSCR', results.dscr.toFixed(2));
        this.updateElement('resultDebtService', `$${results.annualDebtService.toLocaleString()}`);
        this.updateElement('resultSpread', `${results.spread.toFixed(0)} bps`);

        // Update credit decision
        const decisionElement = document.getElementById('creditDecision');
        if (decisionElement) {
            decisionElement.textContent = creditDecision.decision;
            decisionElement.style.color = creditDecision.color;
        }

        // Show results section
        const resultsSection = document.getElementById('dealResults');
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
    }

    /**
     * Debounced calculate function
     */
    debouncedCalculate = this.debounce(() => {
        this.calculateDeal();
    }, 500);

    /**
     * Debounce utility function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Update DOM element safely
     */
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const errorContainer = document.getElementById('errorContainer');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="error">
                    <div class="error-message">${message}</div>
                </div>
            `;
            setTimeout(() => {
                errorContainer.innerHTML = '';
            }, 5000);
        } else {
            alert(message);
        }
    }

    /**
     * Show critical error that prevents app from working
     */
    showCriticalError(error) {
        document.body.innerHTML = `
            <div class="container">
                <div class="error" style="margin-top: 50px;">
                    <div class="error-message">Critical Error</div>
                    <p>The dashboard failed to initialize. Please refresh the page or contact support.</p>
                    <details style="margin-top: 10px;">
                        <summary>Technical Details</summary>
                        <pre style="white-space: pre-wrap; font-size: 12px; margin-top: 10px;">${error.stack || error.message}</pre>
                    </details>
                </div>
            </div>
        `;
    }

    /**
     * Get application state for debugging
     */
    getState() {
        return {
            isInitialized: this.isInitialized,
            dashboardState: this.dashboardController?.getState() || null,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Cleanup and destroy the application
     */
    destroy() {
        if (this.dashboardController) {
            this.dashboardController.destroy();
        }
        this.dashboardController = null;
        this.isInitialized = false;
    }
}

// Create global app instance
const app = new CapRateDashboardApp();

// Initialize app when script loads
app.init().catch(error => {
    console.error('Failed to start application:', error);
});

// Export for debugging/testing
window.CapRateDashboard = app; 