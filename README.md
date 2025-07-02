# Cap Rate Analyzer

**Author:** Dan Taylor (daniel.taylor@liveoak.bank)  
**Organization:** Live Oak Bank  
**Version:** 2.0.0  
**Last Updated:** July 2025

## Project Overview

The Cap Rate Analyzer is a sophisticated financial analysis tool designed to extract, process, and visualize capitalization rate data from semi-annual commercial real estate reports. This system automates the traditionally manual process of parsing PDF reports and transforms them into actionable insights through an interactive web dashboard.

### Business Purpose

Commercial real estate cap rates are critical indicators for investment decisions, but they're typically published in PDF format across multiple reports throughout the year. This tool:

- **Automates Data Extraction**: Converts PDF reports into structured, searchable data
- **Ensures Data Consistency**: Standardizes cap rate information across different report formats
- **Enables Quick Analysis**: Provides immediate access to historical trends and market comparisons
- **Supports Investment Decisions**: Delivers actionable insights for credit and investment teams

### Key Features

- 🔄 **Automated PDF Processing**: Intelligent parsing of semi-annual cap rate reports
- 📊 **Interactive Dashboard**: Real-time visualization of cap rate trends and market data
- 🎯 **Market Intelligence**: Comprehensive analysis across sectors, regions, and time periods
- 📈 **Historical Tracking**: Maintains complete historical record of cap rate evolution
- 🔍 **Advanced Filtering**: Drill-down capabilities by sector, market, and time period
- 💾 **Data Export**: Export capabilities for further analysis and reporting
- ⚡ **High Performance**: Optimized for processing large datasets efficiently

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+ (for dashboard development)
- 4GB+ RAM (recommended for processing large PDFs)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd cap_rate_project

# Install Python dependencies
pip install -e .

# Verify installation
python -m pytest tests/ -v
```

### Basic Usage

```bash
# Process a single PDF report
python scripts/process_pdf.py semi_annual_reports/h1_2024.pdf

# Start the dashboard server
python scripts/serve_dashboard.py

# Access dashboard at http://localhost:8080
```

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF Reports   │───▶│  Parser Engine   │───▶│  Data Storage   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │                         │
                               ▼                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Dashboard     │◀───│  Web Interface   │◀───│  API Layer      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

#### 1. **Parser Engine** (`src/cap_rate_analyzer/core/`)
- **Purpose**: Extracts structured data from PDF reports
- **Key Classes**: `CapRateParser`, `DataProcessor`
- **Features**: Intelligent text recognition, data validation, error handling

#### 2. **Data Models** (`src/cap_rate_analyzer/models/`)
- **Purpose**: Defines data structures and validation rules
- **Key Classes**: `CapRateRecord`, `ParseResult`, `ProcessingResult`
- **Features**: Pydantic-based validation, type safety, serialization

#### 3. **Utilities** (`src/cap_rate_analyzer/utils/`)
- **Purpose**: Supporting functionality for text processing and configuration
- **Key Modules**: `TextProcessor`, `Config`
- **Features**: Text normalization, market name standardization, configuration management

#### 4. **Web Dashboard** (`dashboard/`)
- **Purpose**: Interactive visualization and analysis interface
- **Technologies**: Pure JavaScript, Chart.js, responsive CSS
- **Features**: Real-time filtering, historical trends, export capabilities

### Data Flow

1. **Ingestion**: PDF reports placed in `semi_annual_reports/` directory
2. **Parsing**: `CapRateParser` extracts structured data using advanced text processing
3. **Validation**: Data validated against business rules and stored in structured format
4. **Processing**: `DataProcessor` aggregates, deduplicates, and enriches data
5. **Storage**: Results saved as CSV (human-readable) and JSON (dashboard-optimized)
6. **Visualization**: Dashboard loads data and provides interactive analysis tools

## Testing & Quality Assurance

### Comprehensive Test Coverage: 94.89%

The project maintains **enterprise-grade testing standards** with comprehensive validation:

- **📊 Test Coverage**: 94.89% (exceeds 80% industry standard)
- **✅ Test Count**: 132 tests - all passing
- **🎯 Quality Gate**: 80% minimum coverage threshold  
- **⚡ Performance**: Full test suite executes in < 2 seconds

### Test Suite Breakdown
- **Unit Tests (117)**: Core component validation
  - Parser: 21 tests (93% coverage)
  - Processor: 47 tests (97% coverage)  
  - Models: 9 tests (100% coverage)
  - Configuration: 24 tests (100% coverage)
  - Text Processing: 16 tests (90% coverage)
- **Integration Tests (15)**: End-to-end workflow validation
- **Dashboard Tests (21)**: UI component and functionality testing

### Testing Commands
```bash
# Run all tests with coverage report
pytest tests/ --cov=src/cap_rate_analyzer --cov-report=html -v

