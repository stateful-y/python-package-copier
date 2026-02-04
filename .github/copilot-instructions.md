# Python Package Copier - AI Coding Agent Instructions

## Project Overview

This is a **Copier template project** that generates modern Python packages. You're working on the *template itself*, not a generated project. The `template/` directory contains Jinja2 templates (`.jinja` files) that copier renders when creating new Python packages.

**Key distinction**:
- Changes to root files (`noxfile.py`, `pyproject.toml`) affect this template repository
- Changes to `template/*.jinja` files affect generated projects
- Root `pyproject.toml` only needs test/docs dependencies; generated projects in `template/pyproject.toml.jinja` define the full Python package setup

## Template Architecture

### Directory Structure
- **`template/`**: Jinja2 templates for generated projects
  - All files ending in `.jinja` are rendered by Copier
  - Variable substitution uses `{{ variable_name }}` syntax
  - Non-.jinja files are copied verbatim
  - Conditional directories use Jinja syntax in names: `{% if include_actions %}workflows{% endif %}/`
- **`copier.yml`**: Template configuration defining user prompts and defaults
  - Defines all template variables, types, help text, defaults, and choices
  - Includes validators for cross-field validation (e.g., max >= min Python version)
- **Root files**: Development setup for the template repository itself
  - Root `pyproject.toml` contains only test/docs dependencies (not package deps)
  - Root `noxfile.py` defines sessions for template development

### Template Variables
Variables defined in `copier.yml` are used in `.jinja` files:
- `{{ package_name }}`: Python import name (underscores)
- `{{ project_slug }}`: Repository/URL name (hyphens)
- `{{ project_name }}`: Human-readable display name
- `{{ python_version }}`: Minimum Python version (e.g., "3.11")
- `{{ author_name }}`, `{{ author_email }}`: Maintainer info
- `{{ github_username }}`: GitHub org/user for URLs

See `template/pyproject.toml.jinja` and `template/noxfile.py.jinja` for usage examples.

## Developer Workflows

### Testing Template Changes
```bash
# Fast tests only (unit tests, no subprocess calls) - recommended during development
uv run pytest -m "not slow and not integration"

# All tests including integration tests
uv run pytest -v

# Or use nox for multi-version testing
uvx nox -s tests
```

The test suite uses copier's `run_copy()` to generate actual projects in temp directories (`tmp_path`), then validates:
- File/directory structure matches expectations
- Generated content includes required tools and configurations
- Multiple license options generate correctly
- GitHub workflows are properly templated with uv and ty

**Test Organization**:
- **Unit tests** (unmarked): Fast validation of template generation and content
- **`@pytest.mark.integration`**: Tests that run generated project commands (nox sessions, pytest, etc.)
- **`@pytest.mark.slow`**: Long-running tests (typically 30+ seconds each)
- **Marker usage**: Use `-m "not slow and not integration"` to run fast tests only
- Test modules: `test_template.py` (comprehensive), `test_option_values.py` (individual options), `test_option_combinations.py` (option interactions), `test_github_workflows.py` (workflow validation), `test_docs_content.py` (documentation), `test_template_options.py` (template option handling)
- All test modules are configured in `pyproject.toml` under `[tool.pytest.ini_options]`

**Important**: `CopierTestFixture` (in [tests/conftest.py](tests/conftest.py)) provides default answers for all prompts. Tests use `result.project_dir` to access the generated temporary project. Assertions should verify *generated* project content, not template source files.

**Common test pattern**:
```python
def test_feature(copie):
    result = copie.copy(extra_answers={"license": "MIT"})
    assert (result.project_dir / "LICENSE").is_file()
    content = (result.project_dir / "pyproject.toml").read_text()
    assert "expected_string" in content
```

**Integration test pattern** (runs actual commands in generated project):
```python
@pytest.mark.integration
@pytest.mark.slow
def test_generated_project_builds(copie):
    result = copie.copy()
    subprocess.run(["uvx", "nox", "-s", "tests"], cwd=result.project_dir, check=True)
```

See [tests/test_template.py](tests/test_template.py) for assertion patterns.

### Code Quality

Format and fix code:

=== "just"

    ```bash
    just fix
    ```

