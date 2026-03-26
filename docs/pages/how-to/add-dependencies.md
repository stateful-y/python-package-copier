# How to Add Dependencies

This guide shows you how to add runtime and development dependencies to a project generated from the template.

## Prerequisites

- A generated project with [uv](https://docs.astral.sh/uv/) installed
- Familiarity with Python packaging basics

## Add a Runtime Dependency

Runtime dependencies are packages your users need when they install your package:

```bash
uv add requests
```

This updates `pyproject.toml` under `[project.dependencies]` and refreshes the lock file.

## Add a Development Dependency

Development dependencies are organized into groups. Add to the appropriate group:

```bash
# Add to the tests group
uv add --group tests hypothesis

# Add to the docs group
uv add --group docs mkdocs-glightbox

# Add to the lint group
uv add --group lint bandit
```

After adding, sync your environment:

```bash
uv sync --group dev
```

## Dependency Groups

The template organizes development dependencies into these groups:

| Group | Purpose | Contents |
|-------|---------|----------|
| `dev` | Meta-group - includes all others | References tests, lint, docs, fix, examples |
| `tests` | Testing tools | pytest, pytest-cov, pytest-mock, pytest-xdist, covdefaults, hypothesis |
| `lint` | Code quality | ruff, ty |
| `docs` | Documentation | mkdocs, mkdocs-material, mkdocstrings, pymdown-extensions |
| `fix` | Auto-formatting | pre-commit-uv |
| `examples` | Interactive notebooks | marimo (if `include_examples=true`) |

## Add an Optional Dependency

For features users can opt into:

1. Edit `pyproject.toml` to define the optional group:

    ```toml
    [project.optional-dependencies]
    pandas = ["pandas>=2.0"]
    ```

2. Users install with:

    ```bash
    pip install my-package[pandas]
    ```

## Remove a Dependency

```bash
# Runtime dependency
uv remove requests

# Development dependency from a specific group
uv remove --group tests hypothesis
```

## See Also

- [Configuration Files](../reference/configuration.md) - `pyproject.toml` structure and tool settings
- [How to Customize Your Project](customize-template.md) - other project customizations
