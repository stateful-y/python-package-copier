# Contributing

## Setup

```bash
# Clone the repository
git clone https://github.com/stateful-y/python-package-copier.git
cd python-package-copier

# Install dependencies
uv sync --group test --group docs

# Install pre-commit hooks (optional)
uv run pre-commit install
```

## Test Template Changes

The template repository uses pytest with markers to categorize tests:

- **Fast tests**: Unit tests that validate template generation without running subprocesses
- **Slow tests**: Tests marked with `@pytest.mark.slow` that take longer to execute
- **Integration tests**: Tests marked with `@pytest.mark.integration` that use `copier.run_copy()` to generate actual projects

### Test Commands

Run fast tests only (recommended during development):

=== "just"

    ```bash
    just test-fast
    ```

=== "nox"

    ```bash
    uvx nox -s test_fast
    ```

=== "uv run"

    ```bash
    uv run pytest -m "not slow and not integration" -v
    ```

Run slow and integration tests:

=== "just"

    ```bash
    just test-slow
    ```

=== "nox"

    ```bash
    uvx nox -s test_slow
    ```

=== "uv run"

    ```bash
    uv run pytest -m "slow or integration" -v
    ```

Run all tests:

=== "just"

    ```bash
    just test
    ```

=== "nox"

    ```bash
    uvx nox -s test
    ```

=== "uv run"

    ```bash
    uv run pytest -v
    ```

### When to Mark Tests

Mark your tests appropriately to maintain fast feedback:

- Use `@pytest.mark.slow` for tests that take more than a few seconds
- Use `@pytest.mark.integration` for tests that run `copier.run_copy()` or execute commands in generated projects
- Tests without marks should be fast unit tests that only validate template structure and content

Example:

```python
import pytest

@pytest.mark.integration
@pytest.mark.slow
def test_generated_project_builds(copie):
    """Test that generated project can run nox sessions."""
    result = copie.copy()
    subprocess.run(["uvx", "nox", "-s", "tests"], cwd=result.project_dir, check=True)
```

### CI Test Strategy

The CI pipeline uses a two-tier testing strategy optimized for fast feedback:

1. **Fast tests** (`test-fast` job): Runs on minimum and maximum Python versions (3.11, 3.14) only:
   - **Draft PRs**: Ubuntu only (2 jobs) - Quick feedback in ~2-3 minutes
   - **Ready PRs/Main**: All OS - Ubuntu, Windows, macOS (6 jobs) - Cross-platform validation

2. **Full test suite** (`test-full` job): Runs all tests (fast + slow + integration) on Ubuntu across all Python versions (3.11-3.14) when the PR is not in draft mode or on the main branch (4 jobs).

**Total CI jobs:**
- Draft PRs: 3 jobs (2 test + 1 lint)
- Ready PRs: 11 jobs (6 test-fast + 4 test-full + 1 lint)

### Manual Testing with `just gen`

The `just gen` command generates a temporary project from the template, runs a recipe inside it, and automatically cleans up afterwards. This is the fastest way to verify template changes produce a working project.

```bash
# Build docs in a generated project (with examples, the default)
just gen build

# Run tests in a generated project
just gen test

# Run linters
just gen lint

# Format and fix code
just gen fix

# Generate without examples
just examples=false gen build
just examples=false gen test
```

The generated project is created in `.generated/` and removed automatically via a shell trap, even if the recipe fails.

#### Available recipes

Any recipe from the generated project's justfile can be passed to `just gen`:

| Recipe | Description |
| --- | --- |
| `test` | Run tests and doctests |
| `test-fast` | Fast tests only (no slow/integration) |
| `test-cov` | Tests with coverage report |
| `test-docstrings` | Run docstring examples |
| `lint` | Run ruff, rumdl, and ty |
| `fix` | Auto-format via pre-commit |
| `build` | Build documentation |
| `build-fast` | Build docs without notebook export (with examples only) |
| `serve` | Serve docs locally at localhost:8080 |
| `link` | Check built docs for dead links |
| `all` | Run fix + test |

## Code Quality

Format and fix all issues:

=== "just"

    ```bash
    just fix
    ```

=== "nox"

    ```bash
    uvx nox -s fix
    ```

=== "uv run"

    ```bash
    uv run ruff format src tests
    uv run ruff check src tests --fix
    uv run ty check src
    ```

Check code (fix + test):

=== "just"

    ```bash
    just all
    ```

=== "uv run"

    ```bash
    uvx pre-commit run --all-files && uv run pytest tests/ -n auto -v
    ```

## Documentation

Build documentation:

=== "just"

    ```bash
    just build
    ```

=== "nox"

    ```bash
    uvx nox -s build_docs
    ```

=== "uv run"

    ```bash
    uv run mkdocs build
    ```

Serve documentation at localhost:8080:

=== "just"

    ```bash
    just serve
    ```

=== "nox"

    ```bash
    uvx nox -s serve_docs
    ```

