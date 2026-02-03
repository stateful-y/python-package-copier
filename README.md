<p align="center">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/stateful-y/python-package-copier-template/main/docs/assets/logo_light.png">
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/stateful-y/python-package-copier-template/main/docs/assets/logo_dark.png">
    <img src="https://raw.githubusercontent.com/stateful-y/python-package-copier-template/main/docs/assets/logo_light.png" alt="python-package-copier-template">
  </picture>
</p>


[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Tests](https://github.com/stateful-y/python-package-copier-template/workflows/Tests/badge.svg)](https://github.com/stateful-y/python-package-copier-template/actions/workflows/tests.yml)
[![Documentation](https://readthedocs.org/projects/python-package-copier-template/badge/?version=latest)](https://python-package-copier-template.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, production-ready Python package template using [Copier](https://copier.readthedocs.io/). Save hours of setup time with best practices, modern tooling (uv, ruff, ty, pytest), and comprehensive CI/CD pipelines already configured.

📚 **[Full Documentation](https://python-package-copier-template.readthedocs.io/)**

## Quick Start

```bash
# Create a new package
uvx copier copy gh:stateful-y/python-package-copier-template my-package

# Initialize
cd my-package
uv sync --group dev
uv run pytest
```

## Features

- Fast package management with [uv](https://github.com/astral-sh/uv)
- Code formatting and linting with [ruff](https://github.com/astral-sh/ruff)
- Type checking with [ty](https://github.com/astral-sh/ty)
- Testing with [pytest](https://pytest.org/) and coverage via Codecov
- Documentation with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- Task automation with [nox](https://nox.thea.codes/) and [just](https://github.com/casey/just)
- CI/CD with [GitHub Actions](https://github.com/features/actions)
- Automated tag-based releases with [git-cliff](https://git-cliff.org/) changelog generation, automatic PyPI publishing, and GitHub release creation via changelog PR workflow
- Pre-commit hooks for code quality
- Modern PEP 517/518 build with [hatchling](https://hatch.pypa.io/latest/)

## Template Development

```bash
# Clone and setup
git clone https://github.com/stateful-y/python-package-copier-template.git
cd python-package-copier-template
uv sync --group test --group docs

# Run unit tests (recommended during development)
uv run pytest -m "not slow and not integration"

# Run all tests
just test

# Run specific test suites
uv run pytest tests/test_option_values.py -v        # Individual option validation
uv run pytest tests/test_option_combinations.py -v  # Option combinations & integration
uv run pytest tests/test_github_workflows.py -v     # Workflow validation
uv run pytest tests/test_docs_content.py -v         # Documentation tests

# Run integration tests (comprehensive smoke tests)
uv run pytest -m "integration or slow" -v

# Documentation
just serve
```

See the [Contributing Guide](https://python-package-copier-template.readthedocs.io/contributing/) and [Testing Documentation](docs/TESTING.md) for details.

## Test Structure

The test suite is comprehensive with 6 focused test modules covering:
- Individual option values (edge cases, unicode, derivations)
- Option combinations (license types, Python versions, examples×actions)
- GitHub Actions workflows
- Documentation content
- Generated project functionality (package installation, tests, linting, docs building)
- Comprehensive smoke tests that run all nox sessions

Tests use pytest markers for efficient execution:
- Unit tests run in <5 minutes (default in CI for PRs)
- Integration tests run on main branch (comprehensive validation including all nox sessions)

See [docs/TESTING.md](docs/TESTING.md) for complete test documentation.

## License

MIT License - see the [LICENSE](LICENSE) file for details.
