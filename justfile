# justfile for python-package-copier

# List available commands
default:
    @just --list

# Install dependencies and pre-commit
install:
    uv sync --group dev
    uvx pre-commit install

# Run tests with parallel execution
test:
    uv run pytest tests/ -n auto -v

# Run fast tests (excludes slow and integration tests)
test-fast:
    uv run pytest tests/ -m "not slow and not integration" -n auto -v

# Run slow tests (includes integration tests)
test-slow:
    uv run pytest tests/ -m "slow or integration" -n auto -v

# Run linters
lint:
    uv run ruff check tests/
    uvx rumdl check .

# Format and fix code (via pre-commit)
fix:
    uvx pre-commit run --all-files --show-diff-on-failure

# Check built docs for dead links (build first with 'just build')
link:
    uvx linkchecker site/index.html --no-status --no-warnings --ignore-url 'material/overrides'

# Build documentation
build:
    uv run mkdocs build --clean

# Serve documentation locally
serve:
    @echo "###### Starting local server. Press Control+C to stop server ######"
    uv run mkdocs serve -a localhost:8080

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

# --- Run commands inside a generated project ---

generated_dir := ".generated"
examples := "true"

# Generate a temporary project, run a just recipe in it, then clean up
# Usage: just gen <recipe>          (with examples)
#        just examples=false gen <recipe>  (without examples)
gen +recipe:
    #!/usr/bin/env bash
    set -euo pipefail
    dest="$(pwd)/{{ generated_dir }}"
    rm -rf "$dest"
    uvx copier copy --defaults \
        --data project_name="Test Project" \
        --data package_name="test_project" \
        --data description="Generated test project" \
        --data author_name="Test Author" \
        --data author_email="test@example.com" \
        --data github_username="testuser" \
        --data include_examples="{{ examples }}" \
        --data include_actions=true \
        --vcs-ref=HEAD \
        . "$dest"
    cd "$dest"
    git init -q && git add -A && git commit -q -m "init" --no-verify
    cleanup() { rm -rf "$dest"; }
    trap cleanup EXIT
    just {{ recipe }}
