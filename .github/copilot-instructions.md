# Python Package Copier - AI Instructions

## Project Overview
This is a **Copier template** for generating modern Python packages.
- **Root**: configuration for *this* repo (tests, docs for the template).
- **`template/`**: Jinja2 source files for *generated* projects. Changes here affect output.
- **`copier.yml`**: Defines user prompts/variables (e.g., `{{ package_name }}`).

## Critical Workflows
- **Package Management**: Uses **uv** exclusively. No `pip` or `venv`.
- **Task Running**: `uvx nox` (global install) or `just`.
- **Testing**:
    - **Fast (Unit)**: `just test-fast` (Checks file structure/content generation).
    - **Slow (Integration)**: `just test-slow` (Runs `nox` *inside* generated projects).
    - **Fixture**: Use `copie` fixture (wraps `CopierTestFixture`) in `tests/conftest.py`.
- **Lint/Fix**: `just fix` (Runs `uvx pre-commit`).

## Architecture & Patterns
- **Template Files**: End in `.jinja`. Variables: `{{ min_python_version }}`.
- **Conditional Dirs**: directory names like `{% if include_examples %}examples{% endif %}/`.
- **Tech Stack (Target)**: `uv`, `hatchling` (build), `ruff` (linter), `ty` (types), `nox` (tasks).
- **Nox Configuration**:
    - **Root**: `noxfile.py` tests the template.
    - **Template**: `template/noxfile.py.jinja` tests the *generated* package.
    - **Important**: `nox` is NOT a project dependency; it's run via `uvx`.

## Development Rules
1. **Adding Features**:
    - Update `copier.yml` (prompts).
    - Update `template/` files.
    - Update `tests/conftest.py` default answers.
    - Add test case in `tests/test_template.py`.
2. **Dependencies**:
    - Root `pyproject.toml`: Only for testing the template (copier, pytest).
    - Template `pyproject.toml.jinja`: Definition for generated packages.
3. **CI/CD**:
    - Template uses `tests.yml` (fast/full split).
    - Generated projects get `tests.yml`, `changelog.yml` (git-cliff), `publish-release.yml`.

## Common Commands
```bash
just test-fast        # Run unit tests (fast feedback)
just fix              # Auto-format and lint
just serve            # Preview docs
uv sync --group test  # Install test deps
```
