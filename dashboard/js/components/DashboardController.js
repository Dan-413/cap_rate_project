/**
 * DashboardController - Main controller that orchestrates the dashboard
 */
class DashboardController {
    constructor() {
        this.dataService = null;
        this.chartManager = null;
        this.marketValidationService = null;
        this.isInitialized = false;
        this.currentFilters = {
            sector: null,
            market: null
        };
    }

    /**
     * Initialize the dashboard
     */
    async initialize() {
        try {
            this.showLoadingState();
            
            // Initialize services
            this.dataService = new DataService();
            await this.dataService.loadCapRateData();
            
            this.chartManager = new ChartManager(this.dataService);
            this.marketValidationService = new MarketValidationService(this.dataService);
            
            // Initialize UI components
            this.initializeControls();
            this.updateStatistics();
            await this.chartManager.initializeCharts();
            
            this.hideLoadingState();
            this.isInitialized = true;
            
            console.log('Dashboard initialized successfully');
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showErrorState(error.message);
        }
    }

    /**
     * Initialize control elements and event listeners
     */
    initializeControls() {
        // Populate sector dropdown
        const sectorSelect = document.getElementById('sectorFilter');
        if (sectorSelect) {
            const sectors = this.dataService.getSectors();
            sectorSelect.innerHTML = '<option value="">All Sectors</option>';
            sectors.forEach(sector => {
                const option = document.createElement('option');
                option.value = sector;
                option.textContent = sector;
                sectorSelect.appendChild(option);
            });
            
            sectorSelect.addEventListener('change', (e) => {
                this.currentFilters.sector = e.target.value || null;
                this.updateCharts();
            });
        }

        // Populate market dropdown
        const marketSelect = document.getElementById('marketFilter');
        if (marketSelect) {
            const markets = this.dataService.getMarkets();
            marketSelect.innerHTML = '<option value="">All Markets</option>';
            markets.forEach(market => {
                const option = document.createElement('option');
                option.value = market;
                option.textContent = market;
                marketSelect.appendChild(option);
            });
            
            marketSelect.addEventListener('change', (e) => {
                this.currentFilters.market = e.target.value || null;
                this.updateCharts();
            });
        }

        // Populate period dropdown
        const periodSelect = document.getElementById('periodFilter');
        if (periodSelect) {
            const periods = this.dataService.getPeriods();
            periodSelect.innerHTML = '<option value="">All Periods</option>';
            periods.forEach(period => {
                const option = document.createElement('option');
                option.value = period;
                option.textContent = this.formatPeriodLabel(period);
                periodSelect.appendChild(option);
            });
            
            periodSelect.addEventListener('change', (e) => {
                this.currentFilters.period = e.target.value || null;
                this.updateCharts();
            });
        }

        // Reset button
        const resetButton = document.getElementById('resetFilters');
        if (resetButton) {
            resetButton.addEventListener('click', () => {
                this.resetFilters();
            });
        }

        // Export button
        const exportButton = document.getElementById('exportData');
        if (exportButton) {
            exportButton.addEventListener('click', () => {
                this.exportData();
            });
        }

        // Market Analysis button
        const marketAnalysisButton = document.getElementById('marketAnalysis');
        if (marketAnalysisButton) {
            marketAnalysisButton.addEventListener('click', () => {
                this.showMarketAnalysis();
            });
        }

        // Chart export buttons
        this.initializeExportButtons();
        
        // Calculator toggle button
        this.initializeCalculatorToggle();
    }

    /**
     * Format period label for display
     */
    formatPeriodLabel(period) {
        const [year, half] = period.split('_');
        return `${year} H${half}`;
    }

