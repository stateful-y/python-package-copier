# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.9.1] - 2026-02-07

This **patch release** includes 3 commits.


### Bug Fixes
- Remove pre-build dependency from serve commands and fix hooks indentation by @gtauzin
- Example link in docs by @gtauzin
- Use relative path for standalone notebook link in examples.md by @gtauzin

### Contributors

Thanks to all contributors for this release:
- @gtauzin

## [0.8.0] - 2026-02-05

This **minor release** includes 3 commits.


### Features
- Add pytest-based parallel example testing with lint command  ([#65](https://github.com/stateful-y/python-package-copier/pull/65)) by @gtauzin

### Bug Fixes
- Template configuration and documentation improvements  ([#64](https://github.com/stateful-y/python-package-copier/pull/64)) by @gtauzin

### Refactoring
- Simplify justfile commands to use uv directly  ([#66](https://github.com/stateful-y/python-package-copier/pull/66)) by @gtauzin

### Contributors

Thanks to all contributors for this release:
- @gtauzin

## [0.7.3] - 2026-02-04

This **patch release** includes 1 commit.


### Miscellaneous Tasks
- Improve template configuration and documentation  ([#62](https://github.com/stateful-y/python-package-copier/pull/62)) by @gtauzin

### Contributors

Thanks to all contributors for this release:
- @gtauzin

## [0.7.2] - 2026-02-04

This **patch release** includes 1 commit.


### Bug Fixes
- Re-enable markdown copying from standalone script to mkdocs hook  ([#60](https://github.com/stateful-y/python-package-copier/pull/60)) by @gtauzin

### Contributors

Thanks to all contributors for this release:
- @gtauzin

## [0.7.1] - 2026-02-04

This **patch release** includes 1 commit.


### Documentation
- Align command documentation with tab syntax  ([#58](https://github.com/stateful-y/python-package-copier/pull/58)) by @gtauzin

### Contributors

Thanks to all contributors for this release:
- @gtauzin

## [0.7.0] - 2026-02-04

This **minor release** includes 7 commits.


### Features
- Add manual approval gate for PyPI releases  ([#54](https://github.com/stateful-y/python-package-copier/pull/54)) by @gtauzin

### Bug Fixes
- Store all copier answers and add max_python_version parameter  ([#50](https://github.com/stateful-y/python-package-copier/pull/50)) by @gtauzin
- Update repos name and add site_url to mkdocs.yml for ReadTheDocs  ([#52](https://github.com/stateful-y/python-package-copier/pull/52)) by @gtauzin
- Change RTD build job from build to post_build stage  ([#53](https://github.com/stateful-y/python-package-copier/pull/53)) by @gtauzin
- Add explicit UTF-8 encoding to all test file reads for Windows compatibility  ([#56](https://github.com/stateful-y/python-package-copier/pull/56)) by @gtauzin

### Documentation
- Improve template documentation with complete variable list and release workflow  ([#51](https://github.com/stateful-y/python-package-copier/pull/51)) by @gtauzin

### Miscellaneous Tasks
- Standardize test command naming across nox, justfile, and CI  ([#55](https://github.com/stateful-y/python-package-copier/pull/55)) by @gtauzin

`### Contributors

Thanks to all contributors for this release:
- @gtauzin
`
## [0.6.0] - 2026-02-03

This **minor release** includes 4 commits.


### Features
- Include logos across docs and README  ([#44](https://github.com/stateful-y/python-package-copier/pull/44)) by @gtauzin
- Transform template docs to a user-focused structure  ([#46](https://github.com/stateful-y/python-package-copier/pull/46)) by @gtauzin

### Documentation
- Update documentation assets and add README  ([#48](https://github.com/stateful-y/python-package-copier/pull/48)) by @gtauzin

### Refactoring
- Restructure test suite and improve marimo/MkDocs integration  ([#45](https://github.com/stateful-y/python-package-copier/pull/45)) by @gtauzin

### Contributors

Thanks to all contributors for this release:
- @gtauzin

## [0.5.0] - 2026-01-28

This **minor release** includes 3 commits.


### Features
- Make just install pre-commit by @gtauzin

### Bug Fixes
- Transfer repos ownership to stateful-y by @gtauzin
- Make just install point to dev group by @gtauzin

### Contributors

Thanks to all contributors for this release:
- @gtauzin

## [0.4.0] - 2026-01-28

This **minor release** includes 4 commits.


### Features
- Add docstring testing support and restructure documentation  ([#37](https://github.com/gtauzin/python-package-copier/pull/37)) by @gtauzin
- Add optional marimo notebook examples  ([#38](https://github.com/gtauzin/python-package-copier/pull/38)) by @gtauzin

### Bug Fixes
- Improve release notes extraction from CHANGELOG.md  ([#35](https://github.com/gtauzin/python-package-copier/pull/35)) by @gtauzin
- Correct copier source path and add update documentation  ([#36](https://github.com/gtauzin/python-package-copier/pull/36)) by @gtauzin

### Refactoring
- Rename `include_github_actions` into `include_actions` and `python_version` into `min_python_version`  ([#38](https://github.com/gtauzin/python-package-copier/pull/38)) by @gtauzin

### Contributors

Thanks to all contributors for this release:
- @gtauzin

## [0.3.0] - 2026-01-22

This **minor release** includes 7 commits.


### Features
- Add dependency groups for dev, checks, and examples  ([#28](https://github.com/gtauzin/python-package-copier/pull/28)) by @gtauzin
- Add PR title validation and improve git-cliff configuration  ([#33](https://github.com/gtauzin/python-package-copier/pull/33)) by @gtauzin

### Bug Fixes
- Extract release notes from merged CHANGELOG.md instead of regenerating  ([#25](https://github.com/gtauzin/python-package-copier/pull/25)) by @gtauzin
- Remove license classifier from template  ([#26](https://github.com/gtauzin/python-package-copier/pull/26)) by @gtauzin
- Update lint command to check types correctly  ([#27](https://github.com/gtauzin/python-package-copier/pull/27)) by @gtauzin
- Exclude _version.py from ruff and coverage reports  ([#29](https://github.com/gtauzin/python-package-copier/pull/29)) by @gtauzi

### Documentation
- Document automated release workflow with git-cliff and changelog PR  ([#30](https://github.com/gtauzin/python-package-copier/pull/30)) by @gtauzin

### Contributors

Thanks to all contributors for this release:
- @gtauzin

## [0.2.0] - 2026-01-21

This **minor release** includes 13 commits.


### Features
- Automate release notes with git-cliff and commitizen  ([#6](https://github.com/gtauzin/python-package-copier/pull/6)) by @gtauzin
- Align template repo tooling with generated projects  ([#7](https://github.com/gtauzin/python-package-copier/pull/7)) by @gtauzin
- Enrich CHANGELOG generation with metadata and fix lint issues  ([#21](https://github.com/gtauzin/python-package-copier/pull/21)) by @gtauzin

### Bug Fixes
- Remove non-functional include_docker prompt  ([#5](https://github.com/gtauzin/python-package-copier/pull/5)) by @gtauzin
- Use PR instead of direct push for CHANGELOG updates  ([#8](https://github.com/gtauzin/python-package-copier/pull/8), [#9](https://github.com/gtauzin/python-package-copier/pull/9), [#10](https://github.com/gtauzin/python-package-copier/pull/10), [#11](https://github.com/gtauzin/python-package-copier/pull/11)) by @gtauzin
- Create GitHub Release after changelog PR is merged  ([#13](https://github.com/gtauzin/python-package-copier/pull/13), [#15](https://github.com/gtauzin/python-package-copier/pull/15), [#17](https://github.com/gtauzin/python-package-copier/pull/17), [#19](https://github.com/gtauzin/python-package-copier/pull/19), [#23](https://github.com/gtauzin/python-package-copier/pull/23)) by @gtauzin

### Contributors

Thanks to all contributors for this release:
- @gtauzin

## [0.1.0] - 2026-01-20

This **minor release** includes 1 commit.

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

### Contributors

Thanks to all contributors for this release:
- @gtauzin
