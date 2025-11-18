.PHONY: help format format-check lint lint-fix type-check all-checks install-dev clean test test-cov build publish publish-test publish-check

# Poetry detection
POETRY := $(shell which poetry 2>/dev/null)

# Python interpreter - prefer Poetry, then .venv, otherwise system
ifdef POETRY
    # Use poetry run for all commands
    PYTHON := python3
    POETRY_RUN := poetry run
else ifneq ($(wildcard .venv/bin/python),)
    PYTHON := .venv/bin/python
    POETRY_RUN :=
else
    PYTHON := python3
    POETRY_RUN :=
endif

# Use uv if available, otherwise pip
UV := $(shell which uv 2>/dev/null)
ifdef UV
    PIP := uv pip
else
    PIP := $(PYTHON) -m pip
endif

# Directories
SRC_DIR := aiorobokassa
TESTS_DIR := tests

# Tools - use poetry run if available
ifdef POETRY_RUN
    BLACK := $(POETRY_RUN) black
    RUFF := $(POETRY_RUN) ruff
    MYPY := $(POETRY_RUN) mypy
    PYTEST := $(POETRY_RUN) pytest
else
    BLACK := $(PYTHON) -m black
    RUFF := $(PYTHON) -m ruff
    MYPY := $(PYTHON) -m mypy
    PYTEST := $(PYTHON) -m pytest
endif

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install-dev: ## Install development dependencies with Poetry
	@if [ -z "$(POETRY)" ]; then \
		echo "Error: Poetry is not installed. Install it with: curl -sSL https://install.python-poetry.org | python3 -"; \
		exit 1; \
	fi
	@echo "Installing development dependencies with Poetry..."
	poetry install --extras dev

format: ## Format code with black
	@echo "Formatting code with black..."
	$(BLACK) $(SRC_DIR) || true
	@if [ -d "tests" ]; then $(BLACK) tests || true; fi
	@if [ -d "examples" ]; then $(BLACK) examples || true; fi

format-check: ## Check code formatting without making changes
	@echo "Checking code formatting..."
	$(BLACK) --check $(SRC_DIR)
	@if [ -d "tests" ]; then $(BLACK) --check tests || true; fi
	@if [ -d "examples" ]; then $(BLACK) --check examples || true; fi

lint: ## Run ruff linter
	@echo "Running ruff linter..."
	$(RUFF) check $(SRC_DIR)
	@if [ -d "tests" ]; then $(RUFF) check tests || true; fi
	@if [ -d "examples" ]; then $(RUFF) check examples || true; fi

lint-fix: ## Run ruff linter and auto-fix issues
	@echo "Running ruff linter with auto-fix..."
	$(RUFF) check --fix $(SRC_DIR)
	@if [ -d "tests" ]; then $(RUFF) check --fix tests || true; fi
	@if [ -d "examples" ]; then $(RUFF) check --fix examples || true; fi

type-check: ## Run mypy type checker
	@echo "Running mypy type checker..."
	$(MYPY) $(SRC_DIR)

all-checks: format-check lint type-check ## Run all checks (format, lint, type-check)
	@echo "All checks passed!"

clean: ## Clean cache and temporary files
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf dist/ build/ .venv/ poetry.lock 2>/dev/null || true
	@echo "Clean complete!"

test: ## Run tests
	@echo "Running tests..."
	$(PYTEST) tests/ -v

test-cov: ## Run tests with coverage
	@echo "Running tests with coverage..."
	$(PYTEST) tests/ --cov=$(SRC_DIR) --cov-report=html --cov-report=term

# Poetry commands (POETRY already defined above)

build: clean ## Build distribution packages with Poetry
	@if [ -z "$(POETRY)" ]; then \
		echo "Error: Poetry is not installed. Install it with: curl -sSL https://install.python-poetry.org | python3 -"; \
		exit 1; \
	fi
	@echo "Building distribution packages with Poetry..."
	poetry build
	@echo "Build complete! Packages are in dist/"

publish-test: build ## Publish to TestPyPI (for testing)
	@if [ -z "$(POETRY)" ]; then \
		echo "Error: Poetry is not installed."; \
		exit 1; \
	fi
	@echo "Publishing to TestPyPI..."
	@echo "Note: If you have account-scoped token, set:"
	@echo "  export POETRY_HTTP_BASIC_TESTPYPI_USERNAME='__token__'"
	@echo "  export POETRY_HTTP_BASIC_TESTPYPI_PASSWORD='your-token'"
	poetry publish --repository testpypi
	@echo "Published to TestPyPI! Test with: pip install -i https://test.pypi.org/simple/ aiorobokassa"

publish: build ## Publish to PyPI
	@if [ -z "$(POETRY)" ]; then \
		echo "Error: Poetry is not installed."; \
		exit 1; \
	fi
	@echo "Publishing to PyPI..."
	@echo "Note: If you have account-scoped token, set:"
	@echo "  export POETRY_HTTP_BASIC_PYPI_USERNAME='__token__'"
	@echo "  export POETRY_HTTP_BASIC_PYPI_PASSWORD='your-token'"
	poetry publish
	@echo "Published to PyPI!"

publish-check: build ## Check distribution before publishing
	@echo "Checking distribution..."
	@if [ -z "$(POETRY)" ]; then \
		echo "Error: Poetry is not installed."; \
		exit 1; \
	fi
	poetry check
	@echo "Distribution check complete!"

docs: ## Build documentation
	@echo "Building documentation..."
	@if [ -z "$(POETRY)" ]; then \
		echo "Error: Poetry is not installed."; \
		exit 1; \
	fi
	@if [ -z "$(POETRY_RUN)" ]; then \
		cd docs && sphinx-build -b html . _build/html; \
	else \
		cd docs && $(POETRY_RUN) sphinx-build -b html . _build/html; \
	fi
	@echo "Documentation built in docs/_build/html/"

docs-serve: docs ## Build and serve documentation
	@echo "Serving documentation at http://localhost:8000"
	cd docs/_build/html && python3 -m http.server 8000

docs-clean: ## Clean documentation build files
	@echo "Cleaning documentation..."
	rm -rf docs/_build docs/.doctrees
	@echo "Documentation cleaned!"