    /**
     * Initialize chart export buttons
     */
    initializeExportButtons() {
        const exportButtons = document.querySelectorAll('[data-export-chart]');
        exportButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const chartName = e.target.dataset.exportChart;
                this.chartManager.exportChart(chartName);
            });
        });
    }

    /**
     * Initialize calculator toggle button
     */
    initializeCalculatorToggle() {
        const toggleButton = document.getElementById('toggleCalculator');
        if (toggleButton) {
            toggleButton.addEventListener('click', () => {
                this.toggleCalculator();
            });
        }
        
        // Initialize deal calculator functionality
        this.initializeDealCalculator();
        
        // Initialize calculator mode toggle
        this.initializeCalculatorModeToggle();
    }

    /**
     * Initialize deal calculator functionality
     */
    initializeDealCalculator() {
        const calculateButton = document.getElementById('calculateDeal');
        if (calculateButton) {
            calculateButton.addEventListener('click', () => {
                this.calculateDeal();
            });
        }
        
        // Add input validation and real-time feedback
        const inputs = ['propertyValue', 'annualNOI', 'loanAmount', 'interestRate', 'amortizationMonths', 'sofrRate'];
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('input', () => {
                    this.validateInput(input);
                });
            }
        });
    }

    /**
     * Validate individual input
     */
    validateInput(input) {
        const value = parseFloat(input.value);
        const inputId = input.id;
        
        // Remove previous validation classes
        input.classList.remove('valid', 'invalid');
        
        // Validation rules
        let isValid = false;
        switch (inputId) {
            case 'propertyValue':
            case 'annualNOI':
            case 'loanAmount':
                isValid = value > 0 && value <= 100000000; // Up to $100M
                break;
            case 'interestRate':
                isValid = value >= 0 && value <= 20;
                break;
            case 'amortizationMonths':
                isValid = value >= 12 && value <= 600; // 1-50 years in months
                break;
            case 'sofrRate':
                isValid = value >= 0 && value <= 10;
                break;
        }
        
        if (input.value && !isNaN(value)) {
            input.classList.add(isValid ? 'valid' : 'invalid');
        }
    }

    /**
     * Calculate deal metrics
     */
    calculateDeal() {
        const inputs = {
            propertyValue: parseFloat(document.getElementById('propertyValue').value),
            annualNOI: parseFloat(document.getElementById('annualNOI').value),
            loanAmount: parseFloat(document.getElementById('loanAmount').value),
            interestRate: parseFloat(document.getElementById('interestRate').value),
            amortizationMonths: parseFloat(document.getElementById('amortizationMonths').value),
            sofrRate: parseFloat(document.getElementById('sofrRate').value)
        };
        
        // Validate all inputs
        const missingInputs = [];
        Object.keys(inputs).forEach(key => {
            if (isNaN(inputs[key]) || inputs[key] <= 0) {
                missingInputs.push(key);
            }
        });
        
        if (missingInputs.length > 0) {
            alert(`Please enter valid values for: ${missingInputs.join(', ')}`);
            return;
        }
        
        // Create deal model and calculate (convert months to years for calculation)
        const deal = new DealModel(
            inputs.propertyValue,
            inputs.annualNOI,
            inputs.loanAmount,
            inputs.interestRate,
            inputs.amortizationMonths / 12, // Convert to years for internal calculation
            inputs.sofrRate
        );
        
        const calculations = deal.calculate();
        const creditDecision = deal.getCreditDecision();
        
        // Update results display
        this.displayDealResults(calculations, creditDecision, deal);
        
        // Show results section
        const resultsSection = document.getElementById('dealResults');
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
        
        // Add market context
        this.addMarketContext(calculations.actualCapRate);
    }

    /**
     * Display deal calculation results
     */
    displayDealResults(calculations, creditDecision, deal) {
        // Update result values
        document.getElementById('resultCapRate').textContent = `${calculations.actualCapRate.toFixed(2)}%`;
        document.getElementById('resultLTV').textContent = `${calculations.actualLTV.toFixed(1)}%`;
        document.getElementById('resultDSCR').textContent = calculations.dscr.toFixed(2);
        document.getElementById('resultDebtService').textContent = `$${calculations.annualDebtService.toLocaleString()}`;
        document.getElementById('resultSpread').textContent = `${calculations.spread.toFixed(0)} bps`;
        
        // Update credit decision with styling
        const creditElement = document.getElementById('creditDecision');
        if (creditElement) {
            creditElement.textContent = creditDecision.decision;
            creditElement.style.color = creditDecision.color;
        }
        
        // Add risk indicators
        this.updateRiskIndicators(calculations, deal);
    }

    /**
     * Update risk indicators with color coding
     */
    updateRiskIndicators(calculations, deal) {
        // DSCR risk indicator
        const dscrRisk = deal.getDSCRRisk(calculations.dscr);
        const dscrElement = document.getElementById('resultDSCR');
        if (dscrElement && dscrElement.parentElement) {
            dscrElement.parentElement.style.borderLeftColor = dscrRisk.color;
        }
        
        // LTV risk indicator
        const ltvRisk = deal.getLTVRisk(calculations.actualLTV);
        const ltvElement = document.getElementById('resultLTV');
        if (ltvElement && ltvElement.parentElement) {
            ltvElement.parentElement.style.borderLeftColor = ltvRisk.color;
        }
    }

    /**
     * Add market context to deal analysis
     */
    addMarketContext(dealCapRate) {
        // Get market data for comparison
        const marketData = this.dataService.getMarketRanking(50);
        const sectorData = this.dataService.getSectorComparison();
        
        // Find comparable rates
        const marketAvg = marketData.reduce((sum, m) => sum + m.avgRate, 0) / marketData.length;
        const sectorAvg = sectorData.reduce((sum, s) => sum + s.avgRate, 0) / sectorData.length;
        
        // Add context message
        let contextMessage = '';
        if (dealCapRate > marketAvg + 0.5) {
            contextMessage = `✅ Deal cap rate is ${(dealCapRate - marketAvg).toFixed(1)}% above market average`;
        } else if (dealCapRate < marketAvg - 0.5) {
            contextMessage = `⚠️ Deal cap rate is ${(marketAvg - dealCapRate).toFixed(1)}% below market average`;
        } else {
            contextMessage = `ℹ️ Deal cap rate is in line with market average (${marketAvg.toFixed(2)}%)`;
        }
        
        // Display context
        let contextElement = document.getElementById('marketContext');
        if (!contextElement) {
            contextElement = document.createElement('div');
            contextElement.id = 'marketContext';
            contextElement.className = 'market-context';
            document.getElementById('dealResults').appendChild(contextElement);
        }
        contextElement.textContent = contextMessage;
    }

    /**
     * Toggle deal calculator visibility
     */
    toggleCalculator() {
        const calculator = document.getElementById('dealCalculator');
        const button = document.getElementById('toggleCalculator');
        
        if (calculator && button) {
            if (calculator.style.display === 'none') {
                calculator.style.display = 'block';
                button.textContent = 'Hide Deal Calculator';
            } else {
                calculator.style.display = 'none';
                button.textContent = 'Show Deal Calculator';
            }
        }
    }

    /**
     * Update statistics display
     */
    updateStatistics() {
        if (!this.dataService.processedData) return;

        const data = this.dataService.processedData;
        const validData = data.filter(row => 
            this.dataService.isValidCapRate(row.H1_Low) || 
            this.dataService.isValidCapRate(row.H1_High) || 
            this.dataService.isValidCapRate(row.H2_Low) || 
            this.dataService.isValidCapRate(row.H2_High)
        );

        // Calculate statistics
        const totalRecords = validData.length;
        const sectors = this.dataService.getSectors().length;
        const markets = this.dataService.getMarkets().length;
        const periods = this.dataService.getPeriods();

        // Calculate time range (years covered)
        const years = [...new Set(periods.map(p => p.split('_')[0]))].sort();
        const timeRange = years.length > 1 ? `${years[0]}-${years[years.length - 1]}` : years[0] || 'N/A';

        // Calculate average cap rate and volatility
        const allRates = [];
        validData.forEach(row => {
            if (row.h1_avg) allRates.push(row.h1_avg);
            if (row.h2_avg) allRates.push(row.h2_avg);
        });
        
        const avgCapRate = allRates.length > 0 
            ? allRates.reduce((sum, rate) => sum + rate, 0) / allRates.length 
            : 0;

        // Calculate market volatility (standard deviation)
        const marketVolatility = this.calculateVolatility(allRates);

        // Calculate additional credit metrics
        const highestCapRate = allRates.length > 0 ? Math.max(...allRates) : 0;
        const lowestCapRate = allRates.length > 0 ? Math.min(...allRates) : 0;
        const riskSpread = highestCapRate - lowestCapRate;

        // Calculate market trend (compare recent vs older periods)
        const trendDirection = this.calculateMarketTrend(periods, validData);

        // Update DOM elements
        this.updateStatElement('totalRecords', totalRecords.toLocaleString());
        this.updateStatElement('totalSectors', sectors);
        this.updateStatElement('totalMarkets', markets);
        this.updateStatElement('timeRange', timeRange);
        this.updateStatElement('avgCapRate', `${avgCapRate.toFixed(2)}%`);
        this.updateStatElement('marketVolatility', `${marketVolatility.toFixed(2)}%`);
        this.updateStatElement('highestCapRate', `${highestCapRate.toFixed(2)}%`);
        this.updateStatElement('lowestCapRate', `${lowestCapRate.toFixed(2)}%`);
        this.updateStatElement('riskSpread', `${riskSpread.toFixed(2)}%`);
        this.updateStatElement('trendDirection', trendDirection);
    }

    /**
     * Calculate market trend direction
     */
    calculateMarketTrend(periods, validData) {
        if (periods.length < 2) return 'Insufficient Data';

        // Sort periods chronologically
        const sortedPeriods = periods.sort((a, b) => {
            const [yearA, halfA] = a.split('_').map(Number);
            const [yearB, halfB] = b.split('_').map(Number);
            if (yearA !== yearB) return yearA - yearB;
            return halfA - halfB;
        });

        // Get recent vs older period averages
        const recentPeriods = sortedPeriods.slice(-2); // Last 2 periods
        const olderPeriods = sortedPeriods.slice(0, 2); // First 2 periods

        const recentRates = [];
        const olderRates = [];

        validData.forEach(row => {
            if (recentPeriods.includes(row.period_key)) {
                if (row.h1_avg) recentRates.push(row.h1_avg);
                if (row.h2_avg) recentRates.push(row.h2_avg);
            }
            if (olderPeriods.includes(row.period_key)) {
                if (row.h1_avg) olderRates.push(row.h1_avg);
                if (row.h2_avg) olderRates.push(row.h2_avg);
            }
        });

        if (recentRates.length === 0 || olderRates.length === 0) return 'No Trend Data';

        const recentAvg = recentRates.reduce((sum, rate) => sum + rate, 0) / recentRates.length;
        const olderAvg = olderRates.reduce((sum, rate) => sum + rate, 0) / olderRates.length;
        const change = recentAvg - olderAvg;

        if (Math.abs(change) < 0.1) return '→ Stable';
        return change > 0 ? '↗ Rising' : '↘ Falling';
    }

    /**
     * Calculate volatility (standard deviation)
     */
    calculateVolatility(rates) {
        if (rates.length < 2) return 0;
        
        const mean = rates.reduce((sum, rate) => sum + rate, 0) / rates.length;
        const squaredDiffs = rates.map(rate => Math.pow(rate - mean, 2));
        const variance = squaredDiffs.reduce((sum, diff) => sum + diff, 0) / rates.length;
        
        return Math.sqrt(variance);
    }

    /**
     * Update a statistics element
     */
    updateStatElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Update charts based on current filters
     */
    updateCharts() {
        if (!this.isInitialized) return;
        
        this.chartManager.updateCharts(this.currentFilters);
        this.updateFilteredStatistics();
    }

    /**
     * Update statistics based on current filters
     */
    updateFilteredStatistics() {
        const filteredData = this.dataService.filterData({
            ...this.currentFilters,
            validMarketOnly: true
        });

        const filteredCount = filteredData.length;
        this.updateStatElement('filteredRecords', 
            filteredCount > 0 ? `${filteredCount.toLocaleString()} filtered` : 'All data'
        );
    }

    /**
     * Reset all filters
     */
    resetFilters() {
        this.currentFilters = {
            sector: null,
            market: null,
            period: null
        };

        // Reset dropdowns
        const sectorSelect = document.getElementById('sectorFilter');
        const marketSelect = document.getElementById('marketFilter');
        const periodSelect = document.getElementById('periodFilter');
        
        if (sectorSelect) sectorSelect.value = '';
        if (marketSelect) marketSelect.value = '';
        if (periodSelect) periodSelect.value = '';

        // Hide market analysis if visible
        const analysisSection = document.getElementById('marketAnalysisSection');
        if (analysisSection) {
            analysisSection.remove();
        }

        // Update charts
        this.updateCharts();
    }

    /**
     * Export data as CSV
     */
    exportData() {
        if (!this.dataService.processedData) return;

        const filteredData = this.dataService.filterData({
            ...this.currentFilters,
            validMarketOnly: true
        });

        if (filteredData.length === 0) {
            alert('No data to export with current filters');
            return;
        }

        const csv = this.convertToCSV(filteredData);
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `cap_rate_data_${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
        
        window.URL.revokeObjectURL(url);
    }

    /**
     * Convert data to CSV format
     */
    convertToCSV(data) {
        if (data.length === 0) return '';

        const headers = Object.keys(data[0]);
        const csvRows = [headers.join(',')];

        data.forEach(row => {
            const values = headers.map(header => {
                const value = row[header];
                return typeof value === 'string' && value.includes(',') 
                    ? `"${value}"` 
                    : value;
            });
            csvRows.push(values.join(','));
        });

        return csvRows.join('\n');
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const loadingElement = document.getElementById('loadingState');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }

        const mainContent = document.getElementById('mainContent');
        if (mainContent) {
            mainContent.style.display = 'none';
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        const loadingElement = document.getElementById('loadingState');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }

        const mainContent = document.getElementById('mainContent');
        if (mainContent) {
            mainContent.style.display = 'block';
        }
    }

    /**
     * Show error state
     */
    showErrorState(message) {
        this.hideLoadingState();
        
        const errorElement = document.getElementById('errorState');
        if (errorElement) {
            errorElement.style.display = 'block';
            const errorMessage = errorElement.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.textContent = message;
            }
        }
    }

    /**
     * Get current dashboard state
     */
    getState() {
        return {
            filters: { ...this.currentFilters },
            isInitialized: this.isInitialized,
            dataLoaded: !!this.dataService?.processedData,
            recordCount: this.dataService?.processedData?.length || 0
        };
    }

    /**
     * Cleanup resources
     */
    destroy() {
        if (this.chartManager) {
            this.chartManager.destroyCharts();
        }
        this.dataService = null;
        this.chartManager = null;
        this.marketValidationService = null;
        this.isInitialized = false;
    }

    /**
     * Show detailed market analysis
     */
    showMarketAnalysis() {
        const market = this.currentFilters.market;
        if (!market) {
            alert('Please select a specific market to analyze.');
            return;
        }
        
        const analysis = this.dataService.getMarketAnalysis(market);
        if (!analysis) {
            alert('No data available for the selected market.');
            return;
        }
        
        this.displayMarketAnalysis(analysis);
    }

    /**
     * Display market analysis in a modal or dedicated section
     */
    displayMarketAnalysis(analysis) {
        // Create or update market analysis display
        let analysisSection = document.getElementById('marketAnalysisSection');
        if (!analysisSection) {
            analysisSection = document.createElement('section');
            analysisSection.id = 'marketAnalysisSection';
            analysisSection.className = 'chart-container';
            document.querySelector('.charts-grid').appendChild(analysisSection);
        }
        
        const html = `
            <h2 class="chart-title">Market Analysis: ${analysis.market}</h2>
            <div class="credit-metrics">
                <div class="metric-card">
                    <div class="metric-title">Total Records</div>
                    <div class="metric-value">${analysis.totalRecords}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Overall Average</div>
                    <div class="metric-value">${analysis.summary.overallAvg}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Volatility</div>
                    <div class="metric-value">${analysis.summary.volatility}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Range</div>
                    <div class="metric-value">${analysis.summary.overallMin}% - ${analysis.summary.overallMax}%</div>
                </div>
            </div>
            <div class="sector-breakdown">
                <h3>Sector Breakdown</h3>
                <div class="credit-metrics">
                    ${Object.entries(analysis.sectors).map(([sector, data]) => `
                        <div class="metric-card">
                            <div class="metric-title">${sector}</div>
                            <div class="metric-value">${data.avgRate}%</div>
                            <div class="metric-status">Range: ${data.minRate}% - ${data.maxRate}%</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        analysisSection.innerHTML = html;
        analysisSection.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Initialize calculator mode toggle functionality
     */
    initializeCalculatorModeToggle() {
        const modeRadios = document.querySelectorAll('input[name="calculatorMode"]');
        modeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.switchCalculatorMode(e.target.value);
            });
        });

        // Initialize validation dropdowns
        this.initializeValidationDropdowns();

        // Initialize market validation button
        const validationButton = document.getElementById('performMarketValidation');
        if (validationButton) {
            validationButton.addEventListener('click', () => {
                this.performMarketValidation();
            });
        }
    }

    /**
     * Switch between calculator modes
     */
    switchCalculatorMode(mode) {
        const standardFields = document.getElementById('standardCalculatorFields');
        const validationFields = document.getElementById('marketValidationFields');
        const calculateButton = document.getElementById('calculateDeal');
        const validationButton = document.getElementById('performMarketValidation');
        const dealResults = document.getElementById('dealResults');
        const validationResults = document.getElementById('marketValidationResults');

        if (mode === 'standard') {
            standardFields.style.display = 'grid';
            validationFields.style.display = 'none';
            calculateButton.style.display = 'block';
            validationButton.style.display = 'none';
            dealResults.style.display = 'none';
            validationResults.style.display = 'none';
        } else {
            standardFields.style.display = 'none';
            validationFields.style.display = 'grid';
            calculateButton.style.display = 'none';
            validationButton.style.display = 'block';
            dealResults.style.display = 'none';
            validationResults.style.display = 'none';
        }
    }

    /**
     * Initialize validation dropdown options
     */
    initializeValidationDropdowns() {
        // Populate validation sector dropdown
        const validationSectorSelect = document.getElementById('validationSector');
        if (validationSectorSelect) {
            const sectors = this.dataService.getSectors();
            validationSectorSelect.innerHTML = '<option value="">Select Asset Class</option>';
            sectors.forEach(sector => {
                const option = document.createElement('option');
                option.value = sector;
                option.textContent = sector;
                validationSectorSelect.appendChild(option);
            });
        }

        // Populate validation market dropdown
        const validationMarketSelect = document.getElementById('validationMarket');
        if (validationMarketSelect) {
            const markets = this.dataService.getMarkets();
            validationMarketSelect.innerHTML = '<option value="">Select Market</option>';
            markets.forEach(market => {
                const option = document.createElement('option');
                option.value = market;
                option.textContent = market;
                validationMarketSelect.appendChild(option);
            });
        }

        // Populate validation period dropdown
        const validationPeriodSelect = document.getElementById('validationPeriod');
        if (validationPeriodSelect) {
            const periods = this.dataService.getPeriods();
            validationPeriodSelect.innerHTML = '<option value="">Select Period</option>';
            periods.forEach(period => {
                const option = document.createElement('option');
                option.value = period;
                option.textContent = this.formatPeriodLabel(period);
                validationPeriodSelect.appendChild(option);
            });
        }
    }

    /**
     * Perform market validation analysis
     */
    performMarketValidation() {
        const inputs = {
            annualNOI: parseFloat(document.getElementById('validationNOI').value),
            loanAmount: parseFloat(document.getElementById('validationLoanAmount').value),
            sector: document.getElementById('validationSector').value,
            market: document.getElementById('validationMarket').value,
            period: document.getElementById('validationPeriod').value,
            propertyValue: document.getElementById('validationPropertyValue').value ? 
                parseFloat(document.getElementById('validationPropertyValue').value) : null
        };

        // Validate required inputs
        const requiredFields = ['annualNOI', 'loanAmount', 'sector', 'market', 'period'];
        const missingFields = requiredFields.filter(field => {
            return field === 'sector' || field === 'market' || field === 'period' ? 
                !inputs[field] : (!inputs[field] || inputs[field] <= 0);
        });

        if (missingFields.length > 0) {
            alert(`Please provide: ${missingFields.join(', ')}`);
            return;
        }

        // Perform market validation
        const validationResults = this.marketValidationService.performMarketValidation(inputs);
        
        if (validationResults.error) {
            alert(validationResults.error);
            return;
        }

        // Display results
        this.displayMarketValidationResults(validationResults, inputs);
    }

    /**
     * Display market validation results
     */
    displayMarketValidationResults(results, inputs) {
        const resultsContainer = document.getElementById('marketValidationContent');
        const resultsSection = document.getElementById('marketValidationResults');

        let html = '';

        // Market Data Section
        if (results.marketData) {
            html += `
                <div class="validation-section">
                    <h4>Market Data: ${results.marketData.sector} in ${results.marketData.market} (${this.formatPeriodLabel(results.marketData.period)})</h4>
                    <div class="market-data-grid">
                        <div class="market-data-item">
                            <div class="market-data-label">Average Cap Rate</div>
                            <div class="market-data-value">${results.marketData.avgRate}%</div>
                        </div>
                        <div class="market-data-item">
                            <div class="market-data-label">Range</div>
                            <div class="market-data-value">${results.marketData.minRate}% - ${results.marketData.maxRate}%</div>
                        </div>
                        <div class="market-data-item">
                            <div class="market-data-label">Data Points</div>
                            <div class="market-data-value">${results.marketData.dataPoints}</div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Derived Property Value Section
        if (results.derivedValue) {
            html += `
                <div class="derived-value-display">
                    <h4>Market-Derived Property Value</h4>
                    <div class="value">$${results.derivedValue.derivedValue.toLocaleString()}</div>
                    <div class="calculation">${results.derivedValue.calculation}</div>
                </div>
            `;
        }

        // Property Validation Section
        if (results.validation) {
            const statusClass = results.validation.validation.toLowerCase().replace('_', '-');
            html += `
                <div class="validation-section">
                    <h4>Property Value Validation</h4>
                    <div class="validation-status ${statusClass}">
                        ${results.validation.message}
                    </div>
                    <div class="market-data-grid">
                        <div class="market-data-item">
                            <div class="market-data-label">Deal Cap Rate</div>
                            <div class="market-data-value">${results.validation.dealCapRate}%</div>
                        </div>
                        <div class="market-data-item">
                            <div class="market-data-label">Market Average</div>
                            <div class="market-data-value">${results.validation.marketData.avgRate}%</div>
                        </div>
                        <div class="market-data-item">
                            <div class="market-data-label">Variance</div>
                            <div class="market-data-value">${results.validation.variance > 0 ? '+' : ''}${results.validation.variance}%</div>
                        </div>
                    </div>
                </div>
            `;
        }

        // LTV Analysis Section
        if (results.impliedLTV) {
            const propertyValue = inputs.propertyValue || results.derivedValue?.derivedValue;
            html += `
                <div class="validation-section">
                    <h4>LTV Analysis</h4>
                    <div class="market-data-grid">
                        <div class="market-data-item">
                            <div class="market-data-label">Implied LTV</div>
                            <div class="market-data-value">${results.impliedLTV.impliedLTV}%</div>
                        </div>
                        <div class="market-data-item">
                            <div class="market-data-label">Risk Level</div>
                            <div class="market-data-value">${results.impliedLTV.riskLevel.replace('_', ' ')}</div>
                        </div>
                        <div class="market-data-item">
                            <div class="market-data-label">Property Value</div>
                            <div class="market-data-value">$${propertyValue.toLocaleString()}</div>
                        </div>
                    </div>
                    <p style="margin-top: 15px; color: var(--tertiary-color);">${results.impliedLTV.message}</p>
                </div>
            `;
        }

        // Recommendations Section
        if (results.recommendations && results.recommendations.length > 0) {
            html += `
                <div class="validation-section">
                    <h4>Recommendations</h4>
                    <ul class="recommendations-list">
                        ${results.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        resultsContainer.innerHTML = html;
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Export for global use
window.DashboardController = DashboardController; 