# Run specific test categories  
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only

# View detailed coverage report
open htmlcov/index.html
```

## Data Sources & Formats

### Supported PDF Formats

The system intelligently handles various semi-annual report formats:

- **CBRE Cap Rate Survey Reports** (H1/H2 annual editions)
- **Standardized Industry Reports** (following common formatting patterns)
- **Custom Report Formats** (with configurable parsing rules)

### Input Requirements

- **File Naming**: Must include year and half (e.g., `h1_2024.pdf`, `2023_h2.pdf`)
- **Content Structure**: Reports should contain tabular cap rate data
- **Data Quality**: Clear sector, market, and rate information

### Output Formats

- **CSV**: `historical_cap_rates.csv` - Human-readable, Excel-compatible
- **JSON**: `dashboard_data.json` - Optimized for dashboard consumption
- **Metadata**: `processing_metadata.json` - Processing history and statistics

## Configuration & Customization

### Environment Configuration

```bash
# Copy environment template
cp .env.template .env

# Configure key settings
MIN_CAP_RATE=0.5          # Minimum valid cap rate
MAX_CAP_RATE=15.0         # Maximum valid cap rate
MIN_MARKET_LENGTH=3       # Minimum market name length
```

### Parser Configuration

The parser can be customized for different report formats:

```python
# Custom parsing configuration
custom_config = {
    'parsing': {
        'min_cap_rate': 1.0,
        'max_cap_rate': 20.0,
        'excluded_terms': ['preliminary', 'draft']
    },
    'validation': {
        'required_markets': ['New York', 'Los Angeles', 'Chicago'],
        'valid_sectors': ['Office', 'Industrial', 'Retail']
    }
}
```

### Dashboard Customization

- **Branding**: Update colors and logos in `dashboard/css/style.css`
- **Features**: Enable/disable components in `dashboard/js/config.js`
- **Data Sources**: Configure API endpoints in `dashboard/js/services/DataService.js`

## Deployment & Production

### Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Start development server with auto-reload
python scripts/serve_dashboard.py --debug

# Run tests in watch mode
pytest tests/ --cov=src --cov-report=term -f
```

### Production Deployment

#### Option 1: Traditional Server Deployment

```bash
# Production server setup
pip install gunicorn
gunicorn --bind 0.0.0.0:8080 --workers 4 scripts.serve_dashboard:app

# Nginx configuration (recommended)
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Option 2: Docker Containerization

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8080
CMD ["python", "scripts/serve_dashboard.py"]
```

#### Option 3: Cloud Deployment

**AWS Deployment:**
- **Compute**: AWS Lambda + API Gateway for serverless processing
- **Storage**: S3 for PDF storage, RDS for structured data
- **Frontend**: CloudFront + S3 for dashboard hosting

**Azure Deployment:**
- **Compute**: Azure Functions + Azure Web Apps
- **Storage**: Blob Storage + Azure SQL Database
- **Frontend**: Azure CDN + Static Web Apps

**Google Cloud Platform:**
- **Compute**: Cloud Functions + Cloud Run
- **Storage**: Cloud Storage + Cloud SQL
- **Frontend**: Cloud CDN + Firebase Hosting

### Performance Optimization

#### Production Recommendations

1. **Caching Strategy**
   ```python
   # Implement Redis caching for processed data
   CACHE_TIMEOUT = 3600  # 1 hour
   REDIS_URL = "redis://localhost:6379"
   ```