=== "nox"

    ```bash
    uvx nox -s fix
    ```

=== "uv run"

    ```bash
    uv run ruff format src tests
    uv run ruff check src tests --fix
    uv run ty check src
    ```

Check without fixing:

```bash
just check
```

### Documentation

Build docs:

=== "just"

    ```bash
    just docs
    ```

=== "nox"

    ```bash
    uvx nox -s build_docs
    ```

=== "uv run"

    ```bash
    uv run mkdocs build
    ```

Live preview at localhost:8080:

=== "just"

    ```bash
    just serve
    ```

=== "nox"

    ```bash
    uvx nox -s serve_docs
    ```

=== "uv run"

    ```bash
    uv run mkdocs serve
    ```

## Project-Specific Conventions

### Tooling Stack
Generated projects use this opinionated modern Python stack:
- **uv**: Fast dependency management (replaces pip/poetry)
- **hatchling + hatch-vcs**: Build backend with VCS-based versioning
- **ruff**: Combined linter + formatter (replaces black, isort, flake8)
- **ty**: Type checker (not mypy/pyright)
- **nox**: Task runner with uv backend (installed globally via `uvx nox`, NOT a project dependency)
- **pytest**: Testing with coverage via `covdefaults`
- **marimo**: Interactive Python notebooks (optional, if `include_examples: true`)

**Critical**: nox is NOT listed in `template/pyproject.toml.jinja` dependencies. It's installed system-wide with `uv tool install nox` or invoked via `uvx nox`. Generated projects' GitHub workflows use `uv tool install nox` for CI. Do not add nox to dependency groups when testing if it appears in generated projects.

### Nox Sessions
Both template and generated projects use nox with `uv` backend:
- Sessions install deps via `session.run_install("uv", "sync", ...)`
- Set `UV_PROJECT_ENVIRONMENT` env var to point to nox's virtualenv
- Default sessions defined in `nox.options.sessions`

Example from `template/noxfile.py.jinja`:
```python
nox.options.default_venv_backend = "uv|virtualenv"
session.run_install("uv", "sync", "--group", "dev",
    env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location})
```

**Generated project sessions**:
- `test_fast`: Run fast tests only (excludes slow and integration)
- `test_slow`: Run slow and integration tests only
- `test_coverage`: Run tests with coverage (single Python version)
- `test`: Run tests across multiple Python versions (no coverage)
- `doctest`: Validate docstrings with doctest
- `run_examples` (if enabled): Run marimo notebooks as scripts to validate they execute
- `fix`: Run pre-commit hooks for formatting/linting/type checking
- `lint`: Legacy session (use `fix` instead)
- `build_docs` / `serve_docs`: Build or preview documentation

### Justfile Commands
The `justfile` provides convenient shortcuts that delegate to either `uv run` (simple) or `uvx nox` (complex):

**Template repository commands**:
- `just test`: Run all tests
- `just test-fast`: Fast tests only (recommended for development)
- `just test-slow`: Slow and integration tests
- `just fix`: Format and fix code (via nox fix session)
- `just check`: Fix + test
- `just docs`: Build documentation
- `just serve`: Documentation preview

**Generated project commands** (same as above, plus):
- `just test-cov`: Run tests with coverage
- `just doctest`: Run docstring examples
- `just example` (if enabled): Run marimo notebook interactively

### Command Documentation Pattern
All documentation uses mkdocs-material tab syntax to show three equivalent ways to run commands:

```markdown
=== "just"

    ```bash
    just test
    ```

=== "nox"

    ```bash
    uvx nox -s test
    ```

=== "uv run"

    ```bash
    uv run pytest -v
    ```
```

This three-tier hierarchy serves different needs:
- **just**: Convenience for everyday development (recommended)
- **nox**: Multi-version testing and CI/CD
- **uv run**: Direct tool control when specific options are needed

### Pre-commit Configuration
Generated projects include pre-commit hooks for:
- Ruff formatting and linting (auto-fix enabled)
- Interrogate (docstring coverage, excludes tests/)
- Type checking with ty (src/ only, via local hook)
- Standard checks (trailing whitespace, YAML/TOML validation)

