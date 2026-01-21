# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.2.0] - 2026-01-21

This **minor release** includes 13 commits.


### Features
- Automate release notes with git-cliff and commitizen  ([#6](https://github.com/gtauzin/python-package-copier-template/pull/6)) by @gtauzin
- Align template repo tooling with generated projects  ([#7](https://github.com/gtauzin/python-package-copier-template/pull/7)) by @gtauzin
- Enrich CHANGELOG generation with metadata and fix lint issues  ([#21](https://github.com/gtauzin/python-package-copier-template/pull/21)) by @gtauzin

### Bug Fixes
- Remove non-functional include_docker prompt  ([#5](https://github.com/gtauzin/python-package-copier-template/pull/5)) by @gtauzin
- Use PR instead of direct push for CHANGELOG updates  ([#8](https://github.com/gtauzin/python-package-copier-template/pull/8)) by @gtauzin
- Add base branch to PR creation for detached HEAD state  ([#9](https://github.com/gtauzin/python-package-copier-template/pull/9)) by @gtauzin
- Use PAT token for release workflow PR creation  ([#10](https://github.com/gtauzin/python-package-copier-template/pull/10)) by @gtauzin
- Use RELEASE_AUTOMATION_TOKEN for release workflow PR creation  ([#11](https://github.com/gtauzin/python-package-copier-template/pull/11)) by @gtauzin
- Create GitHub Release after changelog PR is merged  ([#13](https://github.com/gtauzin/python-package-copier-template/pull/13)) by @gtauzin
- Ensure changelog PR commits are signed and pass lint checks  ([#15](https://github.com/gtauzin/python-package-copier-template/pull/15)) by @gtauzin
- Ensure changelog PRs include pre-commit formatting changes  ([#17](https://github.com/gtauzin/python-package-copier-template/pull/17)) by @gtauzin
- Remove trailing spaces from git-cliff generated CHANGELOG  ([#19](https://github.com/gtauzin/python-package-copier-template/pull/19)) by @gtauzin
- Use --latest flag and add pre-commit validation to changelog workflow  ([#23](https://github.com/gtauzin/python-package-copier-template/pull/23)) by @gtauzin

### New Contributors

Thanks to all contributors for this release:
- @gtauzin
## [Unreleased]

### Added
- Automated release notes generation with git-cliff
- Conventional commit enforcement with commitizen
- Automatic CHANGELOG.md updates on release
- GitHub Release creation with generated notes

### Removed
- Removed non-functional `include_docker` prompt that had no implementation

## [0.1.0] - 2026-01-20

### Added
- Modern Python package template using Copier
- Type checking with ty
- Fast dependency management with uv
- Linting and formatting with ruff
- Testing with pytest and nox
- Documentation with MkDocs Material theme
- GitHub Actions CI/CD workflows
- Pre-commit hooks configuration
- Task automation with justfile
- Comprehensive test suite for template validation
- ReadTheDocs integration
- Multiple license options (MIT, Apache-2.0, BSD-3-Clause, GPL-3.0, Proprietary)
- Example code and tests
- Full documentation structure
