# Quick Start

Get your Python package up and running in 5 minutes.

## Prerequisites

Install [uv](https://docs.astral.sh/uv/) for fast package management:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Create Your Package

```bash
uvx copier copy gh:stateful-y/python-package-copier my-package
```

Answer the prompts about your project. You'll be asked for:

- `project_name`: Human-readable name (e.g., "My Awesome Package")
- `package_name`: Python import name with underscores (auto-derived, e.g., "my_awesome_package")
- `project_slug`: Repository/URL name with hyphens (auto-derived, e.g., "my-awesome-package")
- `version`: Initial version number (default: "0.1.0")
- `description`: One-line project description
- `author_name`: Your name
- `author_email`: Your email address
- `github_username`: GitHub username or organization (optional)
- `license`: Choose from MIT (default), Apache-2.0, BSD-3-Clause, GPL-3.0, or Proprietary
- `min_python_version`: Minimum Python version (default: 3.11, choices: 3.11-3.14)
- `max_python_version`: Maximum Python version (default: 3.14, choices: 3.11-3.14)
- `include_actions`: Include GitHub Actions CI/CD workflows? (default: true)
- `include_examples`: Include interactive [marimo](https://marimo.io/) notebooks in `examples/`? (default: true)

See [Template Variables](reference.md#template-variables) in the Reference Guide for detailed descriptions.

## Initialize Your Project

```bash
cd my-package

# Install dependencies
uv sync --group dev

# Set up pre-commit hooks
uv run pre-commit install
```

## Verify Setup

```bash
# Run tests
uv run pytest

# View documentation
uvx nox -s serve_docs
```

## Push to GitHub

```bash
git init
git add .
git commit -m "feat: initial project setup"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/my-package.git
git branch -M main
git push -u origin main
```

## Setup CI/CD

### Codecov (Coverage Reporting)

1. Sign up at [codecov.io](https://codecov.io/)
2. Add your repository
3. Go to Settings → Copy the upload token
4. In GitHub: Settings → Secrets and variables → Actions → New secret
5. Add `CODECOV_TOKEN` with your token

**Note**: This token is used by multiple workflows: `tests.yml` (on every push/PR) and `nightly.yml` (daily dependency testing).

### PyPI Publishing (Automated Releases)

**Required setup** (for automated releases):

1. **PyPI Trusted Publishing** (OIDC, no tokens needed):
   - Create account at [pypi.org](https://pypi.org/account/register/)
   - Publish your first release manually, or create the project on PyPI
   - Go to your project → Manage → Publishing
   - Add a new publisher with:
     - **Owner**: Your GitHub username/org
     - **Repository**: Your repository name
     - **Workflow**: `publish-release.yml`
     - **Environment**: `pypi`

2. **GitHub Personal Access Token** (for changelog PR creation):
   - Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Click "Generate new token"
   - Configure:
     - **Token name**: `CHANGELOG_AUTOMATION_TOKEN`
     - **Expiration**: 90 days or longer
     - **Repository access**: Only select repositories → Choose your repository
     - **Permissions**: Contents (Read/Write), Pull requests (Read/Write)
   - In repository Settings → Secrets and variables → Actions → New secret
   - Add `CHANGELOG_AUTOMATION_TOKEN` with your token

3. **Configure PyPI environment protection** (for manual approval):
   - Go to repository Settings → Environments
   - Click on `pypi` environment (or create it)
   - Enable "Required reviewers" and add yourself as a reviewer
   - This ensures PyPI releases require manual approval after GitHub Release creation

Release your package by pushing a version tag:

```bash
git tag v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

This triggers: changelog generation → PR creation → (after merge) GitHub release → **manual approval** → PyPI publish.

See the [Contributing Guide](contributing.md) for detailed release process documentation.

### ReadTheDocs (Documentation)

1. Go to [readthedocs.org](https://readthedocs.org/accounts/signup/)
2. Sign in with GitHub
3. Click "Import a Project"
4. Select your repository
5. Click "Build version" - your docs are live!

Documentation builds automatically on every push to main.

## Next Steps

- **[Reference Guide](reference.md)** - Full command reference, CI/CD setup, testing guide
- **[Contributing](contributing.md)** - For template developers
- **[GitHub Template](https://github.com/stateful-y/python-package-copier)** - Source code and issues