=== "uv run"

    ```bash
    uv run mkdocs serve
    ```

## Modifying the Template

### Edit Template Files

Template files are in the `template/` directory. Files ending with `.jinja` are rendered by Copier with variable substitution.

### Edit Template Configuration

Edit `copier.yml` to add or modify template prompts and variables.

### Test Your Changes

After making changes:

1. Run `just test-fast` to test template generation
2. Run `just gen build` to verify the generated project builds docs
3. Run `just gen test` to verify tests pass in the generated project

## Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/) to automate changelog generation and releases. All commit messages must follow this format:

```text
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Commit Types

- `feat:` - A new feature (triggers minor version bump)
- `fix:` - A bug fix (triggers patch version bump)
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### Breaking Changes

To indicate a breaking change (triggers major version bump):
- Add `!` after the type: `feat!: remove deprecated API`
- Or include `BREAKING CHANGE:` in the footer

### Examples

```bash
feat: add support for Python 3.13
fix(tests): correct test fixture configuration
docs: update quickstart guide
feat!: remove support for Python 3.9
```

The pre-commit hook will validate your commit messages automatically.

## Release Process

Releases are automated via GitHub Actions with a **manual approval gate** before PyPI publishing to ensure quality control.

```mermaid
graph LR
    A[Push Tag<br/>v*.*.*] --> B[changelog.yml]
    B --> C[Generate<br/>CHANGELOG.md]
    B --> D[Build Package<br/>validation]
    C --> E[Create PR]
    E --> F[Review & Merge<br/>PR]
    F --> G[publish-release.yml]
    G --> H[Create GitHub<br/>Release]
    H --> I{Manual<br/>Approval}
    I -->|Approve| J[Publish to PyPI]
    style I fill:#ff9,stroke:#333,stroke-width:2px
    style J fill:#9f9,stroke:#333,stroke-width:2px
```

### Initial Setup (One-time)

Before you can create releases, you need to configure two things:

#### 1. Create a Personal Access Token for Changelog Automation

1. **Create a Fine-grained Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Click "Generate new token"
   - Configure:
     - **Token name**: `CHANGELOG_AUTOMATION_TOKEN`
     - **Expiration**: 90 days or longer
     - **Repository access**: Only select repositories → Choose this repository
     - **Permissions**:
       - Contents: Read and write
       - Pull requests: Read and write

2. **Add token as repository secret**:
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CHANGELOG_AUTOMATION_TOKEN`
   - Value: Paste your generated token

#### 2. Configure PyPI Environment with Required Reviewers

To enable the manual approval gate before PyPI publishing:

1. **Set up Trusted Publishing on PyPI** (if not already done):
   - Go to your PyPI project → Manage → Publishing
   - Add a new publisher with:
     - **Owner**: stateful-y
     - **Repository**: python-package-copier
     - **Workflow**: `publish-release.yml`
     - **Environment**: `pypi`

2. **Configure environment protection in GitHub**:
   - Go to repository Settings → Environments
   - Click on the `pypi` environment (or create it if it doesn't exist)
   - Enable "Required reviewers"
   - Add maintainers as required reviewers
   - Optionally set a wait timer for additional safety

This ensures that no package is published to PyPI without explicit approval from a maintainer.

### Creating a Release

1. **Ensure all changes follow conventional commits** - The changelog is auto-generated from commit messages

2. **Create and push a version tag**:
   ```bash
   git tag v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

3. **Automated changelog workflow** (`changelog.yml`):
   - Generates the changelog using [git-cliff](https://git-cliff.org/)
   - Creates a **Pull Request** with the updated `CHANGELOG.md`
   - Builds the package distributions (wheels and sdist) for **immediate validation**
   - Stores distributions as workflow artifacts (reused later to avoid rebuilding)

4. **Review and merge the changelog PR**:
   - Review the generated changelog
   - Merge the PR to update the main branch
   - The PR is automatically labeled with `changelog` and `automated`

5. **Automated release workflow** (`publish-release.yml`):
   - Creates a GitHub Release with auto-generated release notes
   - Attaches distribution files to the release
   - **Waits for manual approval** before proceeding to PyPI

6. **Manual approval for PyPI publishing**:
   - Designated reviewers receive a notification
   - Review the GitHub Release to verify everything is correct
   - Approve the deployment to publish to PyPI
   - Package is published using Trusted Publishing (OIDC, no tokens needed)

### Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features (backward compatible)
- **PATCH** (0.0.1): Bug fixes

The version is tracked via Git tags and managed by `hatch-vcs`.

### What Gets Into the Changelog

Based on your commit types:
- `feat:` → **Added** section
- `fix:` → **Fixed** section
- `docs:` → **Documentation** section
- `perf:` → **Performance** section
- `refactor:` → **Refactored** section
- `style:` → **Styling** section
- `test:` → **Testing** section
- `chore:` → **Miscellaneous** section

Commits that don't follow conventional format are excluded from the changelog.
