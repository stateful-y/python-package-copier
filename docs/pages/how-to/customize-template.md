# How to Customize Your Project

This guide shows you how to modify common settings in a project generated from the template. These changes are safe to make and will be preserved when you [update from the template](update-template.md).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- A project generated with `uvx copier copy gh:stateful-y/python-package-copier my-package`

## Customize Ruff Rules

Edit `pyproject.toml` to adjust linting and formatting:

```toml
[tool.ruff]
line-length = 88  # Change from default 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PL", "T201"]
ignore = ["PLR0913"]  # Allow many arguments
```

Run `just fix` to apply the new rules.

## Adjust Coverage Thresholds

The default coverage threshold is intentionally permissive (`fail_under = 1`). To increase it:

```toml
[tool.coverage.report]
fail_under = 80  # Require 80% coverage
```

## Customize Pre-commit Hooks

Edit `.pre-commit-config.yaml` to add or remove hooks. For example, to add a security scanner:

```yaml
- repo: https://github.com/PyCQA/bandit
  rev: 1.8.3
  hooks:
    - id: bandit
      args: ["-r", "src/"]
```

After editing, update hooks and run them:

```bash
uv run pre-commit autoupdate
uv run pre-commit run --all-files
```

## Customize the Docstring Coverage Threshold

The default requires 75% docstring coverage. To change it:

```toml
[tool.interrogate]
fail-under = 90  # Require 90% docstring coverage
```

## Add Custom Nox Sessions

Edit `noxfile.py` to add project-specific automation sessions. For example, a benchmarking session:

```python
@nox.session(python=PYTHON_VERSIONS[0])
def benchmark(session: nox.Session) -> None:
    """Run performance benchmarks."""
    session.install(".[tests]", "pytest-benchmark")
    session.run("pytest", "benchmarks/", "--benchmark-only")
```

## Customize Documentation Theme

Edit `mkdocs.yml` to change the theme colors, logo, or features:

```yaml
theme:
  palette:
    - scheme: default
      primary: blue  # Change color
      accent: amber
```

## Common Variations

- **Switching build backend**: Possible but requires updating `pyproject.toml` `[build-system]` and removing hatch-vcs config
- **Adding a CLI**: Add an entry point in `pyproject.toml` `[project.scripts]` and create the CLI module

## See Also

- [Template Variables](../reference/template-variables.md) - what each variable controls
- [Configuration Files](../reference/configuration.md) - full configuration reference
- [How to Add Dependencies](add-dependencies.md) - managing project dependencies
