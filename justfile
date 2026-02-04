# justfile for python-package-copier

# List available commands
default:
    @just --list

# Install dependencies and pre-commit
install:
    uv sync --group dev
    uvx pre-commit install

# Run tests
test:
    uv run pytest -v

# Run fast tests (excludes slow and integration tests)
test-fast:
    uv run pytest -m "not slow and not integration" -v

# Run slow tests (includes integration tests)
test-slow:
    uv run pytest -m "slow or integration" -v

# Format and fix code (via pre-commit)
fix:
    uvx nox -s fix

# Build documentation
docs:
    uvx nox -s build_docs

# Serve documentation locally
serve:
    uvx nox -s serve_docs

# Clean build artifacts
clean:
    rm -rf .nox
    rm -rf build dist *.egg-info
    rm -rf .pytest_cache .ty_cache .ruff_cache
    rm -rf site
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete

# Run all checks
all: fix test
