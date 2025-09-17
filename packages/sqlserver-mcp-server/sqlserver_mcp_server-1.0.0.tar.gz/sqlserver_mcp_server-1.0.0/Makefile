.PHONY: help install install-dev test test-unit test-integration test-contract lint format typecheck clean build publish

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run all tests
	pytest

test-unit: ## Run unit tests
	pytest tests/unit/

test-integration: ## Run integration tests
	pytest tests/integration/

test-contract: ## Run contract tests
	pytest tests/contract/

lint: ## Run linting
	flake8 src tests
	black --check src tests
	isort --check-only src tests

format: ## Format code
	black src tests
	isort src tests

typecheck: ## Run type checking
	mypy src

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .tox/

build: ## Build package
	python build.py

build-simple: ## Build package (simple)
	python -m build

publish: ## Publish package to PyPI
	python scripts/publish.py

publish-test: ## Publish package to TestPyPI
	python scripts/publish.py --repository testpypi

publish-dry-run: ## Dry run publication
	python scripts/publish.py --dry-run

publish-test-dry-run: ## Dry run publication to TestPyPI
	python scripts/publish.py --repository testpypi --dry-run

coverage: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

docker-build: ## Build Docker image
	docker build -t sqlserver-mcp-server .

docker-run: ## Run Docker container
	docker run -p 8000:8000 sqlserver-mcp-server

docker-compose-up: ## Start services with docker-compose
	docker-compose up -d

docker-compose-down: ## Stop services with docker-compose
	docker-compose down

docker-compose-logs: ## Show docker-compose logs
	docker-compose logs -f
