# How to Set Up CI/CD Services

This guide walks you through configuring the external services that power your generated project's CI/CD pipeline. Complete these steps after pushing your project to GitHub.

## Prerequisites

- A project generated with `include_actions=true` (the default)
- The project pushed to a GitHub repository

## Codecov (Coverage Reporting)

Codecov aggregates test coverage reports from CI runs.

1. Sign up at [codecov.io](https://codecov.io/) with your GitHub account
2. Add your repository from the Codecov dashboard
3. Go to **Settings** and copy the upload token
4. In your GitHub repository: **Settings → Secrets and variables → Actions → New repository secret**
5. Add `CODECOV_TOKEN` with your token value

This token is used by `tests.yml` (on every push/PR) and `nightly.yml` (daily testing).

## PyPI Publishing (Automated Releases)

The release pipeline uses **Trusted Publishing** (OIDC) - no API tokens are stored in your repository.

### 1. Configure Trusted Publishing on PyPI

1. Create an account at [pypi.org](https://pypi.org/account/register/)
2. Publish your first release manually, or create the project on PyPI
3. Go to your project → **Manage → Publishing**
4. Add a new publisher:
   - **Owner**: Your GitHub username/organization
   - **Repository**: Your repository name
   - **Workflow**: `publish-release.yml`
   - **Environment**: `pypi`

### 2. Create a Personal Access Token for Changelog Automation

The changelog workflow needs a token to create PRs:

1. Go to **GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Click **Generate new token** and configure:
   - **Token name**: `CHANGELOG_AUTOMATION_TOKEN`
   - **Expiration**: 90 days or longer
   - **Repository access**: Only select repositories → choose your repository
   - **Permissions**: Contents (Read/Write), Pull requests (Read/Write)
3. In your repository: **Settings → Secrets and variables → Actions → New repository secret**
4. Add `CHANGELOG_AUTOMATION_TOKEN` with the token value

### 3. Configure the PyPI Environment for Manual Approval

This ensures releases require explicit maintainer approval before publishing:

1. Go to repository **Settings → Environments**
2. Create or select the `pypi` environment
3. Enable **Required reviewers** under *Deployment protection rules*
4. Add one or more maintainers as required reviewers
5. (Optional) Enable a **Wait timer** for additional safety

!!! note
    Environment protection rules require **public repositories** or **GitHub Pro/Team/Enterprise** plans.

### Verify the Release Pipeline

Push a version tag to trigger the full flow:

```bash
git tag v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

This triggers: changelog generation → PR creation → (after merge) GitHub Release → **manual approval** → PyPI publish.

See [GitHub Workflows](../reference/github-workflows.md) for the full workflow reference and [About the Release Process](../explanation/release-process.md) for design rationale.

## ReadTheDocs (Documentation)

1. Sign up at [readthedocs.org](https://readthedocs.org/accounts/signup/) with GitHub
2. Click **Import a Project**
3. Select your repository
4. Click **Build version** - your docs are live

Documentation builds automatically on every push to main. The generated `.readthedocs.yml` handles all build configuration.

## Summary

| Service | Secret/Config | Used By |
|---------|--------------|---------|
| Codecov | `CODECOV_TOKEN` secret | tests.yml, nightly.yml |
| PyPI | Trusted Publishing (no secret) | publish-release.yml |
| Changelog | `CHANGELOG_AUTOMATION_TOKEN` secret | changelog.yml |
| Manual approval | `pypi` environment with reviewers | publish-release.yml |
| ReadTheDocs | Repository import (no secret) | Automatic on push |
