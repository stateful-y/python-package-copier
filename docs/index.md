![](assets/logo_dark.png#only-dark){width=800}
![](assets/logo_light.png#only-light){width=800}

# Welcome to Python Copier Template's Documentation

A modern Python package template using [Copier](https://copier.readthedocs.io/) that gets you from zero to production-ready in minutes. Answer a few questions, and Copier renders a complete project with testing, linting, documentation, CI/CD, and release automation - all wired up and ready to go.

## Features

- **Modern tooling**: [uv](https://github.com/astral-sh/uv) for 10-100x faster package management
- **Code quality**: [ruff](https://github.com/astral-sh/ruff) for ultra-fast linting and formatting
- **Type checking**: [ty](https://github.com/astral-sh/ty) with strict mode enabled
- **Testing**: [pytest](https://pytest.org/) with coverage and docstring testing
- **Documentation**: [MkDocs](https://www.mkdocs.org/) with Material theme and ReadTheDocs
- **CI/CD**: GitHub Actions for testing, linting, releases, and coverage reporting
- **Automated releases**: Tag-based workflow with changelog generation, GitHub releases, and PyPI publishing with manual approval gate
- **Pre-commit hooks**: Automated code quality checks on every commit
- **Build system**: Modern PEP 517/518 with hatchling + hatch-vcs
- **Task automation**: [nox](https://nox.thea.codes/) and [just](https://github.com/casey/just)

## Get Started

- **[Quick Start](pages/quickstart.md)** - Create your package in 5 minutes

## How-to Guides

- **[Set Up CI/CD Services](pages/how-to/setup-cicd.md)** - Configure Codecov, PyPI, ReadTheDocs
- **[Customize Your Project](pages/how-to/customize-template.md)** - Adjust ruff rules, coverage, hooks
- **[Update from Template](pages/how-to/update-template.md)** - Pull in template improvements
- **[Add Dependencies](pages/how-to/add-dependencies.md)** - Manage runtime and dev dependencies
- **[Contribute to the Template](pages/how-to/contribute.md)** - Help improve the template

## Reference

- **[Template Variables](pages/reference/template-variables.md)** - All configurable options
- **[Project Structure](pages/reference/project-structure.md)** - Generated file tree and roles
- **[Commands](pages/reference/commands.md)** - just, nox, and uv command reference
- **[GitHub Workflows](pages/reference/github-workflows.md)** - CI/CD workflow details
- **[Configuration Files](pages/reference/configuration.md)** - Tool configuration reference

## Explanation

- **[Architecture Overview](pages/explanation/architecture.md)** - How the template is designed
- **[Release Process](pages/explanation/release-process.md)** - How automated releases work
