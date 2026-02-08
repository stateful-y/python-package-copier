<p align="center">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/stateful-y/python-package-copier/main/docs/assets/logo_light.png">
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/stateful-y/python-package-copier/main/docs/assets/logo_dark.png">
    <img src="https://raw.githubusercontent.com/stateful-y/python-package-copier/main/docs/assets/logo_light.png" alt="python-package-copier">
  </picture>
</p>


[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Tests](https://github.com/stateful-y/python-package-copier/workflows/Tests/badge.svg)](https://github.com/stateful-y/python-package-copier/actions/workflows/tests.yml)
[![Documentation](https://readthedocs.org/projects/python-package-copier/badge/?version=latest)](https://python-package-copier.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, production-ready Python package template using [Copier](https://copier.readthedocs.io/). Save hours of setup time with best practices, modern tooling (uv, ruff, ty, pytest), and comprehensive CI/CD pipelines already configured.

📚 **[Full Documentation](https://python-package-copier.readthedocs.io/)**

## Quick Start

```bash
# Create a new package
uvx copier copy gh:stateful-y/python-package-copier my-package

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
- Automated tag-based releases with [git-cliff](https://git-cliff.org/) changelog generation, GitHub release creation, and PyPI publishing with manual approval gate
- Pre-commit hooks for code quality
- Modern PEP 517/518 build with [hatchling](https://hatch.pypa.io/latest/)

## Template Development

```bash
# Clone and setup
git clone https://github.com/stateful-y/python-package-copier.git
cd python-package-copier
uv sync --group test --group docs

# Run unit tests (recommended during development)
uv run pytest -m "not slow and not integration"
# or: just test-fast

# Run all tests
uv run pytest -v
# or: just test

# Format and fix code
uvx nox -s fix
# or: just fix

# Build documentation
uvx nox -s serve_docs
# or: just serve
```

See the [Contributing Guide](https://python-package-copier.readthedocs.io/pages/contributing/) for complete development and testing documentation.

## License

MIT License - see the [LICENSE](LICENSE) file for details.

<p align="center">
  <img src="docs/assets/made_by_stateful-y.png" alt="Made by stateful-y">
</p>
