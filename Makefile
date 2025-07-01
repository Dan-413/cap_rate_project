.PHONY: help install test lint format clean dashboard update

# Default target
help:
	@echo "Cap Rate Analyzer - Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install package and dependencies"
	@echo "  install-dev Install with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test        Run all tests"
	@echo "  test-unit   Run unit tests only"
	@echo "  test-cov    Run tests with coverage report"
	@echo "  lint        Run linting (flake8, mypy)"
	@echo "  format      Format code (black, isort)"
	@echo "  clean       Clean up temporary files"
	@echo ""
	@echo "Operations:"
	@echo "  dashboard   Start dashboard server"
	@echo "  update      Update dashboard with all PDFs"
	@echo "  serve       Start development server"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest

test-unit:
	pytest tests/unit/

test-cov:
	pytest --cov=src/cap_rate_analyzer --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .mypy_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -f processing.log

# Operations
dashboard:
	python start_dashboard.py

update:
	python scripts/update_dashboard.py

serve:
	python scripts/serve_dashboard.py 