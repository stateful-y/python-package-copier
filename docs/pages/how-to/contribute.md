# How to Contribute to the Template

We welcome contributions to python-package-copier! This guide helps you get set up and submit your first pull request.

## Types of Contributions

Not sure where to start? Pick a path:

- **Report a bug**: [Open an issue](https://github.com/stateful-y/python-package-copier/issues/new) with steps to reproduce, expected behavior, and your environment (Python, uv, copier versions)
- **Fix a bug**: Find an open issue, comment that you're working on it, then follow the development workflow below
- **Add a template feature**: Update `copier.yml` + `template/` files + tests - see [Modifying the Template](#modifying-the-template)
- **Improve documentation**: Edit files in `docs/` and run `just serve` to preview

## Repository Structure

!!! important "Scope confusion is the #1 contributor issue"
    This repository has three distinct layers. Understanding them prevents most mistakes.

```text
python-package-copier/
├── copier.yml          # Template configuration (prompts/variables)
├── template/           # Jinja2 source files → what users GET
│   ├── pyproject.toml.jinja
│   ├── noxfile.py.jinja
│   └── ...
├── tests/              # Tests for the template itself
├── docs/               # Documentation for this template repo
├── noxfile.py          # Nox config for testing the template
└── pyproject.toml      # Dependencies for template development
```

| Layer | Path | Purpose |
|-------|------|---------|
| **Root project** | `noxfile.py`, `pyproject.toml`, `tests/`, `docs/` | Infrastructure for developing and testing the template |
| **Template source** | `template/` | Jinja2 files rendered by Copier into generated projects |
| **Generated project** | *(created by `copier copy`)* | The user's actual Python package - not in this repo |

Changes to files in `template/` affect what users get. Changes to root files affect how the template is developed and tested.

## Setup

```bash
git clone https://github.com/stateful-y/python-package-copier.git
cd python-package-copier

# Install dependencies
uv sync --group test --group docs

# Install pre-commit hooks (optional but recommended)
uv run pre-commit install
```

## Test Template Changes

### Test Categories

- **Fast tests**: Validate template generation without running subprocesses
- **Slow tests**: Tests marked with `@pytest.mark.slow` that take longer
- **Integration tests**: Tests marked with `@pytest.mark.integration` that use `copier.run_copy()`

### Test Commands

=== "just"

    ```bash
    just test-fast   # Fast tests (recommended during development)
    just test-slow   # Slow and integration tests
    just test        # All tests
    ```

=== "nox"

    ```bash
    uvx nox -s test_fast   # Fast tests across versions
    uvx nox -s test_slow   # Slow tests across versions
    uvx nox -s test        # All tests
    ```

=== "uv run"

    ```bash
    uv run pytest -m "not slow and not integration" -v   # Fast tests
    uv run pytest -m "slow or integration" -v            # Slow tests
    uv run pytest -v                                     # All tests
    ```

### When to Mark Tests

- Use `@pytest.mark.slow` for tests that take more than a few seconds
- Use `@pytest.mark.integration` for tests that run `copier.run_copy()` or execute commands in generated projects
- Tests without marks should be fast unit tests that only validate template structure and content

### Manual Testing with `just gen`

`just gen` generates a temporary project, runs a recipe inside it, and cleans up automatically:

```bash
just gen build          # Build docs in a generated project
just gen test           # Run tests in a generated project
just gen lint           # Run linters
just gen fix            # Format and fix code
just examples=false gen build  # Generate without examples
```

### CI Test Strategy

| PR State | Fast Tests | Full Tests | Lint | Total Jobs |
|----------|-----------|------------|------|------------|
| Draft | Ubuntu only (2 jobs) | - | 1 job | 3 |
| Ready | All OS (6 jobs) | All Python versions (4 jobs) | 1 job | 11 |

## Modifying the Template

### Edit Template Files

Template files are in `template/`. Files ending in `.jinja` are rendered by Copier with variable substitution.

### Edit Template Configuration

Edit `copier.yml` to add or modify template prompts and variables.

### Test Your Changes

After making changes:

1. Run `just test-fast` to test template generation
2. Run `just gen build` to verify the generated project builds docs
3. Run `just gen test` to verify tests pass in the generated project

## Code Quality

=== "just"

    ```bash
    just fix         # Format and fix code
    just all         # Fix + test
    ```

=== "nox"

    ```bash
    uvx nox -s fix
    ```

=== "uv run"

    ```bash
    uvx pre-commit run --all-files --show-diff-on-failure
    ```

## Documentation

=== "just"

    ```bash
    just build       # Build documentation
    just serve       # Preview at localhost:8080
    ```

=== "nox"

    ```bash
    uvx nox -s build_docs
    uvx nox -s serve_docs
    ```

## Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/). All commit messages must follow:

```text
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

Breaking changes: Add `!` after the type (`feat!: remove deprecated API`) or include `BREAKING CHANGE:` in the footer.

The pre-commit hook validates your commit messages automatically.

## Before You Open a PR

- [ ] Run `just test-fast` - all fast tests pass
- [ ] Run `just fix` - code is formatted and linted
- [ ] Write or update tests for your changes
- [ ] If you changed docs, run `just serve` and verify they render
- [ ] Use conventional commit messages
- [ ] If adding a template feature, update `copier.yml` and add a test in `tests/`

## Release Process

!!! note "Maintainers only"
    Releases are handled by project maintainers via git tags. Contributors do not need to manage releases.

Maintainers: see [About the Release Process](../explanation/release-process.md) for the full workflow.

## Troubleshooting

**Problem: `uvx nox` not found**
: Install uv first: `curl -LsSf https://astral.sh/uv/install.sh | sh`. Nox is run via `uvx`, not installed globally.

**Problem: Pre-commit fails on first run**
: Run `uv sync --group test` first to install all dependencies, then `uv run pre-commit install`.

**Problem: Tests pass locally but fail in CI**
: Check the Python version matrix. CI tests across 3.11–3.14 and multiple operating systems. Your local Python may differ.

**Problem: `copier copy` fails during integration tests**
: Ensure you have a recent copier version: `uvx copier --version`. The template requires copier 9+.

**Problem: `just gen` fails**
: Check that `uv` and `copier` are installed and available in your PATH. Run `just gen test` with `--verbose` for more details.

## See Also

- [Commands](../reference/commands.md) - full command reference
- [Template Variables](../reference/template-variables.md) - what each variable controls
- [Architecture Overview](../explanation/architecture.md) - understanding the template design