2. **Database Integration**
   ```python
   # Replace CSV with PostgreSQL for large datasets
   DATABASE_URL = "postgresql://user:pass@localhost/caprates"
   ```

3. **Async Processing**
   ```python
   # Implement Celery for background PDF processing
   CELERY_BROKER_URL = "redis://localhost:6379"
   ```

### Monitoring & Maintenance

#### Key Metrics to Monitor

- **Processing Time**: PDF parsing duration
- **Data Quality**: Validation error rates
- **System Performance**: Memory and CPU usage
- **User Activity**: Dashboard access patterns

#### Logging Configuration

```python
# Production logging setup
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/caprate/app.log',
            'level': 'INFO'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}
```

## Security Considerations

### Data Protection

- **Input Validation**: All PDF inputs validated before processing
- **File Type Checking**: Strict file extension and content validation
- **Resource Limits**: Memory and processing time constraints
- **Error Handling**: Secure error messages without sensitive information

### Authentication & Authorization

For production deployment, consider implementing:

- **API Authentication**: JWT tokens or API keys
- **User Management**: Role-based access control
- **Audit Logging**: Complete activity tracking
- **Data Encryption**: At-rest and in-transit encryption

### Network Security

```nginx
# Security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000";
```

## API Documentation

### Core Endpoints

#### PDF Processing
```http
POST /api/process
Content-Type: multipart/form-data

# Upload PDF for processing
curl -X POST -F "file=@report.pdf" http://localhost:8080/api/process
```

#### Data Retrieval
```http
GET /api/data
# Returns complete dataset in JSON format

GET /api/data?sector=Industrial&year=2024
# Filtered data by sector and year

GET /api/markets
# Returns list of available markets

GET /api/sectors
# Returns list of available sectors
```

#### Export Functions
```http
GET /api/export/csv
# Downloads complete dataset as CSV

GET /api/export/json
# Downloads dashboard-optimized JSON
```

## Contributing & Development

### Development Workflow

1. **Fork and Clone**: Create your own fork of the repository
2. **Feature Branches**: Create feature branches for new development
3. **Testing**: Ensure all tests pass and maintain coverage above 85%
4. **Documentation**: Update documentation for any new features
5. **Pull Request**: Submit PR with clear description of changes

### Code Standards

- **Python**: Follow PEP 8 style guidelines
- **JavaScript**: Use ESLint configuration provided
- **Testing**: Maintain test coverage above 85%
- **Documentation**: Include docstrings for all public methods

### Local Development Setup

```bash
# Development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Pre-commit hooks
pip install pre-commit
pre-commit install

# Run development server
python scripts/serve_dashboard.py --debug
```

## Troubleshooting

### Common Issues

#### PDF Processing Errors
```bash
# Issue: "Could not extract year/half from filename"
# Solution: Ensure filename contains year and half (e.g., h1_2024.pdf)

# Issue: "No valid cap rates found"
# Solution: Verify PDF contains tabular data with percentage values
```

#### Dashboard Loading Issues
```bash
# Issue: "Dashboard shows no data"
# Solution: Check data files exist in dashboard/data/

# Issue: "Charts not rendering"
# Solution: Verify Chart.js library is loaded correctly
```

#### Performance Issues
```bash
# Issue: Slow PDF processing
# Solution: Increase memory allocation or process files individually

# Issue: Dashboard slow loading
# Solution: Implement data pagination or caching
```

### Debug Mode

```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
python scripts/serve_dashboard.py

# Test specific components
python -c "from src.cap_rate_analyzer.core.parser import CapRateParser; p = CapRateParser(); print(p.parse_file('test.pdf'))"
```

## Support & Contact

**Project Author:** Dan Taylor  
**Email:** daniel.taylor@liveoak.bank  
**Organization:** Live Oak Bank  

For technical support, bug reports, or feature requests, please contact the author directly or submit issues through your organization's development process.

### Version History

- **v2.0.0**: Complete system redesign with enhanced parsing and dashboard
- **v1.x**: Initial implementation and basic functionality
- **v0.x**: Prototype and proof of concept

---

**© 2024 Live Oak Bank. All rights reserved.**  
*This software is proprietary and confidential. Unauthorized reproduction or distribution is prohibited.*
