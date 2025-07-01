/**
 * ChartManager - Handles all chart rendering and interactions
 */
class ChartManager {
    constructor(dataService) {
        this.dataService = dataService;
        this.charts = {};
        this.brandColors = {
            primary: '#371CA1',
            secondary: '#1C0E52',
            accent: '#1ECD7D',
            tertiary: '#C17B42',
            light: '#E8DCC1',
            background: '#F6F4EF'
        };
        
        this.sectorColors = {
            'Industrial': '#371CA1',
            'Multifamily': '#1ECD7D',
            'Office': '#C17B42',
            'Retail': '#1C0E52',
            'Hotel': '#E8DCC1'
        };
    }

    /**
     * Initialize all charts
     */
    async initializeCharts() {
        try {
            await this.createTimeSeriesChart();
            await this.createSectorComparisonChart();
            await this.createMarketRankingChart();
        } catch (error) {
            console.error('Error initializing charts:', error);
            throw error;
        }
    }

    /**
     * Create time series chart with MULTIPLE LINES for each asset class
     */
    async createTimeSeriesChart(sector = null, market = null) {
        const ctx = document.getElementById('timeSeriesChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.charts.timeSeries) {
            this.charts.timeSeries.destroy();
        }

        // Get multi-sector time series data
        const multiSectorData = this.dataService.getMultiSectorTimeSeriesData(sector, market);
        
        if (!multiSectorData.periods || multiSectorData.periods.length === 0) {
            this.showNoDataMessage('timeSeriesChart');
            return;
        }

        // Create datasets for each sector
        const datasets = multiSectorData.sectors.map(sectorName => {
            return {
                label: sectorName,
                data: multiSectorData.data[sectorName] || [],
                borderColor: this.sectorColors[sectorName] || this.brandColors.primary,
                backgroundColor: (this.sectorColors[sectorName] || this.brandColors.primary) + '20',
                borderWidth: 3,
                fill: false,
                tension: 0.4,
                pointBackgroundColor: this.sectorColors[sectorName] || this.brandColors.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                spanGaps: true
            };
        });

        this.charts.timeSeries = new Chart(ctx, {
            type: 'line',
            data: {
                labels: multiSectorData.periods.map(p => this.formatPeriodLabel(p)),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        labels: {
                            color: this.brandColors.secondary,
                            font: { size: 12, weight: 'bold' }
                        }
                    },
                    tooltip: {
                        backgroundColor: this.brandColors.secondary,
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.brandColors.primary,
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.y;
                                return value !== null ? `${context.dataset.label}: ${value.toFixed(2)}%` : `${context.dataset.label}: No data`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Cap Rate (%)',
                            color: this.brandColors.secondary,
                            font: { size: 14, weight: 'bold' }
                        },
                        ticks: {
                            color: this.brandColors.secondary,
                            callback: (value) => `${value.toFixed(1)}%`
                        },
                        grid: {
                            color: this.brandColors.light + '40'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time Period',
                            color: this.brandColors.secondary,
                            font: { size: 14, weight: 'bold' }
                        },
                        ticks: {
                            color: this.brandColors.secondary,
                            maxRotation: 45
                        },
                        grid: {
                            color: this.brandColors.light + '40'
                        }
                    }
                }
            }
        });
    }

    /**
     * Create sector comparison chart
     */
    async createSectorComparisonChart() {
        const ctx = document.getElementById('sectorChart');
        if (!ctx) return;

        if (this.charts.sector) {
            this.charts.sector.destroy();
        }

        const sectorData = this.dataService.getSectorComparison();
        
        if (sectorData.length === 0) {
            this.showNoDataMessage('sectorChart');
            return;
        }

        const labels = sectorData.map(item => item.sector);
        const data = sectorData.map(item => item.avgRate);
        const colors = labels.map(label => this.sectorColors[label] || this.brandColors.primary);

        this.charts.sector = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average Cap Rate',
                    data: data,
                    backgroundColor: colors.map(color => color + '80'),
                    borderColor: colors,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: this.brandColors.secondary,
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        callbacks: {
                            label: (context) => `Average: ${context.parsed.y.toFixed(2)}%`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Cap Rate (%)',
                            color: this.brandColors.secondary,
                            font: { size: 14, weight: 'bold' }
                        },
                        ticks: {
                            color: this.brandColors.secondary,
                            callback: (value) => `${value.toFixed(1)}%`
                        }
                    },
                    x: {
                        ticks: {
                            color: this.brandColors.secondary,
                            font: { weight: 'bold' }
                        }
                    }
                }
            }
        });
    }

    /**
     * Create market ranking chart
     */
    async createMarketRankingChart() {
        const ctx = document.getElementById('marketChart');
        if (!ctx) return;

        if (this.charts.market) {
            this.charts.market.destroy();
        }

        const marketData = this.dataService.getMarketRanking(10);
        
        if (marketData.length === 0) {
            this.showNoDataMessage('marketChart');
            return;
        }

        const labels = marketData.map(item => this.truncateLabel(item.market, 15));
        const data = marketData.map(item => item.avgRate);

        this.charts.market = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average Cap Rate',
                    data: data,
                    backgroundColor: this.brandColors.accent + '80',
                    borderColor: this.brandColors.accent,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: this.brandColors.secondary,
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        callbacks: {
                            label: (context) => `${context.parsed.x.toFixed(2)}%`
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Cap Rate (%)',
                            color: this.brandColors.secondary,
                            font: { size: 14, weight: 'bold' }
                        },
                        ticks: {
                            color: this.brandColors.secondary,
                            callback: (value) => `${value.toFixed(1)}%`
                        }
                    },
                    y: {
                        ticks: {
                            color: this.brandColors.secondary,
                            font: { size: 11 }
                        }
                    }
                }
            }
        });
    }

    /**
     * Update charts based on filters
     */
    updateCharts(filters = {}) {
        this.createTimeSeriesChart(filters.sector, filters.market);
        // Sector and market charts don't need filtering updates
    }

    /**
     * Show no data message
     */
    showNoDataMessage(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = this.brandColors.secondary;
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('No data available for selected filters', canvas.width / 2, canvas.height / 2);
    }

    /**
     * Format period label for display
     */
    formatPeriodLabel(period) {
        const [year, half] = period.split('_');
        return `${year} ${half}`;
    }

    /**
     * Get chart label based on filters
     */
    getChartLabel(sector, market) {
        let label = 'Cap Rate Trends';
        if (sector && market) {
            label = `${sector} - ${market}`;
        } else if (sector) {
            label = `${sector} Sector`;
        } else if (market) {
            label = `${market} Market`;
        }
        return label;
    }

    /**
     * Truncate long labels
     */
    truncateLabel(label, maxLength) {
        return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
    }

    /**
     * Export chart as image
     */
    exportChart(chartName) {
        if (!this.charts[chartName]) return;
        
        const canvas = this.charts[chartName].canvas;
        const link = document.createElement('a');
        link.download = `${chartName}_chart.png`;
        link.href = canvas.toDataURL();
        link.click();
    }

    /**
     * Destroy all charts
     */
    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Export for global use
window.ChartManager = ChartManager; 