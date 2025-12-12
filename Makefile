.PHONY: help install test format lint type-check security quality up down rebuild clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test: ## Run tests
	pytest --cov=app --cov-report=term-missing

test-html: ## Run tests with HTML coverage report
	pytest --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

format: ## Format code with black
	black app/ scripts/

lint: ## Lint code with ruff
	ruff check app/ scripts/

lint-fix: ## Lint and fix code with ruff
	ruff check --fix app/ scripts/

type-check: ## Type check with mypy
	mypy app/ --ignore-missing-imports

security: ## Run security scan with bandit
	bandit -r app/ -ll

quality: format lint type-check security test ## Run all quality checks

up: ## Start Docker containers
	docker-compose up -d

down: ## Stop Docker containers
	docker-compose down

rebuild: ## Rebuild Docker containers
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d

clean: ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	rm -f bandit-report.json

api-test: ## Run API integration tests
	chmod +x test_api.sh
	./test_api.sh

ci: ## Run CI checks locally
	make format
	make lint
	make type-check
	make security
	make test

