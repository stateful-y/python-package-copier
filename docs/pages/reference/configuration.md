# Configuration Files

## Technology Stack

| Category | Tool | Purpose |
|----------|------|---------|
| **Build** | hatchling | Modern build backend |
| **Build** | hatch-vcs | Git-based versioning |
| **Package Manager** | uv | Fast dependency management |
| **Formatter** | ruff | Code formatting |
| **Linter** | ruff | Code linting |
| **Type Checker** | ty | Static type checking |
| **Test Framework** | pytest | Unit testing |
| **Docstring Testing** | pytest-doctest | Test code examples in docstrings |
| **Coverage** | pytest-cov | Code coverage |
| **Test Automation** | nox | Multi-environment testing |
| **Pre-commit** | pre-commit | Git hooks |
| **Documentation** | MkDocs | Static site generator |
| **Doc Theme** | Material | Beautiful theme |
| **API Docs** | mkdocstrings | Docstring extraction |
| **Task Runner** | just | Command automation |
| **CI/CD** | GitHub Actions | Automation platform |
| **Coverage Reporting** | Codecov | Test coverage tracking |
| **Dependency Updates** | Dependabot | Automated updates |
| **Changelog** | git-cliff | Automated changelog generation |
| **Commit Convention** | commitizen | Conventional commits enforcement |

## pyproject.toml

Central configuration containing:

- Project metadata (name, version, description)
- Dependencies and dependency groups
- Build system configuration (hatchling + hatch-vcs)
- Tool configurations (ruff, pytest, coverage)

### Ruff Configuration

```toml
[tool.ruff]
line-length = 120
target-version = "py3XX"  # Set to min_python_version

[tool.ruff.format]
preview = true
docstring-code-format = true

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PL", "T201"]
```

### Coverage Configuration

```toml
[tool.coverage.run]
branch = true
plugins = ["covdefaults"]

[tool.coverage.report]
fail_under = 1  # Permissive default
```

### Interrogate (Docstring Coverage)

```toml
[tool.interrogate]
fail-under = 75
exclude = ["setup.py", "docs", "build", "*_version.py"]
ignore-init-method = true
ignore-init-module = true
```

## .pre-commit-config.yaml

Pre-commit hooks configured in generated projects:

| Hook | Purpose |
|------|---------|
| trailing-whitespace | Remove trailing whitespace |
| end-of-file-fixer | Ensure files end with newline |
| check-yaml | Validate YAML syntax |
| check-toml | Validate TOML syntax |
| check-json | Validate JSON syntax |
| check-added-large-files | Prevent large file commits |
| check-merge-conflict | Detect merge conflict markers |
| debug-statements | Detect debugger imports |
| mixed-line-ending | Normalize line endings |
| commitizen | Enforce conventional commit messages (if `include_actions=true`) |
| interrogate | Check docstring coverage (75% minimum) |
| ruff | Format and lint code |
| rumdl | Lint markdown files (MkDocs flavor) |
| ty | Type checking via uv run |

## mkdocs.yml

Documentation site configuration:

- Material for MkDocs theme with light/dark toggle
- Search, tags, and mkdocstrings plugins
- Code highlighting with line numbers and copy buttons
- Mermaid diagram support
- MathJax for LaTeX equations
- Tabbed content and admonitions

## .readthedocs.yml

ReadTheDocs build configuration:

- Python 3.13 build environment
- Ubuntu 24.04 base image
- uv integration for fast installs
- Post-build link checking via linkchecker
- Syncs the `docs` dependency group