Note: `ty` runs as a local hook requiring system installation.

## Common Patterns

### Adding Template Variables
1. Add question to `copier.yml` with type, help text, default
2. Use `{{ variable_name }}` in `.jinja` files
3. Update `tests/conftest.py` fixture if adding required fields
4. Test generation with `pytest`

### Modifying Generated Structure
When adding files to generated projects:
- Create in `template/` with `.jinja` suffix if needs variable substitution
- Conditional files/directories use Jinja2 control flow in directory names (see `.github/workflows` example)
- Update `tests/test_template.py` expected files/dirs lists
- Document in `docs/structure.md` (if exists)

### Version Constraints
- Template itself: `requires-python = ">=3.11"` (in root `pyproject.toml`)
- Generated projects: Uses `{{ python_version }}` from copier prompt
- Generated `noxfile.py.jinja` tests against multiple Python versions (3.11-3.14)

## Integration Points

### Template Repository CI/CD
The template repository itself has GitHub Actions workflows:
- **`tests.yml`**: Two-tier test strategy optimized for fast feedback
  - `test-fast`: Runs unit tests only (`-m "not slow and not integration"`) on min+max Python versions (3.11, 3.14)
    - Draft PRs: Ubuntu only (2 jobs)
    - Ready PRs/Main: All OS - Ubuntu, Windows, macOS (6 jobs)
  - `test-full`: Runs complete test suite on Ubuntu across all Python versions (3.11-3.14) for ready PRs and main branch (4 jobs)
  - `lint`: Code quality checks
- **`changelog.yml`**: Updates CHANGELOG.md via git-cliff when version tags are pushed
- **`publish-release.yml`**: Creates GitHub releases when changelog PR is merged (template repo does not publish to PyPI)
- **`pr-title.yml`**: Validates PR titles follow conventional commit format

**Test execution strategy**: Boundary version testing (min+max Python) provides quick feedback while maintaining compatibility coverage. Full test suite validates all versions comprehensively before merge.

### GitHub Actions
Generated projects include workflows (if `include_actions: true`):
- `tests.yml`: Run nox tests on push/PR with matrix strategy across Python versions
- `changelog.yml`: Automated changelog generation with git-cliff on version tags, builds package distributions
- `publish-release.yml`: Creates GitHub release when changelog PR is merged, then publishes to PyPI with manual approval gate
- `nightly.yml`: Scheduled dependency testing against latest package versions
- `pr-title.yml`: Validate PR titles follow conventional commit format
- `dependabot.yml`: Automated dependency updates

All workflows use `uv tool install nox` to install nox in CI (not as a project dependency).

### Changelog & Versioning
Generated projects use automated changelog and version management with a manual approval gate for PyPI releases:
- **git-cliff**: Generates changelogs from conventional commits (config in `.git-cliff.toml.jinja`)
- **commitizen**: Enforces conventional commit messages via pre-commit hook
- **hatch-vcs**: VCS-based versioning (reads from git tags, writes to `_version.py`)
- Changelog format follows "Keep a Changelog" style
- On tag push, `changelog.yml` workflow auto-generates CHANGELOG.md and builds distributions
- After changelog PR merge, `publish-release.yml` creates GitHub Release, then requires manual approval before PyPI publish

Example commit format: `feat: add new feature` or `fix: resolve bug`

### ReadTheDocs
- Always included via `.readthedocs.yml.jinja`
- Uses mkdocs-material theme
- Builds with uv for fast installs

### Copier Updates
Generated projects include `.copier-answers.yml` for template updates:
```bash
copier update --trust
```

## Critical Files

- **`copier.yml`**: All template configuration and user prompts
- **`tests/conftest.py`**: Copier test fixture with default answers
- **`template/pyproject.toml.jinja`**: Core dependency and tool config for generated projects
- **`template/noxfile.py.jinja`**: Task automation for generated projects
- **`template/.pre-commit-config.yaml.jinja`**: Code quality enforcement

## Development Setup

```bash
# Initial setup
uv sync --group test --group docs

# Quick validation
just all  # runs check + test

# Before committing
just pre-commit
```

Avoid `pip install` or `python -m venv` - this project uses uv exclusively.
