.PHONY: help install install-dev test lint format type-check clean build publish docs
.DEFAULT_GOAL := help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=onepass_env --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 src tests
	black --check src tests
	isort --check-only src tests

format: ## Format code
	black src tests
	isort src tests

type-check: ## Run type checking
	mypy src

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean ## Build the package
	python -m build

check-build: build ## Check the built package
	twine check dist/*

publish-test: build ## Publish to Test PyPI
	twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	twine upload dist/*

docs: ## Build documentation
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

setup-dev: install-dev ## Setup development environment
	pre-commit install
	@echo "Development environment setup complete!"

version: ## Show current version
	@python -c "from src.onepass_env.__about__ import __version__; print(__version__)"

demo: ## Run a demo of the import command (requires OP_SERVICE_ACCOUNT_TOKEN)
	@echo "🎬 Running 1pass-env demo..."
	@echo "Checking 1Password configuration..."
	@echo "\n📋 Available import commands:"
	@echo "  1pass-env import --name my-app"
	@echo "  1pass-env import --name my-app --fields API_KEY,DB_URL"
	@echo "  1pass-env import --vault secrets --name my-app --file .env.production"
	@echo "  1pass-env import --debug  # See all available fields"
	@echo "\n🔍 Run 'make help' to see all available commands"
	@echo "\n📚 For full documentation: https://github.com/himakarreddy/1pass-env#readme"
