# Commands

The template provides three ways to run common tasks, organized by use case:

- **just**: Convenience for everyday development (recommended)
- **nox**: Multi-version testing and CI/CD
- **uv run**: Direct tool control when specific options are needed

!!! tip "CI/CD Note"
    GitHub Actions workflows use `uv tool install nox` followed by `nox` commands (not `uvx nox`) to leverage build caching and faster execution.

## Run Tests

=== "just"

    ```bash
    just test        # Run all tests
    just test-fast   # Fast tests only
    just test-slow   # Slow and integration tests
    ```

=== "nox"

    ```bash
    uvx nox -s test           # Test on Python 3.11-3.14
    uvx nox -s test_fast      # Fast tests across versions
    uvx nox -s test_slow      # Slow tests across versions
    ```

=== "uv run"

    ```bash
    uv run pytest -v                           # Run all tests with verbosity
    uv run pytest -m "not slow and not integration"  # Fast tests only
    uv run pytest -k test_specific             # Run specific test
    ```

## Format and Fix Code

=== "just"

    ```bash
    just fix         # Format and fix code
    just all         # Fix + test
    ```

=== "nox"

    ```bash
    uvx nox -s fix   # Format and fix (used in CI)
    ```

=== "uv run"

    ```bash
    uvx pre-commit run --all-files --show-diff-on-failure
    ```

## Build Documentation

=== "just"

    ```bash
    just build       # Build documentation
    just serve       # Build and preview at localhost:8080
    ```

=== "nox"

    ```bash
    uvx nox -s build_docs  # Build documentation
    uvx nox -s serve_docs  # Build and preview at localhost:8080
    ```

=== "uv run"

    ```bash
    uv run mkdocs build --clean              # Build documentation
    uv run mkdocs serve -a localhost:8080    # Preview at localhost:8080
    ```

## Nox Sessions Reference

| Session | Purpose | Python Versions |
|---------|---------|-----------------|
| `test` | Full test suite with doctests | All (min–max) |
| `test_fast` | Fast tests only (excludes slow/integration) | All (min–max) |
| `test_slow` | Slow and integration tests | All (min–max) |
| `test_coverage` | Tests with coverage on default Python | Single (min) |
| `test_compat` | Dependency pinning/compatibility | Single (min) |
| `test_examples` | Run marimo notebook examples | Single |
| `test_docstrings` | Run docstring examples (pytest --doctest) | Single (min) |
| `lint` | Code quality checks (ruff, rumdl, ty) | Single (latest) |
| `fix` | Auto-format and fix (pre-commit) | Single (latest) |
| `build_docs` | Render documentation with MkDocs | Single (latest) |
| `serve_docs` | Local dev server (localhost:8080) | Single (latest) |
| `link_docs` | Check documentation for broken links | Single (latest) |

## Just Commands Reference

| Command | Description |
|---------|-------------|
| `just test` | Run full tests with doctests |
| `just test-fast` | Fast tests only (no slow/integration) |
| `just test-slow` | Slow/integration tests |
| `just test-cov` | Tests with coverage report (HTML) |
| `just test-docstrings` | Docstring examples |
| `just test-compat` | Compatibility with pinned versions |
| `just example [file]` | Open marimo notebook interactively (if `include_examples`) |
| `just test-examples` | Run all example tests (if `include_examples`) |
| `just lint` | Ruff, rumdl, ty checks |
| `just fix` | Run pre-commit on all files |
| `just build` / `just build-fast` | Build docs (fast skips notebook export) |
| `just serve` / `just serve-fast` | Serve docs locally |
| `just link` | Check for broken links |
| `just clean` | Remove build artifacts |
| `just all` | Run fix + test |
