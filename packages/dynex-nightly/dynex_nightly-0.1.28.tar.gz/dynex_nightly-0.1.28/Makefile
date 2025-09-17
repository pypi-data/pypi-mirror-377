.PHONY: help install install-dev test test-unit test-integration test-coverage lint format clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e .
	pip install pytest pytest-cov flake8 black isort matplotlib

test: ## Run all tests
	python -m pytest tests/ -v

test-unit: ## Run unit tests only
	python -m pytest tests/ -v -m "not integration"

test-integration: ## Run integration tests only
	python -m pytest tests/test_integration.py -v -m integration

test-coverage: ## Run tests with coverage report
	python -m pytest tests/ -v --cov=dynex --cov-report=term-missing --cov-report=html

test-basic: ## Run basic functionality tests
	python -c "import dynex; dynex.test()"

test-config: ## Test configuration handling
	python -c "import os; os.environ.update({'DYNEX_API_KEY': 'test', 'DYNEX_API_SECRET': 'test', 'DYNEX_API_ENDPOINT': 'https://test', 'DYNEX_FTP_HOSTNAME': 'test', 'DYNEX_FTP_USERNAME': 'test', 'DYNEX_FTP_PASSWORD': 'test'}); from dynex import DynexConfig; print('Config test passed')"

test-runner: ## Run tests using the test runner script
	python tests/test_runner.py --all --coverage --html

lint: ## Run linting
	flake8 dynex tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 dynex tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Format code
	black dynex tests
	isort dynex tests

format-check: ## Check code formatting
	black --check dynex tests
	isort --check-only dynex tests

clean: ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf tests/tmp/
	rm -rf tests/testnet/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

setup-test-env: ## Setup test environment
	mkdir -p tests/tmp tests/testnet
	chmod +x tests/testnet/dynexcore 2>/dev/null || echo "Mock solver will be created during tests"

test-all: clean setup-test-env test-coverage lint format-check ## Run all checks (clean, test, lint, format)

ci-test: setup-test-env test-coverage lint format-check ## Run CI tests

# Development helpers
dev-install: install-dev setup-test-env ## Install dev environment and setup test files

quick-test: setup-test-env test-unit ## Quick test run for development

# Documentation
docs: ## Generate documentation (if sphinx is available)
	@echo "Documentation generation not implemented yet"

# Release helpers
build: clean ## Build package
	python -m build

check-build: build ## Check built package
	twine check dist/*

# Test specific components
test-models: ## Test model classes
	python -m pytest tests/test_models.py -v

test-sampler: ## Test sampler
	python -m pytest tests/test_sampler.py -v

test-api: ## Test API
	python -m pytest tests/test_api.py -v

test-config-tests: ## Test configuration
	python -m pytest tests/test_config.py -v

test-utils: ## Test utilities
	python -m pytest tests/test_utils.py -v
