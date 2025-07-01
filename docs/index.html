<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cap Rate Trends Dashboard</title>
    <link rel="stylesheet" href="css/dashboard.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <!-- Loading State -->
    <div id="loadingState" class="loading">
        <div class="loading-spinner"></div>
        <p>Loading Cap Rate Dashboard...</p>
    </div>

    <!-- Error State -->
    <div id="errorState" class="error">
        <div class="error-message">Failed to Load Dashboard</div>
        <div class="error-details">Please check your internet connection and try refreshing the page.</div>
    </div>

    <!-- Main Content -->
    <div id="mainContent" class="container">
        <!-- Header -->
        <header class="header">
            <h1>Cap Rate Trends Dashboard</h1>
            <p>Commercial Real Estate Market Analysis</p>
        </header>

        <!-- Error Container for Runtime Errors -->
        <div id="errorContainer"></div>

        <!-- Controls -->
        <section class="controls">
            <div class="control-group">
                <label for="sectorFilter">Sector:</label>
                <select id="sectorFilter">
                    <option value="">All Sectors</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="marketFilter">Market:</label>
                <select id="marketFilter">
                    <option value="">All Markets</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="periodFilter">Time Period:</label>
                <select id="periodFilter">
                    <option value="">All Periods</option>
                </select>
            </div>
            
            <button id="resetFilters">Reset Filters</button>
            <button id="exportData">Export Data</button>
            <button id="toggleCalculator">Show Deal Calculator</button>
            <button id="marketAnalysis">Market Analysis</button>
        </section>

        <!-- Statistics Grid -->
        <section class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="totalRecords">-</div>
                <div class="stat-label">Total Records</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalSectors">-</div>
                <div class="stat-label">Asset Classes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalMarkets">-</div>
                <div class="stat-label">Markets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="timeRange">-</div>
                <div class="stat-label">Time Range</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avgCapRate">-</div>
                <div class="stat-label">Average Cap Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="marketVolatility">-</div>
                <div class="stat-label">Market Volatility</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="highestCapRate">-</div>
                <div class="stat-label">Highest Cap Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="lowestCapRate">-</div>
                <div class="stat-label">Lowest Cap Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="riskSpread">-</div>
                <div class="stat-label">Risk Spread</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="trendDirection">-</div>
                <div class="stat-label">Market Trend</div>
            </div>
        </section>

        <!-- Deal Calculator (Positioned prominently after stats) -->
        <section id="dealCalculator" class="chart-container" style="display: none;">
            <h2 class="chart-title">Deal Calculator & Credit Analysis</h2>
            
            <!-- Calculator Mode Toggle -->
            <div class="calculator-mode-toggle">
                <label class="toggle-label">
                    <input type="radio" name="calculatorMode" value="standard" checked> Standard Calculation
                </label>
                <label class="toggle-label">
                    <input type="radio" name="calculatorMode" value="validation"> Market Validation
                </label>
            </div>

            <!-- Standard Calculator Fields -->
            <div id="standardCalculatorFields" class="credit-metrics">
                <div class="metric-card">
                    <div class="metric-title">Property Value ($)</div>
                    <input type="number" id="propertyValue" placeholder="Enter property value" min="0" step="1000">
                </div>
                <div class="metric-card">
                    <div class="metric-title">Annual NOI ($)</div>
                    <input type="number" id="annualNOI" placeholder="Enter annual NOI" min="0" step="1000">
                </div>
                <div class="metric-card">
                    <div class="metric-title">Loan Amount ($)</div>
                    <input type="number" id="loanAmount" placeholder="Enter loan amount" min="0" step="1000">
                </div>
                <div class="metric-card">
                    <div class="metric-title">Interest Rate (%)</div>
                    <input type="number" id="interestRate" placeholder="Enter interest rate" min="0" max="20" step="0.01">
                </div>
                <div class="metric-card">
                    <div class="metric-title">Amortization (Months)</div>
                    <input type="number" id="amortizationMonths" placeholder="Enter months (e.g., 360)" min="1" max="600" step="1">
                </div>
                <div class="metric-card">
                    <div class="metric-title">SOFR Rate (%)</div>
                    <input type="number" id="sofrRate" placeholder="Enter SOFR rate" min="0" max="10" step="0.01">
                </div>
            </div>

            <!-- Market Validation Fields -->
            <div id="marketValidationFields" class="credit-metrics" style="display: none;">
                <div class="metric-card">
                    <div class="metric-title">Annual NOI ($)</div>
                    <input type="number" id="validationNOI" placeholder="Enter annual NOI" min="0" step="1000">
                </div>
                <div class="metric-card">
                    <div class="metric-title">Loan Amount ($)</div>
                    <input type="number" id="validationLoanAmount" placeholder="Enter loan amount" min="0" step="1000">
                </div>
                <div class="metric-card">
                    <div class="metric-title">Asset Class</div>
                    <select id="validationSector">
                        <option value="">Select Asset Class</option>
                    </select>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Market</div>
                    <select id="validationMarket">
                        <option value="">Select Market</option>
                    </select>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Time Period</div>
                    <select id="validationPeriod">
                        <option value="">Select Period</option>
                    </select>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Property Value ($) - Optional</div>
                    <input type="number" id="validationPropertyValue" placeholder="Leave blank to derive from market" min="0" step="1000">
                    <small>Leave blank to derive from market cap rates</small>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="calculator-actions">
                <button id="calculateDeal">Calculate Deal & Credit Analysis</button>
                <button id="performMarketValidation" style="display: none;">Perform Market Validation</button>
            </div>
            
            <!-- Standard Deal Results -->
            <div id="dealResults" style="display: none;">
                <h3>Standard Calculation Results</h3>
                <div class="credit-metrics">
                    <div class="metric-card risk-indicator">
                        <div class="metric-title">Cap Rate</div>
                        <div class="metric-value" id="resultCapRate">-</div>
                    </div>
                    <div class="metric-card risk-indicator">
                        <div class="metric-title">LTV Ratio</div>
                        <div class="metric-value" id="resultLTV">-</div>
                    </div>
                    <div class="metric-card risk-indicator">
                        <div class="metric-title">DSCR</div>
                        <div class="metric-value" id="resultDSCR">-</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Annual Debt Service</div>
                        <div class="metric-value" id="resultDebtService">-</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Spread over SOFR (bps)</div>
                        <div class="metric-value" id="resultSpread">-</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Credit Decision</div>
                        <div class="metric-value" id="creditDecision">-</div>
                    </div>
                </div>
            </div>

            <!-- Market Validation Results -->
            <div id="marketValidationResults" style="display: none;">
                <h3>Market Validation Results</h3>
                <div id="marketValidationContent"></div>
            </div>
        </section>

        <!-- Charts Grid -->
        <section class="charts-grid">
            <!-- Time Series Chart -->
            <div class="chart-container">
                <h2 class="chart-title">
                    Cap Rate Trends Over Time (By Asset Class)
                    <button class="export-btn" data-export-chart="timeSeries">Export Chart</button>
                </h2>
                <canvas id="timeSeriesChart" class="chart-canvas"></canvas>
            </div>

            <!-- Sector Comparison Chart -->
            <div class="chart-container">
                <h2 class="chart-title">
                    Average Cap Rates by Sector
                    <button class="export-btn" data-export-chart="sector">Export Chart</button>
                </h2>
                <canvas id="sectorChart" class="chart-canvas"></canvas>
            </div>

            <!-- Market Ranking Chart -->
            <div class="chart-container">
                <h2 class="chart-title">
                    Top Markets by Cap Rate
                    <button class="export-btn" data-export-chart="market">Export Chart</button>
                </h2>
                <canvas id="marketChart" class="chart-canvas"></canvas>
            </div>
        </section>
    </div>

    <!-- Load modules in proper order -->
    <script src="js/services/DataService.js"></script>
    <script src="js/services/MarketValidationService.js"></script>
    <script src="js/models/DealModel.js"></script>
    <script src="js/components/ChartManager.js"></script>
    <script src="js/components/DashboardController.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
