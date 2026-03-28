# Template Variables

When creating a new project with `uvx copier copy gh:stateful-y/python-package-copier my-package`, you'll be prompted for these variables:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `project_name` | str | *required* | Human-readable project name (e.g., "My Awesome Package") |
| `package_name` | str | *derived* | Python import name with underscores (e.g., "my_awesome_package")<br>Auto-generated from `project_name` |
| `project_slug` | str | *derived* | Repository/URL name with hyphens (e.g., "my-awesome-package")<br>Auto-generated from `project_name` |
| `version` | str | `0.1.0` | Initial package version following [Semantic Versioning](https://semver.org/) |
| `description` | str | `""` | One-line project description for README and package metadata |
| `author_name` | str | *required* | Author or maintainer name |
| `author_email` | str | *required* | Author or maintainer email |
| `github_username` | str | `""` | GitHub username or organization (used in URLs and badges) |
| `license` | str | `MIT` | Project license. Choices:<br>• Apache-2.0<br>• MIT<br>• BSD-3-Clause<br>• GPL-3.0<br>• Proprietary |
| `min_python_version` | str | `3.11` | Minimum Python version. Choices: 3.11, 3.12, 3.13, 3.14 |
| `max_python_version` | str | `3.14` | Maximum Python version. Choices: 3.11, 3.12, 3.13, 3.14<br>Must be ≥ `min_python_version` |
| `include_actions` | bool | `true` | Include GitHub Actions CI/CD workflows (tests, changelog, releases) |
| `include_examples` | bool | `true` | Include `examples/` directory with [marimo](https://marimo.io/) interactive notebooks |

**Note**: Derived variables (`package_name`, `project_slug`) are auto-generated but can be overridden during setup.

**Example**:

- `project_name`: "My Data Tool"
- `package_name`: "my_data_tool" (underscores for Python imports)
- `project_slug`: "my-data-tool" (hyphens for repository names and URLs)

## Variable Effects

### `min_python_version` / `max_python_version`

These variables control several aspects of the generated project:

- **Nox test matrix**: Tests run across all Python versions from min to max
- **CI matrix**: GitHub Actions tests the same version range
- **Ruff target**: The linter targets the minimum Python version
- **Package classifiers**: `pyproject.toml` includes the appropriate `Programming Language :: Python :: 3.x` classifiers

### `include_actions`

When `true`, generates the following in `.github/workflows/`:

- `tests.yml` - CI testing across Python versions and operating systems
- `pr-title.yml` - Conventional commit validation for PR titles
- `changelog.yml` - Automated changelog generation on version tags
- `publish-release.yml` - GitHub Release creation and PyPI publishing
- `nightly.yml` - Daily dependency testing with issue creation on failure

See [GitHub Workflows](github-workflows.md) for full details on each workflow.

### `include_examples`

When `true`, generates:

- `examples/` directory with a sample [marimo](https://marimo.io/) interactive notebook
- `tests/test_examples.py` for testing notebooks
- Additional documentation pages for the example gallery
- Extra dependencies: `numpy`, `pandas`, `plotly`
