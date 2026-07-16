"""Tests for the copier template."""

import os
import posixpath
import re
import shutil
import subprocess

import pytest


def test_template_creates_project(copie_session_default):
    """Test that the template creates a valid project."""
    expected_files = [
        ".gitignore",
        "README.md",
        "pyproject.toml",
        "noxfile.py",
        "mkdocs.yml",
        ".pre-commit-config.yaml",
        "CODE_OF_CONDUCT.md",
    ]
    expected_dirs = [
        "src",
        "src/test_project",
        "docs",
        "tests",
        ".github",
        ".github/workflows",
        "examples",
    ]

    result = copie_session_default

    assert result.exit_code == 0, result.exception
    assert result.exception is None
    assert result.project_dir.is_dir()

    for path in expected_files:
        assert (result.project_dir / path).is_file(), f"Missing file: {path}"

    for path in expected_dirs:
        assert (result.project_dir / path).is_dir(), f"Missing directory: {path}"

    # git-cliff config should be included with GitHub Actions
    assert (result.project_dir / ".git-cliff.toml").is_file()


def test_readthedocs_config_included(copie_session_default):
    """Test that ReadTheDocs config is always included."""
    result = copie_session_default

    assert result.exit_code == 0, result.exception
    assert result.exception is None
    assert (result.project_dir / ".readthedocs.yml").is_file()


def test_gitignore_includes_examples_when_enabled(copie):
    """Test that .gitignore includes examples section when include_examples is true."""
    result = copie.copy(extra_answers={"include_examples": True})

    gitignore = result.project_dir / ".gitignore"
    assert gitignore.is_file()

    content = gitignore.read_text(encoding="utf-8")

    # Should have documentation examples section
    assert "# Documentation examples" in content
    assert "docs/examples/*/" in content


def test_gitignore_excludes_examples_when_disabled(copie):
    """Test that .gitignore excludes examples section when include_examples is false."""
    result = copie.copy(extra_answers={"include_examples": False})

    gitignore = result.project_dir / ".gitignore"
    assert gitignore.is_file()

    content = gitignore.read_text(encoding="utf-8")

    # Should NOT have documentation examples section
    assert "# Documentation examples" not in content
    assert "docs/examples/*/" not in content


def test_gitignore_includes_worktrees(copie_session_default):
    """Test that .gitignore includes .worktrees/ entry."""
    result = copie_session_default

    content = (result.project_dir / ".gitignore").read_text(encoding="utf-8")

    assert "# Worktrees" in content
    assert ".worktrees/" in content


def test_gitignore_uses_project_name_for_version_file(copie):
    """Test that .gitignore uses project_name variable (not project_slug) for the version file path."""
    result = copie.copy(extra_answers={"package_name": "my_package", "project_slug": "my-project"})

    gitignore = result.project_dir / ".gitignore"
    assert gitignore.is_file()

    content = gitignore.read_text(encoding="utf-8")

    # Should use package_name in the version file path
    assert "src/my_package/_version.py" in content
    # Should NOT use project_slug
    assert "src/my-project/_version.py" not in content


def test_generated_project_structure(copie_session_default):
    """Test that the generated project has the correct structure."""
    result = copie_session_default

    # Check source files
    src_dir = result.project_dir / "src" / "test_project"
    assert (src_dir / "__init__.py").is_file()
    assert (src_dir / "hello.py").is_file()
    assert (src_dir / "py.typed").is_file()

    # Check test files
    tests_dir = result.project_dir / "tests"
    assert (tests_dir / "conftest.py").is_file()
    assert (tests_dir / "test_hello.py").is_file()

    # Check docs
    docs_dir = result.project_dir / "docs"
    assert (docs_dir / "index.md").is_file()
    assert (docs_dir / "pages" / "how-to" / "contribute.md").is_file()

    # Check GitHub workflows
    workflows_dir = result.project_dir / ".github" / "workflows"
    assert (workflows_dir / "tests.yml").is_file()
    assert (workflows_dir / "changelog.yml").is_file()
    assert (workflows_dir / "publish-release.yml").is_file()
    assert (workflows_dir / "nightly.yml").is_file()


def test_generated_pyproject_uses_correct_tools(copie_session_default):
    """Test that the generated pyproject.toml uses the correct tools."""
    result = copie_session_default

    pyproject_path = result.project_dir / "pyproject.toml"
    assert pyproject_path.is_file()

    content = pyproject_path.read_text(encoding="utf-8")

    # Check for required tools in dependency groups
    assert "ty" in content, "ty not found in pyproject.toml"
    assert "ruff" in content, "ruff not found in pyproject.toml"
    assert "pytest" in content, "pytest not found in pyproject.toml"
    assert "mkdocs" in content, "mkdocs not found in pyproject.toml"
    assert "pre-commit-uv" in content, "pre-commit-uv not found in pyproject.toml"

    # Check for dependency groups structure
    assert "[dependency-groups]" in content, "dependency-groups not found in pyproject.toml"
    assert "tests" in content, "tests dependency group not found"
    assert "lint" in content, "lint dependency group not found"
    assert "docs" in content, "docs dependency group not found"
    assert "fix" in content, "fix dependency group not found"
    assert "examples" in content, "examples dependency group not found"
    assert "dev" in content, "dev dependency group not found"

    # nox should NOT be a dependency in pyproject.toml - it's installed globally via uvx
    # (note: .nox may appear in tool config exclude lists, which is fine)
    assert '"nox' not in content and "'nox" not in content, (
        "nox should not be a dependency in pyproject.toml (install globally with uvx)"
    )


def test_pyproject_has_interrogate_config(copie_session_default):
    """Test that pyproject.toml includes interrogate configuration."""
    result = copie_session_default

    pyproject_path = result.project_dir / "pyproject.toml"
    assert pyproject_path.is_file()

    content = pyproject_path.read_text(encoding="utf-8")

    # Should have interrogate configuration section
    assert "[tool.interrogate]" in content
    assert "ignore-init-method = true" in content
    assert "fail-under = 75" in content
    assert '"setup.py", "docs", "build", "tests", "*_version.py"' in content


def test_pyproject_ruff_ignores_docs_directory(copie):
    """Test that pyproject.toml configures ruff to ignore prints and unused args in docs/."""
    result = copie.copy()

    pyproject_path = result.project_dir / "pyproject.toml"
    assert pyproject_path.is_file()

    content = pyproject_path.read_text(encoding="utf-8")

    # Should have per-file-ignores section with docs/** configuration
    assert "[tool.ruff.lint.per-file-ignores]" in content
    # Should ignore prints (T201) and unused args (ARG001) in docs
    assert '"docs/**/*"' in content
    assert "T201" in content  # Print statement
    assert "ARG001" in content  # Unused function argument


def test_generated_project_has_correct_license(copie):
    """Test that the generated project has the correct license."""
    result = copie.copy(
        extra_answers={
            "license": "MIT",
        },
    )

    license_path = result.project_dir / "LICENSE"
    assert license_path.is_file()

    content = license_path.read_text(encoding="utf-8")
    assert "MIT" in content


def test_noxfile_configuration(copie_session_default):
    """Test that noxfile is properly configured."""
    result = copie_session_default

    noxfile_path = result.project_dir / "noxfile.py"
    assert noxfile_path.is_file()

    content = noxfile_path.read_text(encoding="utf-8")

    # Check for uv backend
    assert 'default_venv_backend = "uv|virtualenv"' in content

    # Check for ty
    assert "ty" in content, "ty not found in noxfile.py"


def test_noxfile_test_coverage_uses_pytest_cov(copie_session_default):
    """Test that test_coverage session uses pytest-cov instead of manual coverage."""
    result = copie_session_default

    content = (result.project_dir / "noxfile.py").read_text(encoding="utf-8")

    # Should use pytest directly (pytest-cov handles coverage via addopts)
    assert "pytest-cov" in content or "pytest" in content

    # Should NOT use manual coverage commands
    assert 'session.env["COVERAGE_FILE"]' not in content
    assert 'session.env["COVERAGE_PROCESS_START"]' not in content
    assert '"coverage", "erase"' not in content
    assert '"coverage", "run"' not in content
    assert '"coverage", "html"' not in content
    assert '"coverage", "xml"' not in content


def test_precommit_configuration(copie_session_default):
    """Test that pre-commit config is properly set up."""
    result = copie_session_default

    precommit_path = result.project_dir / ".pre-commit-config.yaml"
    assert precommit_path.is_file()

    content = precommit_path.read_text(encoding="utf-8")

    # Check for ruff
    assert "ruff-pre-commit" in content or "ruff" in content

    # Check for ty
    assert "ty" in content, "ty not found in pre-commit config"

    # Check for commitizen
    assert "commitizen" in content, "commitizen not found in pre-commit config"


def test_precommit_interrogate_checks_only_src(copie_session_default):
    """Test that interrogate pre-commit hook only checks src/ directory."""
    result = copie_session_default

    precommit_path = result.project_dir / ".pre-commit-config.yaml"
    assert precommit_path.is_file()

    content = precommit_path.read_text(encoding="utf-8")

    # Should have interrogate configured to check only src/
    assert "interrogate" in content
    assert "files: ^src/" in content
    assert r"exclude: .*_version\.py$" in content


def test_precommit_ty_uses_uv_run(copie_session_default):
    """Test that ty pre-commit hook uses uv run with proper configuration."""
    result = copie_session_default

    precommit_path = result.project_dir / ".pre-commit-config.yaml"
    assert precommit_path.is_file()

    content = precommit_path.read_text(encoding="utf-8")

    # Should have ty configured with uv run, pinned to uv.lock via --locked
    assert "id: ty" in content
    assert "entry: uv run --locked ty check src" in content
    assert "pass_filenames: false" in content


def test_precommit_linters_are_pinned_by_uv_lock(copie_session_default):
    """Test that version-sensitive linters resolve from uv.lock, not a pre-commit rev.

    uv.lock is the single source of truth for these tools, so each must run through
    `uv run --locked`. A pinned `rev:` here would let pre-commit drift from CI.
    """
    result = copie_session_default

    content = (result.project_dir / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    for tool in ("interrogate", "ruff", "ruff format", "rumdl", "ty"):
        assert f"entry: uv run --locked {tool}" in content, f"{tool} does not resolve from uv.lock"

    # The upstream mirrors these hooks used to come from would reintroduce a second
    # version source alongside uv.lock.
    for mirror in ("ruff-pre-commit", "rumdl-pre-commit", "econchick/interrogate"):
        assert mirror not in content, f"{mirror} reintroduces a version source outside uv.lock"


def test_github_workflows(copie_session_default):
    """Test that GitHub workflows are properly configured."""
    result = copie_session_default

    tests_workflow = result.project_dir / ".github" / "workflows" / "tests.yml"
    assert tests_workflow.is_file()

    content = tests_workflow.read_text(encoding="utf-8")

    # Check for uv usage
    assert "astral-sh/setup-uv" in content

    # Check for ty
    assert "ty" in content, "ty not found in tests workflow"

    # Check for test_docstrings job
    assert "test_docstrings:" in content, "test_docstrings job not found in tests workflow"
    assert "nox -s test_docstrings" in content, "test_docstrings nox session not run in CI"

    # Check for test-compat job
    assert "test-compat:" in content, "test-compat job not found in tests workflow"
    assert "nox -s test_compat" in content, "test_compat nox session not run in CI"

    # Check PR title validation workflow
    pr_title_workflow = result.project_dir / ".github" / "workflows" / "pr-title.yml"
    assert pr_title_workflow.is_file(), "PR title validation workflow not found"

    pr_title_content = pr_title_workflow.read_text(encoding="utf-8")
    assert "amannn/action-semantic-pull-request" in pr_title_content
    assert "feat" in pr_title_content
    assert "fix" in pr_title_content
    assert "docs" in pr_title_content


def test_release_workflow(copie_session_default):
    """Test that release workflow includes changelog automation."""
    result = copie_session_default

    # Check changelog.yml workflow
    changelog_workflow = result.project_dir / ".github" / "workflows" / "changelog.yml"
    assert changelog_workflow.is_file()

    changelog_content = changelog_workflow.read_text(encoding="utf-8")

    # Check for git-cliff
    assert "git-cliff" in changelog_content, "git-cliff not found in changelog workflow"

    # Check for changelog job
    assert "changelog" in changelog_content.lower(), "changelog job not found in changelog workflow"

    # Check publish-release.yml workflow
    release_workflow = result.project_dir / ".github" / "workflows" / "publish-release.yml"
    assert release_workflow.is_file()

    release_content = release_workflow.read_text(encoding="utf-8")

    # Check for GitHub release creation
    assert "gh release create" in release_content or "github-release" in release_content.lower(), (
        "GitHub release creation not found"
    )


def test_commitizen_configuration(copie_session_default):
    """Test that commitizen is properly configured."""
    result = copie_session_default

    pyproject_path = result.project_dir / "pyproject.toml"
    assert pyproject_path.is_file()

    content = pyproject_path.read_text(encoding="utf-8")

    # Check for commitizen configuration
    assert "[tool.commitizen]" in content, "commitizen config not found in pyproject.toml"
    assert "cz_conventional_commits" in content, "conventional commits not configured"


def test_git_cliff_configuration(copie_session_default):
    """Test that git-cliff configuration exists."""
    result = copie_session_default

    cliff_config = result.project_dir / ".git-cliff.toml"
    assert cliff_config.is_file()

    content = cliff_config.read_text(encoding="utf-8")

    # Check for conventional commits
    assert "conventional_commits" in content, "conventional commits not enabled in git-cliff"

    # Check for Keep a Changelog format
    assert "Keep a Changelog" in content, "Keep a Changelog format not mentioned"

    # Check that chore(release) commits are skipped
    assert 'message = "^chore\\\\(release\\\\)", skip = true' in content, (
        "chore(release) commits should be skipped in changelog"
    )


def test_different_licenses(copie):
    """Test that different licenses can be selected."""
    licenses = ["MIT", "Apache-2.0", "BSD-3-Clause", "GPL-3.0"]

    for license_name in licenses:
        result = copie.copy(
            extra_answers={
                "license": license_name,
                "project_slug": f"test-{license_name.lower()}",
            },
        )

        assert result.exit_code == 0
        assert result.project_dir.is_dir()

        # Check that LICENSE file exists
        license_path = result.project_dir / "LICENSE"
        assert license_path.is_file()


def test_doctest_configuration(copie):
    """Test that doctest configuration is properly set up."""
    result = copie.copy()

    assert result.exit_code == 0
    assert result.project_dir.is_dir()

    # Check noxfile has test_docstrings session with doctest flags
    noxfile_content = (result.project_dir / "noxfile.py").read_text(encoding="utf-8")
    assert "def test_docstrings(session:" in noxfile_content
    assert '"--doctest-modules"' in noxfile_content

    # Check justfile has test-docstrings command
    justfile_content = (result.project_dir / "justfile").read_text(encoding="utf-8")
    assert "test-docstrings:" in justfile_content
    assert "--doctest-modules" in justfile_content

    # Check hello.py has docstring examples
    hello_py = (result.project_dir / "src" / "test_project" / "hello.py").read_text(encoding="utf-8")
    assert "Examples" in hello_py
    assert ">>>" in hello_py


def test_examples_directory_when_enabled(copie):
    """Test that examples directory is created when include_examples=True."""
    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )

    assert result.exit_code == 0
    examples_dir = result.project_dir / "examples"
    assert examples_dir.is_dir(), "examples/ directory not created"

    # Check for notebook file
    hello_notebook = examples_dir / "hello.py"
    assert hello_notebook.is_file(), "examples/hello.py not created"

    # Check notebook content
    notebook_content = hello_notebook.read_text(encoding="utf-8")
    assert "import marimo" in notebook_content
    assert "app = marimo.App" in notebook_content
    assert "plotly" in notebook_content
    assert "num_points" in notebook_content

    # Check marimo in dependencies and pytest marker for examples
    pyproject_content = (result.project_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert "marimo" in pyproject_content
    assert "plotly" in pyproject_content
    assert "example: marks tests for example notebooks" in pyproject_content

    # Check noxfile has test_examples session that uses pytest
    noxfile_content = (result.project_dir / "noxfile.py").read_text(encoding="utf-8")
    assert "def test_examples(session:" in noxfile_content
    assert "pytest" in noxfile_content
    assert '"tests"' in noxfile_content
    assert '"-m"' in noxfile_content and '"example"' in noxfile_content
    assert '"-n"' in noxfile_content and '"auto"' in noxfile_content

    # Check test_examples.py is created and uses pytest parametrize
    test_examples_file = result.project_dir / "tests" / "test_examples.py"
    assert test_examples_file.is_file(), "tests/test_examples.py not created"
    test_examples_content = test_examples_file.read_text(encoding="utf-8")
    assert "pytest.mark.parametrize" in test_examples_content
    assert "pytest.mark.example" in test_examples_content
    assert "EXAMPLES_DIR.glob" in test_examples_content
    assert "subprocess.run" in test_examples_content
    assert '["python", str(notebook_file)]' in test_examples_content
    assert "https://docs.marimo.io/getting_started/quickstart/#run-as-scripts" in test_examples_content

    # Check docs/examples/ directory exists for exports
    docs_examples_dir = result.project_dir / "docs" / "examples"
    assert docs_examples_dir.is_dir(), "docs/examples/ directory not created"

    # Check justfile has example command and test-examples command
    justfile_content = (result.project_dir / "justfile").read_text(encoding="utf-8")
    assert "example file=" in justfile_content
    assert "marimo edit" in justfile_content
    assert "test-examples:" in justfile_content
    assert "pytest tests" in justfile_content
    assert "-m example" in justfile_content
    assert "-n auto" in justfile_content

    # Check examples.md exists and uses gallery placeholder
    examples_md = result.project_dir / "docs" / "pages" / "tutorials" / "examples.md"
    assert examples_md.is_file(), "docs/pages/tutorials/examples.md not created"
    examples_content = examples_md.read_text(encoding="utf-8")
    assert "<!-- GALLERY -->" in examples_content
    assert "## Running Examples Locally" in examples_content

    # Check mkdocs.yml includes examples in nav and has exclude_docs
    mkdocs_content = (result.project_dir / "mkdocs.yml").read_text(encoding="utf-8")
    assert "Examples: pages/tutorials/examples.md" in mkdocs_content
    # Check for exclude_docs with CLAUDE.md files
    assert "exclude_docs:" in mkdocs_content
    assert "examples/**/CLAUDE.md" in mkdocs_content

    # Check GitHub workflow includes examples job
    tests_workflow = result.project_dir / ".github" / "workflows" / "tests.yml"
    workflow_content = tests_workflow.read_text(encoding="utf-8")
    assert "examples:" in workflow_content
    assert "nox -s test_examples" in workflow_content

    # Check README mentions examples (in "Where can I learn more?" section)
    readme_content = (result.project_dir / "README.md").read_text(encoding="utf-8")
    assert "Interactive Examples:" in readme_content or "examples/" in readme_content
    assert "marimo edit examples/hello.py" in readme_content

    # Check CONTRIBUTING mentions adding examples with new pytest approach
    contributing_content = (result.project_dir / "docs" / "pages" / "how-to" / "contribute.md").read_text(
        encoding="utf-8"
    )
    assert "### Adding Examples" in contributing_content
    assert "test_examples" in contributing_content or "test-examples" in contributing_content


def test_examples_directory_when_disabled(copie):
    """Test that examples directory is NOT created when include_examples=False."""
    result = copie.copy(
        extra_answers={
            "include_examples": False,
        },
    )

    assert result.exit_code == 0

    # Examples directory should not exist or be empty when disabled
    examples_dir = result.project_dir / "examples"
    assert not examples_dir.is_dir(), "examples/ directory created"

    # Marimo should not be in examples dependencies
    pyproject_content = (result.project_dir / "pyproject.toml").read_text(encoding="utf-8")
    # examples group should not exist or be empty
    assert (
        "examples = [" not in pyproject_content
        or "examples = []" in pyproject_content
        or "examples = [\n]" in pyproject_content
    )
    # marimo should not be in dependencies
    assert "marimo" not in pyproject_content
    assert "plotly" not in pyproject_content

    # Check noxfile doesn't have test_examples session
    noxfile_content = (result.project_dir / "noxfile.py").read_text(encoding="utf-8")
    assert "def test_examples(session:" not in noxfile_content

    # Check justfile doesn't have example command
    justfile_content = (result.project_dir / "justfile").read_text(encoding="utf-8")
    # Should not have the example command, but might have other content
    lines = justfile_content.split("\n")
    example_command_lines = [line for line in lines if line.strip().startswith("example:")]
    assert len(example_command_lines) == 0, "example command should not exist"

    # Check examples.md doesn't exist or is empty
    examples_md = result.project_dir / "docs" / "pages" / "tutorials" / "examples.md"
    if examples_md.exists():
        content = examples_md.read_text(encoding="utf-8").strip()
        assert content == "", (
            f"docs/pages/tutorials/examples.md should be empty when examples are disabled, but contains: {content[:100]}"
        )

    # Check mkdocs.yml doesn't include examples in nav
    mkdocs_content = (result.project_dir / "mkdocs.yml").read_text(encoding="utf-8")
    assert "Examples: tutorials/examples.md" not in mkdocs_content

    # Check GitHub workflow doesn't include examples job
    tests_workflow = result.project_dir / ".github" / "workflows" / "tests.yml"
    workflow_content = tests_workflow.read_text(encoding="utf-8")
    assert "test_examples" not in workflow_content


def test_github_actions_when_enabled(copie):
    """Test that GitHub Actions workflows are created when include_actions=True."""
    result = copie.copy(
        extra_answers={
            "include_actions": True,
        },
    )

    assert result.exit_code == 0

    # Check .github directory exists
    github_dir = result.project_dir / ".github"
    assert github_dir.is_dir(), ".github/ directory not created"

    # Check workflows directory exists
    workflows_dir = github_dir / "workflows"
    assert workflows_dir.is_dir(), ".github/workflows/ directory not created"

    # Check for required workflow files
    assert (workflows_dir / "tests.yml").is_file(), "tests.yml workflow not created"
    assert (workflows_dir / "publish-release.yml").is_file(), "publish-release.yml workflow not created"
    assert (workflows_dir / "changelog.yml").is_file(), "changelog.yml workflow not created"
    assert (workflows_dir / "pr-title.yml").is_file(), "pr-title.yml workflow not created"
    assert (workflows_dir / "nightly.yml").is_file(), "nightly.yml workflow not created"

    # Check for GitHub configuration files
    assert (github_dir / "dependabot.yml").is_file(), "dependabot.yml not created"
    assert (github_dir / "PULL_REQUEST_TEMPLATE.md").is_file(), "PR template not created"

    # Check ISSUE_TEMPLATE directory
    issue_template_dir = github_dir / "ISSUE_TEMPLATE"
    assert issue_template_dir.is_dir(), "ISSUE_TEMPLATE directory not created"
    assert (issue_template_dir / "bug_report.yml").is_file(), "bug_report.yml not created"
    assert (issue_template_dir / "feature_request.yml").is_file(), "feature_request.yml not created"
    assert (issue_template_dir / "config.yml").is_file(), "issue template config.yml not created"

    # Check workflow content uses uv
    tests_workflow_content = (workflows_dir / "tests.yml").read_text(encoding="utf-8")
    assert "astral-sh/setup-uv" in tests_workflow_content, "uv not used in tests workflow"

    # Check git-cliff.toml exists (should be included with workflows)
    assert (result.project_dir / ".git-cliff.toml").is_file(), ".git-cliff.toml not created"


def test_github_actions_when_disabled(copie):
    """Test that GitHub Actions workflows are NOT created when include_actions=False."""
    result = copie.copy(
        extra_answers={
            "include_actions": False,
        },
    )

    assert result.exit_code == 0

    # .github directory may exist but workflows should not
    github_dir = result.project_dir / ".github"
    if github_dir.is_dir():
        # Check that workflows directory doesn't exist or is empty
        workflows_dir = github_dir / "workflows"
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml"))
            assert len(workflow_files) == 0, (
                f".github/workflows should be empty but contains: {[f.name for f in workflow_files]}"
            )

    # git-cliff.toml should not exist or be empty (only needed with workflows)
    git_cliff = result.project_dir / ".git-cliff.toml"
    if git_cliff.exists():
        content = git_cliff.read_text(encoding="utf-8").strip()
        assert content == "", ".git-cliff.toml should be empty when GitHub Actions are disabled"


def test_markdown_docs_script_configuration(copie):
    """Test that hooks are properly configured for site preparation."""
    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )

    assert result.exit_code == 0

    # Verify mkdocs hooks.py exists
    hooks_file = result.project_dir / "docs" / "hooks.py"
    assert hooks_file.is_file(), "docs/hooks.py not created"

    # Verify hooks.py has all required hooks
    hooks_content = hooks_file.read_text(encoding="utf-8")
    assert "on_pre_build" in hooks_content, "on_pre_build hook not found"
    assert "on_post_build" in hooks_content, "on_post_build hook not found"

    # Check marimo export logic
    assert "marimo" in hooks_content.lower(), "hooks.py doesn't handle marimo export"
    assert "export" in hooks_content, "hooks.py doesn't export notebooks"

    # Check HTML and markdown copying logic
    assert "shutil.copy2" in hooks_content, "hooks.py doesn't copy files"
    assert "index.html" in hooks_content, "hooks.py doesn't handle HTML files"
    assert "markdown" in hooks_content.lower(), "hooks.py doesn't handle markdown files"

    # Verify mkdocs.yml configures hooks
    mkdocs_content = (result.project_dir / "mkdocs.yml").read_text(encoding="utf-8")
    assert "hooks:" in mkdocs_content, "mkdocs.yml doesn't configure hooks"
    assert "docs/hooks.py" in mkdocs_content, "mkdocs.yml doesn't reference hooks.py"

    # Scripts directory may exist for other utilities
    # export_marimo_examples.py and prepare_site.py are no longer needed (replaced by hooks)


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skip(reason="Marimo HTML export feature not fully implemented in examples.md template")
def test_marimo_notebook_export_to_html(copie):
    """Test that marimo notebooks are properly exported to standalone HTML."""
    import subprocess

    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )

    assert result.exit_code == 0

    # Verify docs/examples directory exists
    docs_examples_dir = result.project_dir / "docs" / "examples"
    assert docs_examples_dir.is_dir(), "docs/examples/ directory not created"

    # Run mkdocs build which triggers hooks to export notebooks
    export_result = subprocess.run(
        ["uvx", "nox", "-s", "build_docs"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert export_result.returncode == 0, (
        f"export_examples failed:\nSTDOUT:\n{export_result.stdout}\n\nSTDERR:\n{export_result.stderr}"
    )

    # Verify HTML file was created
    hello_html = docs_examples_dir / "hello" / "index.html"
    assert hello_html.is_file(), (
        f"hello/index.html not created. docs/examples structure: {list(docs_examples_dir.rglob('*'))}"
    )

    # Verify HTML content
    html_content = hello_html.read_text(encoding="utf-8")
    assert len(html_content) > 1000, "HTML file is suspiciously small"

    # Check for marimo WASM runtime (key indicator of HTML-WASM export)
    assert "marimo" in html_content.lower(), "HTML doesn't contain marimo references"
    assert "wasm" in html_content.lower() or "pyodide" in html_content.lower(), (
        "HTML doesn't contain WASM/Pyodide runtime indicators"
    )

    # Verify the HTML is standalone (not just a stub)
    assert "<html" in html_content.lower(), "HTML doesn't have html tag"
    assert "<script" in html_content.lower(), "HTML doesn't have script tags"

    # Verify HTML file has reasonable size (marimo HTML exports are typically 20KB+)
    html_size_kb = len(html_content) / 1024
    assert html_size_kb > 10, f"HTML file is only {html_size_kb:.1f}KB, suspiciously small"


@pytest.mark.integration
@pytest.mark.slow
def test_markdown_docs_created_and_clean(copie):
    """Test that markdown files are created during build and are clean (no HTML tags)."""
    import subprocess

    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )

    assert result.exit_code == 0

    # Build the docs which should create markdown copies
    build_result = subprocess.run(
        ["uvx", "nox", "-s", "build_docs"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert build_result.returncode == 0, (
        f"build_docs failed:\nSTDOUT:\n{build_result.stdout}\n\nSTDERR:\n{build_result.stderr}"
    )

    # Verify site directory exists
    site_dir = result.project_dir / "site"
    assert site_dir.is_dir(), "site/ directory not created by build_docs"

    # Find all markdown files in site/
    md_files = list(site_dir.rglob("*.md"))
    assert len(md_files) > 0, f"No markdown files found in site/. Site structure: {list(site_dir.iterdir())}"

    # Verify key markdown files exist
    expected_md_files = ["index.md", "getting-started.md", "concepts.md"]
    found_names = {f.name for f in md_files}
    for expected in expected_md_files:
        assert expected in found_names, f"{expected} not found in site/. Found: {found_names}"

    # Verify markdown files contain content and are clean (no HTML tags)
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        assert len(content) > 0, f"{md_file} is empty"

        # Should not contain raw HTML tags from mkdocs-material
        # Exception: index.md can contain <div class="grid cards"> for Material CTA cards
        html_tags_to_check = ["<article", "<div class=", "<nav class=", "<header class="]
        for tag in html_tags_to_check:
            # Allow <div class=> in index.md for Material grid cards feature
            if tag == "<div class=" and md_file.name == "index.md":
                continue
            assert tag not in content, f"{md_file.name} contains HTML tag: {tag}"

        # Should contain markdown formatting
        # At least one of these markdown elements should be present
        has_markdown = any(marker in content for marker in ["# ", "## ", "- ", "* ", "[", "```", "**", "__"])
        assert has_markdown, f"{md_file.name} doesn't appear to contain markdown formatting"


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skip(reason="Marimo HTML export feature not fully implemented in examples.md template")
def test_three_tier_documentation_system(copie):
    """Test that all three documentation tiers work together."""
    import subprocess

    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )

    assert result.exit_code == 0

    # Tier 1: Verify embedded marimo setup in examples.md
    examples_md = result.project_dir / "docs" / "pages" / "tutorials" / "examples.md"
    examples_content = examples_md.read_text(encoding="utf-8")
    # Check for marimo-embed directive with inline code
    has_marimo = "/// marimo-embed" in examples_content and "@app.cell" in examples_content
    assert has_marimo, "Embedded marimo notebook not found in examples.md"

    # Tier 2: Build docs which triggers hooks to export standalone HTML
    export_result = subprocess.run(
        ["uvx", "nox", "-s", "build_docs"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert export_result.returncode == 0, (
        f"build_docs failed:\nSTDOUT:\n{export_result.stdout}\n\nSTDERR:\n{export_result.stderr}"
    )
    standalone_html = result.project_dir / "docs" / "examples" / "hello" / "index.html"
    assert standalone_html.is_file(), "Standalone HTML not created (Tier 2)"

    # Verify examples.md links to standalone HTML
    assert "Standalone HTML Notebooks" in examples_content, "No standalone section in examples.md"
    assert "../examples/hello/" in examples_content, "No link to standalone HTML in examples.md"

    # Verify mkdocs excludes standalone HTML from processing
    mkdocs_yml = result.project_dir / "mkdocs.yml"
    mkdocs_content = mkdocs_yml.read_text(encoding="utf-8")
    assert "exclude_docs:" in mkdocs_content, "mkdocs.yml doesn't have exclude_docs"
    assert "examples/**/index.html" in mkdocs_content, "mkdocs.yml doesn't exclude standalone HTML files"
    assert "examples/**/CLAUDE.md" in mkdocs_content, "mkdocs.yml doesn't exclude CLAUDE.md files"

    # Tier 3: Verify markdown copies were created
    markdown_copy = result.project_dir / "site" / "index.md"
    assert markdown_copy.is_file(), "Markdown copy not created (Tier 3)"

    # Verify all three tiers are present
    assert examples_md.is_file(), "Tier 1 (embedded) missing"
    assert standalone_html.is_file(), "Tier 2 (standalone HTML) missing"
    assert markdown_copy.is_file(), "Tier 3 (markdown copies) missing"


@pytest.mark.integration
@pytest.mark.slow
def test_generated_package_can_be_installed(copie):
    """Smoke test: verify the generated package can be installed with uv sync.

    This test validates that:
    - pyproject.toml is valid
    - All dependencies can be resolved
    - The package can be installed in a virtual environment
    """
    import subprocess

    result = copie.copy(extra_answers={"include_examples": True})
    assert result.exit_code == 0

    # Run uv sync to install the package and all dependencies
    sync_result = subprocess.run(
        ["uv", "sync", "--all-groups"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert sync_result.returncode == 0, (
        f"uv sync failed:\nSTDOUT:\n{sync_result.stdout}\n\nSTDERR:\n{sync_result.stderr}"
    )

    # Verify the package can be imported
    import_result = subprocess.run(
        ["uv", "run", "python", "-c", "import test_project; print(test_project.__version__)"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert import_result.returncode == 0, (
        f"Package import failed:\nSTDOUT:\n{import_result.stdout}\n\nSTDERR:\n{import_result.stderr}"
    )


@pytest.mark.integration
@pytest.mark.slow
def test_generated_project_nox_sessions(copie_session_default):
    """Consolidated smoke test: run all nox sessions on a generated project.

    This comprehensive test validates that all development workflows work:
    - test_coverage: Tests run and coverage is generated
    - lint: Code quality checks pass (ruff, ty)
    - test_docstrings: Doctests pass
    - test_examples: Example notebooks execute successfully
    - build_docs: Documentation builds without errors

    Using session-scoped fixture to avoid regenerating project multiple times.
    This test replaces individual session tests for better performance.
    """
    import subprocess

    result = copie_session_default
    assert result.exit_code == 0

    # Define all nox sessions to test with timeouts
    sessions_to_test = [
        ("test_coverage", 180, "Tests and coverage generation"),
        ("lint", 120, "Code quality checks (ruff + ty)"),
        ("test_docstrings", 120, "Docstring tests"),
        ("test_examples", 120, "Example notebook execution"),
        ("build_docs", 180, "Documentation build"),
    ]

    # Run each session and collect results
    for session_name, timeout, description in sessions_to_test:
        session_result = subprocess.run(
            ["uvx", "nox", "-s", session_name],
            cwd=result.project_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        assert session_result.returncode == 0, (
            f"Session '{session_name}' ({description}) failed:\n"
            f"STDOUT:\n{session_result.stdout}\n\n"
            f"STDERR:\n{session_result.stderr}"
        )

    # Verify expected outputs exist
    assert (result.project_dir / "site" / "index.html").is_file(), "Docs site not generated"
    assert (result.project_dir / ".coverage").exists() or (result.project_dir / "coverage.xml").exists(), (
        "Coverage file not generated"
    )


@pytest.mark.integration
@pytest.mark.slow
def test_generated_source_files_are_valid_python(copie):
    """Smoke test: validate that all generated Python files are syntactically correct.

    This uses Python's ast module to parse all generated .py files.
    """
    import ast

    result = copie.copy(extra_answers={"include_examples": True})
    assert result.exit_code == 0

    # Find all Python files in the generated project (excluding site/ and .venv/)
    python_files = []
    for py_file in result.project_dir.rglob("*.py"):
        # Skip generated site directory and virtual environments
        if "site/" in str(py_file) or ".venv/" in str(py_file) or "__pycache__" in str(py_file):
            continue
        python_files.append(py_file)

    assert len(python_files) > 0, "No Python files found in generated project"

    # Try to parse each Python file
    for py_file in python_files:
        try:
            content = py_file.read_text(encoding="utf-8")
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {py_file.relative_to(result.project_dir)}: {e}")


@pytest.mark.integration
def test_copier_answers_file_generated(copie):
    """Test that .copier-answers.yml is generated for template updates.

    This file is critical for running 'copier update' in the future.
    """
    result = copie.copy(extra_answers={"project_name": "Test Project"})
    assert result.exit_code == 0

    copier_answers = result.project_dir / ".copier-answers.yml"
    assert copier_answers.is_file(), ".copier-answers.yml not generated"

    # Verify it contains copier metadata (answers may not be included by default)
    content = copier_answers.read_text(encoding="utf-8")
    assert "_commit:" in content or "_src_path:" in content  # copier metadata


def test_copier_answers_stores_all_user_inputs(copie):
    """Test that .copier-answers.yml stores all user answers for template updates.

    This is essential for 'copier update' to work correctly.
    """
    custom_answers = {
        "project_name": "My Test Package",
        "package_name": "my_test_pkg",
        "project_slug": "my-test-package",
        "description": "A custom test description",
        "author_name": "Jane Developer",
        "author_email": "jane@example.com",
        "github_username": "janedev",
        "min_python_version": "3.12",
        "max_python_version": "3.13",
        "license": "Apache-2.0",
        "include_actions": False,
        "include_examples": False,
    }

    result = copie.copy(extra_answers=custom_answers)
    assert result.exit_code == 0

    copier_answers = result.project_dir / ".copier-answers.yml"
    assert copier_answers.is_file()

    content = copier_answers.read_text(encoding="utf-8")

    # Verify copier metadata is present
    assert "_commit:" in content, "Missing _commit in .copier-answers.yml"
    assert "_src_path:" in content, "Missing _src_path in .copier-answers.yml"
    assert "gh:stateful-y/python-package-copier" in content

    # Verify all user answers are stored
    assert "author_email: jane@example.com" in content
    assert "author_name: Jane Developer" in content
    assert "description: A custom test description" in content
    assert "github_username: janedev" in content
    assert "include_actions: false" in content or "include_actions: False" in content
    assert "include_examples: false" in content or "include_examples: False" in content
    assert "license: Apache-2.0" in content
    assert "max_python_version: '3.13'" in content or "max_python_version: 3.13" in content
    assert "min_python_version: '3.12'" in content or "min_python_version: 3.12" in content
    assert "package_name: my_test_pkg" in content
    assert "project_name: My Test Package" in content
    assert "project_slug: my-test-package" in content


def test_max_python_version_in_classifiers(copie):
    """Test that pyproject.toml classifiers include all Python versions from min to max."""
    result = copie.copy(
        extra_answers={
            "min_python_version": "3.11",
            "max_python_version": "3.13",
        },
    )
    assert result.exit_code == 0

    pyproject_path = result.project_dir / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")

    # Should include 3.11, 3.12, 3.13
    assert '"Programming Language :: Python :: 3.11"' in content
    assert '"Programming Language :: Python :: 3.12"' in content
    assert '"Programming Language :: Python :: 3.13"' in content
    # Should NOT include 3.14
    assert '"Programming Language :: Python :: 3.14"' not in content


def test_max_python_version_single_version(copie):
    """Test that when min equals max, only one version classifier is included."""
    result = copie.copy(
        extra_answers={
            "min_python_version": "3.12",
            "max_python_version": "3.12",
        },
    )
    assert result.exit_code == 0

    pyproject_path = result.project_dir / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")

    # Should only include 3.12
    assert '"Programming Language :: Python :: 3.12"' in content
    # Should NOT include others
    assert '"Programming Language :: Python :: 3.11"' not in content
    assert '"Programming Language :: Python :: 3.13"' not in content
    assert '"Programming Language :: Python :: 3.14"' not in content


def test_max_python_version_in_noxfile(copie):
    """Test that noxfile uses max_python_version to limit Python versions."""
    result = copie.copy(
        extra_answers={
            "min_python_version": "3.11",
            "max_python_version": "3.12",
        },
    )
    assert result.exit_code == 0

    noxfile_path = result.project_dir / "noxfile.py"
    content = noxfile_path.read_text(encoding="utf-8")

    # Should have both MIN_VERSION and MAX_VERSION constants
    assert 'MIN_VERSION = "3.11"' in content
    assert 'MAX_VERSION = "3.12"' in content
    # Should filter versions with both min and max
    assert "v >= MIN_VERSION and v <= MAX_VERSION" in content


def test_max_python_version_in_github_workflows(copie):
    """Test that GitHub workflow matrix uses max_python_version."""
    result = copie.copy(
        extra_answers={
            "min_python_version": "3.12",
            "max_python_version": "3.13",
            "include_actions": True,
        },
    )
    assert result.exit_code == 0

    tests_workflow = result.project_dir / ".github" / "workflows" / "tests.yml"
    content = tests_workflow.read_text(encoding="utf-8")

    # Should include 3.12 and 3.13 in matrix
    assert '"3.12"' in content
    assert '"3.13"' in content
    # Should NOT include 3.11 or 3.14
    assert '"3.11"' not in content
    assert '"3.14"' not in content


def test_max_python_version_full_range(copie):
    """Test max_python_version with full range 3.11-3.14."""
    result = copie.copy(
        extra_answers={
            "min_python_version": "3.11",
            "max_python_version": "3.14",
        },
    )
    assert result.exit_code == 0

    # Check pyproject.toml classifiers
    pyproject_path = result.project_dir / "pyproject.toml"
    pyproject_content = pyproject_path.read_text(encoding="utf-8")
    assert '"Programming Language :: Python :: 3.11"' in pyproject_content
    assert '"Programming Language :: Python :: 3.12"' in pyproject_content
    assert '"Programming Language :: Python :: 3.13"' in pyproject_content
    assert '"Programming Language :: Python :: 3.14"' in pyproject_content

    # Check noxfile
    noxfile_path = result.project_dir / "noxfile.py"
    noxfile_content = noxfile_path.read_text(encoding="utf-8")
    assert 'MIN_VERSION = "3.11"' in noxfile_content
    assert 'MAX_VERSION = "3.14"' in noxfile_content

    # Check GitHub workflow
    tests_workflow = result.project_dir / ".github" / "workflows" / "tests.yml"
    workflow_content = tests_workflow.read_text(encoding="utf-8")
    assert '"3.11"' in workflow_content
    assert '"3.12"' in workflow_content
    assert '"3.13"' in workflow_content
    assert '"3.14"' in workflow_content


def test_max_python_version_requires_python_unchanged(copie):
    """Test that max_python_version doesn't affect requires-python (only min matters)."""
    result = copie.copy(
        extra_answers={
            "min_python_version": "3.12",
            "max_python_version": "3.13",
        },
    )
    assert result.exit_code == 0

    pyproject_path = result.project_dir / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")

    # requires-python should only use min_python_version
    assert 'requires-python = ">=3.12"' in content
    # Should NOT mention max version in requires-python
    assert "<=3.13" not in content


def test_max_python_version_validation_fails_when_less_than_min(copie):
    """Test that copier validation fails when max_python_version < min_python_version."""
    import pytest

    with pytest.raises(ValueError, match="Validation error.*max_python_version.*Maximum Python version must be"):
        copie.copy(
            extra_answers={
                "min_python_version": "3.13",
                "max_python_version": "3.11",  # Invalid: less than min
            },
        )


def test_max_python_version_validation_passes_when_equal_to_min(copie):
    """Test that validation passes when max_python_version equals min_python_version."""
    result = copie.copy(
        extra_answers={
            "min_python_version": "3.12",
            "max_python_version": "3.12",  # Valid: equal to min
        },
    )

    # Should succeed
    assert result.exit_code == 0
    assert result.exception is None


@pytest.mark.integration
@pytest.mark.slow
def test_example_tests_run_successfully_with_pytest(copie):
    """Test that generated example tests run successfully using pytest directly."""
    import subprocess

    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )

    assert result.exit_code == 0

    # Install dependencies in the generated project
    install_result = subprocess.run(
        ["uv", "sync", "--group", "tests", "--group", "examples"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert install_result.returncode == 0, (
        f"uv sync failed:\nSTDOUT:\n{install_result.stdout}\n\nSTDERR:\n{install_result.stderr}"
    )

    # Run the example tests using pytest directly (disable coverage for this test)
    test_result = subprocess.run(
        ["uv", "run", "pytest", "tests/test_examples.py", "-m", "example", "-v", "--no-cov"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert test_result.returncode == 0, (
        f"pytest test_examples.py failed:\nSTDOUT:\n{test_result.stdout}\n\nSTDERR:\n{test_result.stderr}"
    )

    # Verify test output shows the notebook was tested
    assert "test_notebook_runs_without_error[" in test_result.stdout
    assert "notebook_file" in test_result.stdout  # pytest parametrize creates notebook_file0, etc.
    assert "passed" in test_result.stdout.lower()


@pytest.mark.integration
@pytest.mark.slow
def test_example_tests_run_successfully_with_nox(copie):
    """Test that generated example tests run successfully using nox test_examples session."""
    import subprocess

    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )

    assert result.exit_code == 0

    # Run the test_examples nox session
    nox_result = subprocess.run(
        ["uvx", "nox", "-s", "test_examples"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert nox_result.returncode == 0, (
        f"nox test_examples failed:\nSTDOUT:\n{nox_result.stdout}\n\nSTDERR:\n{nox_result.stderr}"
    )

    # Verify nox output shows tests ran
    output = nox_result.stdout + nox_result.stderr
    assert "test_examples" in output
    assert "passed" in output.lower() or "1 passed" in output


@pytest.mark.integration
@pytest.mark.slow
def test_generated_project_all_tests_pass(copie):
    """Test that all tests in a generated project pass, including examples."""
    import subprocess

    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )

    assert result.exit_code == 0

    # Install dependencies
    install_result = subprocess.run(
        ["uv", "sync", "--group", "tests", "--group", "examples"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert install_result.returncode == 0, (
        f"uv sync failed:\nSTDOUT:\n{install_result.stdout}\n\nSTDERR:\n{install_result.stderr}"
    )

    # Run all tests (including example tests) - disable coverage
    test_result = subprocess.run(
        ["uv", "run", "pytest", "tests/", "-v", "--no-cov"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert test_result.returncode == 0, (
        f"pytest failed:\nSTDOUT:\n{test_result.stdout}\n\nSTDERR:\n{test_result.stderr}"
    )

    # Verify both regular tests and example tests ran
    assert "test_hello.py" in test_result.stdout
    assert "test_examples.py" in test_result.stdout
    assert "notebook_file" in test_result.stdout  # parametrized test name
    assert "passed" in test_result.stdout.lower()


def test_code_of_conduct_content(copie):
    """Test that CODE_OF_CONDUCT.md is generated with correct email."""
    custom_email = "test@example.com"
    result = copie.copy(extra_answers={"author_email": custom_email})

    assert result.exit_code == 0
    assert result.exception is None

    coc_path = result.project_dir / "CODE_OF_CONDUCT.md"
    assert coc_path.is_file()

    content = coc_path.read_text(encoding="utf-8")
    assert f"contacting the project team at {custom_email}" in content
    assert "gtauzin@stateful-y.io" not in content


def test_update_from_template_skill_generated(copie_session_default):
    """Test that the update-from-template skill is included in generated projects."""
    result = copie_session_default

    skill_dir = result.project_dir / ".github" / "skills" / "update-from-template"
    assert skill_dir.is_dir(), "Missing .github/skills/update-from-template/"

    skill_md = skill_dir / "SKILL.md"
    assert skill_md.is_file(), "Missing SKILL.md"

    content = skill_md.read_text(encoding="utf-8")
    assert "name: update-from-template" in content
    assert "copier update" in content

    # Check reference files
    refs_dir = skill_dir / "references"
    assert refs_dir.is_dir(), "Missing references/"
    assert (refs_dir / "file-classification.md").is_file(), "Missing file-classification.md"
    assert (refs_dir / "conflict-resolution.md").is_file(), "Missing conflict-resolution.md"


def test_claude_skills_generated(copie_session_default):
    """Test that Claude Code skills are included in generated projects."""
    result = copie_session_default

    skills_dir = result.project_dir / ".claude" / "skills"
    assert skills_dir.is_dir(), "Missing .claude/skills/"

    # Mirrors .github/skills so both assistants offer the same skills.
    github_skills = {p.name for p in (result.project_dir / ".github" / "skills").iterdir()}
    claude_skills = {p.name for p in skills_dir.iterdir()}
    assert claude_skills == github_skills, f"Skill sets diverged: {claude_skills ^ github_skills}"

    for name in claude_skills:
        assert (skills_dir / name / "SKILL.md").is_file(), f"Missing {name}/SKILL.md"


def test_claude_skills_not_gitignored(copie_session_default):
    """Test that generated projects track .claude/skills/ but ignore personal config.

    ".claude/" would exclude the directory outright and git never descends into an
    excluded directory, so the "!.claude/skills/" negation would silently not apply.
    """
    result = copie_session_default

    gitignore = (result.project_dir / ".gitignore").read_text(encoding="utf-8")
    assert ".claude/*" in gitignore, "Must use '.claude/*' so the negation is reachable"
    assert "!.claude/skills/" in gitignore, "Missing negation to track shipped skills"
    assert not re.search(r"^\.claude/$", gitignore, re.MULTILINE), (
        "'.claude/' excludes the directory and makes '!.claude/skills/' unreachable"
    )


def _load_hooks(project_dir, unique_suffix):
    """Import a generated docs/hooks.py under a unique module name.

    The module name must be unique per project: importing two differently
    generated hooks modules under one name makes ``sys.modules`` return the
    first, so the second variant is never actually exercised and the test
    passes while asserting nothing.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(f"generated_hooks_{unique_suffix}", project_dir / "docs" / "hooks.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_reexport_package(project_dir, package_name):
    """Lay down a package whose public API is exposed entirely by re-export."""
    pkg = project_dir / "src" / package_name
    sub = pkg / "shapes"
    sub.mkdir(parents=True, exist_ok=True)
    (sub / "_impl.py").write_text(
        '"""Private implementation module."""\n\n\n'
        'class Circle:\n    """A round shape."""\n\n\n'
        'class Square:\n    """A boxy shape."""\n\n\n'
        'def area(shape):\n    """Compute an area."""\n    return 0\n',
        encoding="utf-8",
    )
    (sub / "__init__.py").write_text(
        '"""Shapes."""\n\n'
        "from pathlib import Path\n"
        f"from {package_name}.shapes._impl import Circle, area\n"
        "from ._impl import Square as Box\n\n"
        "MAX_SIDES = 4\n\n"
        '__all__ = ["Box", "Circle", "MAX_SIDES", "area"]\n',
        encoding="utf-8",
    )

    # A package with NO __all__: here the package-root guard in
    # _resolve_import_from is what must reject `from pathlib import Path`. The
    # __all__-bearing package above cannot exercise it -- the filter rejects
    # Path first, so the guard is never consulted.
    noall = pkg / "noall"
    noall.mkdir(parents=True, exist_ok=True)
    (noall / "_impl.py").write_text('"""Impl."""\n\n\nclass Gadget:\n    """A gadget."""\n', encoding="utf-8")
    (noall / "__init__.py").write_text(
        '"""No dunder all."""\n\nfrom pathlib import Path\nfrom ._impl import Gadget\n',
        encoding="utf-8",
    )

    # A package exposing an optional extra, guarding its re-exports in a try block.
    optional = pkg / "optional"
    optional.mkdir(parents=True, exist_ok=True)
    (optional / "_impl.py").write_text(
        '"""Optional implementation."""\n\n\nclass Widget:\n    """An optional widget."""\n',
        encoding="utf-8",
    )
    (optional / "__init__.py").write_text(
        '"""Optional feature."""\n\n'
        "try:\n"
        f"    from {package_name}.optional._impl import Widget\n"
        "except ImportError as err:  # pragma: no cover\n"
        '    raise ImportError("install extras") from err\n\n'
        '__all__ = ["Widget"]\n',
        encoding="utf-8",
    )
    return pkg


def test_reexported_symbols_resolve(copie_session_minimal):
    """Re-exported symbols resolve, and the API page members table populates."""
    project_dir = copie_session_minimal.project_dir
    pkg = _write_reexport_package(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "reexport")

    members = hooks._get_public_members(pkg / "shapes" / "__init__.py", pkg)
    names = {e["name"] for e in members["classes"] + members["functions"]}

    # Re-exported classes and functions are found, despite the __init__ declaring none.
    assert "Circle" in names, "re-exported class not resolved"
    assert "area" in names, "re-exported function not resolved"
    # Aliased re-export resolves under the exposed name, not the declared one.
    assert "Box" in names, "aliased re-export not resolved under its exposed name"
    assert "Square" not in names, "aliased re-export leaked its declared name"
    # __all__ filters, it does not authorise: a constant has no page, so it must not resolve.
    assert "MAX_SIDES" not in names, "__all__-listed constant resolved but has no page"
    # An import that leaves the package is not part of this package's API.
    assert "Path" not in names, "incidental third-party import resolved"

    # Classes and functions are bucketed correctly, with descriptions from the declaring module.
    assert {e["name"] for e in members["classes"]} == {"Circle", "Box"}
    assert {e["name"] for e in members["functions"]} == {"area"}
    assert next(e for e in members["classes"] if e["name"] == "Circle")["doc"] == "A round shape."


def test_reexports_guarded_by_try_resolve(copie_session_minimal):
    """Re-exports guarded by a try block (the optional-extra idiom) still resolve.

    ``ast.iter_child_nodes`` sees only the ``Try`` node, so a top-level-only
    scan silently renders an empty API page for these packages.
    """
    project_dir = copie_session_minimal.project_dir
    pkg = _write_reexport_package(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "tryblock")

    members = hooks._get_public_members(pkg / "optional" / "__init__.py", pkg)
    names = {e["name"] for e in members["classes"] + members["functions"]}

    assert "Widget" in names, "re-export inside a try block was not resolved"
    assert next(e for e in members["classes"] if e["name"] == "Widget")["doc"] == "An optional widget."


def test_api_name_lookup_without_importing_package(copie_session_minimal):
    """The lookup is built by static analysis, never by importing the package."""
    import sys

    project_dir = copie_session_minimal.project_dir
    _write_reexport_package(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "noimport")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    lookup = hooks._get_api_name_lookup(project_dir)

    assert lookup.get("Circle") == "minimal_project.shapes.Circle", (
        f"re-exported symbol not in lookup: {sorted(lookup)}"
    )
    assert "minimal_project" not in sys.modules, "hooks imported the generated package"


def test_api_name_lookup_every_name_has_a_page(copie_session_minimal):
    """Interlock: every resolvable name has a generated page to link to."""
    project_dir = copie_session_minimal.project_dir
    _write_reexport_package(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "interlock")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    hooks._generate_api_pages(project_dir)
    generated = {p.stem for p in (project_dir / "docs" / "pages" / "api" / "generated").glob("*.md")}
    lookup = hooks._get_api_name_lookup(project_dir)

    # Guard against a vacuous pass: the re-exported symbols must actually be under test.
    assert "Circle" in lookup, f"re-export package not picked up; lookup={sorted(lookup)}"
    missing = sorted(q for q in lookup.values() if q not in generated)
    assert not missing, f"lookup resolves names with no generated page: {missing}"


def test_api_name_lookup_available_without_examples(copie_session_minimal):
    """The lookup is not gated behind include_examples."""
    hooks_source = (copie_session_minimal.project_dir / "docs" / "hooks.py").read_text(encoding="utf-8")
    assert "def _get_api_name_lookup" in hooks_source, "lookup missing when examples are disabled"
    assert "_API_NAME_LOOKUP_CACHE" in hooks_source, "lookup cache missing when examples are disabled"
    assert "def _get_notebook_api_usage" not in hooks_source, "gallery code leaked into a no-examples project"


def test_api_name_lookup_shared_with_notebook_usage(copie_session_default):
    """The gallery consumes the shared lookup instead of building its own map."""
    hooks_source = (copie_session_default.project_dir / "docs" / "hooks.py").read_text(encoding="utf-8")
    assert "def _get_api_name_lookup" in hooks_source
    assert "name_to_qualified = _get_api_name_lookup(project_root)" in hooks_source, (
        "_get_notebook_api_usage must consume the shared lookup, not derive a second map"
    )


class _FakeFile:
    def __init__(self, src_path, dest_path):
        self.src_path = src_path
        self.dest_path = dest_path


class _FakePage:
    """The subset of mkdocs' Page that on_page_content actually touches."""

    def __init__(self, src_path, dest_path):
        self.file = _FakeFile(src_path, dest_path)
        self.meta = {}
        self.toc = []


def _see_also_page(package_name, class_name, entries, *, method_entries=""):
    """Build a page shaped like real mkdocstrings output.

    The ``<h2 id="{pkg}.{Class}">`` and the ``doc-children`` boundary are not
    decoration: without the h2, ``_process_api_page_content`` returns early, and
    a fixture missing it makes every downstream assertion meaningless.
    """
    method_block = ""
    if method_entries:
        method_block = (
            f'<h3 id="{package_name}.{class_name}.fit">fit</h3>'
            f'<details class="see-also" open><summary>See Also</summary><p>{method_entries}</p></details>'
        )
    return (
        f'<h2 id="{package_name}.{class_name}">{class_name}</h2>'
        f'<div class="doc doc-contents">'
        f'<details class="see-also" open><summary>See Also</summary><p>{entries}</p></details>'
        f"</div>"
        f'<div class="doc doc-children">{method_block}</div>'
    )


def _generated_page(package_name, class_name):
    src = f"pages/api/generated/{package_name}.models.{class_name}.md"
    return _FakePage(src, src.replace(".md", "/index.html"))


def _write_models_module(project_dir, package_name):
    """A module with sibling classes for See Also entries to point at."""
    (project_dir / "src" / package_name / "models.py").write_text(
        '"""Models."""\n\n\nclass Alpha:\n    """Alpha."""\n\n\nclass Beta:\n    """Beta."""\n\n\nclass Gamma:\n    """Gamma."""\n',
        encoding="utf-8",
    )


def test_see_also_links_class_level_entries(copie_session_minimal):
    """Class-level See Also entries link — the case a post-restructure hook misses.

    Driven through on_page_content, not the linkifier alone: the container this
    feature depends on is destroyed partway through that function, so testing
    the linkifier in isolation proves nothing about the real pipeline.
    """
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "seealso_class")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    # One entry per line, as mkdocstrings actually renders them. Running them
    # together on one line hides whether the linkifier respects entry boundaries.
    html = _see_also_page(
        "minimal_project",
        "Alpha",
        "Beta : Plain numpydoc.\n<code>Gamma</code> : Backticked.\nNotARealThing : Unknown.",
    )
    out = hooks.on_page_content(html, _generated_page("minimal_project", "Alpha"), {}, None)

    assert '<a href="../minimal_project.models.Beta/">Beta</a>' in out, "plain entry not linked"
    assert '<a href="../minimal_project.models.Gamma/"><code>Gamma</code></a>' in out, "code-span entry not linked"
    assert "Plain numpydoc." in out, "description text was altered"
    assert not re.search(r"<a[^>]*>NotARealThing", out), "unresolvable entry was linked"
    # The container is gone by the end -- proof the linkifier ran before the restructure.
    assert '<details class="see-also"' not in out


def test_see_also_links_method_level_entries(copie_session_minimal):
    """Method-level See Also entries link too (they sit outside class_region)."""
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "seealso_method")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    html = _see_also_page("minimal_project", "Alpha", "Beta : Class level.", method_entries="Gamma : Method level.")
    out = hooks.on_page_content(html, _generated_page("minimal_project", "Alpha"), {}, None)

    assert '<a href="../minimal_project.models.Gamma/">Gamma</a>' in out, "method-level entry not linked"


def _write_glossary(project_dir, extra=""):
    """A glossary page in the shape the linker reads: def-list terms with anchors."""
    page = project_dir / "docs" / "pages" / "explanation" / "glossary.md"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        "# Glossary\n\n"
        "## Core\n\n"
        "Memory buffer { #memory-buffer .autolink }\n"
        ":   The store of recent rows.\n\n"
        "Forecasting horizon { #forecasting-horizon .autolink }\n"
        ":   How far ahead to predict.\n\n"
        # Defined but NOT opted in: a short common word that would over-link.
        "Step { #step }\n"
        ":   One timestep.\n\n" + extra,
        encoding="utf-8",
    )
    return page


def _glossary_page(src="pages/explanation/concepts.md"):
    return _FakePage(src, src.replace(".md", "/index.html"))


def test_glossary_terms_link_on_other_pages(copie_session_minimal):
    """A term marked .autolink links to the glossary, once, from prose only.

    The glossary page is the single source of truth: a second list of terms in
    hooks.py would drift from the definitions it points at.
    """
    project_dir = copie_session_minimal.project_dir
    _write_glossary(project_dir)
    hooks = _load_hooks(project_dir, "glossary_link")
    hooks._GLOSSARY_TERMS_CACHE = None

    html = "<p>The memory buffer holds rows. A second memory buffer mention.</p><p>The forecasting horizon matters.</p>"
    out = hooks.on_page_content(html, _glossary_page(), {}, None)

    assert '<a href="../glossary/#memory-buffer">memory buffer</a>' in out, "term was not linked"
    assert '<a href="../glossary/#forecasting-horizon">forecasting horizon</a>' in out
    # First occurrence only -- linking every mention is noise, not navigation.
    assert out.count('href="../glossary/#memory-buffer"') == 1, "linked more than the first occurrence"


def test_glossary_skips_terms_not_opted_in(copie_session_minimal):
    """A defined term without .autolink is never linked.

    Defining a word and advertising it everywhere are separate decisions. A
    glossary legitimately defines short common words ("step"), and linking those
    wherever prose happens to use them produces noise.
    """
    project_dir = copie_session_minimal.project_dir
    _write_glossary(project_dir)
    hooks = _load_hooks(project_dir, "glossary_optin")
    hooks._GLOSSARY_TERMS_CACHE = None

    out = hooks.on_page_content("<p>Each step is a step.</p>", _glossary_page(), {}, None)

    assert "#step" not in out, "a term that did not opt in was linked"
    assert "Each step is a step." in out, "text was altered"


def test_glossary_never_links_inside_code_or_headings(copie_session_minimal):
    """Code is not prose, and a link inside a heading or another link is broken markup."""
    project_dir = copie_session_minimal.project_dir
    _write_glossary(project_dir)
    hooks = _load_hooks(project_dir, "glossary_skip")
    hooks._GLOSSARY_TERMS_CACHE = None

    html = (
        "<h2>The memory buffer heading</h2>"
        "<pre><code>memory buffer = 1</code></pre>"
        '<p>See <a href="x">the memory buffer docs</a>.</p>'
        "<p>A real memory buffer in prose.</p>"
    )
    out = hooks.on_page_content(html, _glossary_page(), {}, None)

    assert "<h2>The memory buffer heading</h2>" in out, "linked inside a heading"
    assert "<code>memory buffer = 1</code>" in out, "linked inside code"
    assert '<a href="x">the memory buffer docs</a>' in out, "nested a link inside a link"
    assert '<a href="../glossary/#memory-buffer">memory buffer</a>' in out, "prose occurrence was not linked"


def test_glossary_page_does_not_link_itself(copie_session_minimal):
    """The glossary must not turn its own definitions into links to themselves."""
    project_dir = copie_session_minimal.project_dir
    _write_glossary(project_dir)
    hooks = _load_hooks(project_dir, "glossary_self")
    hooks._GLOSSARY_TERMS_CACHE = None

    page = _glossary_page("pages/explanation/glossary.md")
    out = hooks.on_page_content("<p>A memory buffer is defined here.</p>", page, {}, None)

    assert "<a href=" not in out, "the glossary linked its own terms"


def test_glossary_absent_is_not_an_error(copie_session_minimal):
    """Most projects ship no glossary; the feature must simply do nothing."""
    project_dir = copie_session_minimal.project_dir
    glossary = project_dir / "docs" / "pages" / "explanation" / "glossary.md"
    if glossary.exists():
        glossary.unlink()
    hooks = _load_hooks(project_dir, "glossary_absent")
    hooks._GLOSSARY_TERMS_CACHE = None

    html = "<p>A memory buffer here.</p>"
    assert hooks.on_page_content(html, _glossary_page(), {}, None) == html


def test_see_also_links_member_path_entries(copie_session_minimal):
    """A ``Class.member`` See Also entry qualifies to a full autoref identifier.

    A member -- a method or attribute -- has no page of its own; it is an anchor
    on its class page, so it cannot resolve to a direct URL the way a class can.
    Its short leading segment (``Beta``) is a project symbol, so the entry is
    qualified to ``minimal_project.models.Beta.build`` and deferred to autorefs,
    which knows the anchor. The pre-fix path treated any dotted entry whose head
    was not the package as external and emitted the bare ``Beta.build`` as the
    identifier, which never matches the registered qualified name and degraded
    silently to plain text under the ``optional`` attribute.
    """
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "seealso_member")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    html = _see_also_page("minimal_project", "Alpha", "Beta.build : Instantiate from a config.")
    out = hooks.on_page_content(html, _generated_page("minimal_project", "Alpha"), {}, None)

    assert '<autoref optional identifier="minimal_project.models.Beta.build">Beta.build</autoref>' in out, (
        "a Class.member entry was not qualified to its full autoref identifier"
    )
    assert 'identifier="Beta.build"' not in out, "member path was deferred to autorefs unqualified (never resolves)"


def test_see_also_linkify_runs_before_restructure(copie_session_minimal):
    """Order-locking: reordering on_page_content silently reverts this feature.

    Linkifying after the restructure produces nothing for class-level sections
    while still working for method-level ones, so a test that only covers
    method-level entries would not catch the regression.
    """
    hooks_source = (copie_session_minimal.project_dir / "docs" / "hooks.py").read_text(encoding="utf-8")
    body = hooks_source[hooks_source.index("def on_page_content") :]
    linkify_at = body.index("_linkify_see_also(")
    restructure_at = body.index("_process_api_page_content(")
    assert linkify_at < restructure_at, (
        "_linkify_see_also must be called BEFORE _process_api_page_content; "
        "the latter dissolves the <details class='see-also'> block the former matches"
    )


def test_see_also_scoped_to_generated_api_pages(copie_session_minimal):
    """A See Also block on a non-generated page is not rewritten."""
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "seealso_scope")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    html = '<details class="see-also" open><summary>See Also</summary><p>Beta : Nope.</p></details>'
    page = _FakePage("pages/api/models.md", "pages/api/models/index.html")
    out = hooks.on_page_content(html, page, {}, None)

    assert out == html, "linkification leaked outside pages/api/generated/"


def test_see_also_external_name_defers_to_autorefs(copie_session_minimal):
    """An external dotted name is handed to autorefs, not resolved eagerly.

    Inventories are registered into the autorefs URL map but applied in its
    on_env hook, which runs after on_page_content -- asking for the URL here
    raises KeyError even when the inventory is configured. The `optional`
    attribute keeps an unresolvable name quiet rather than failing --strict.
    """
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "seealso_external")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    html = _see_also_page("minimal_project", "Alpha", "sklearn.linear_model.Ridge : External.\nBeta : Project.")
    out = hooks.on_page_content(html, _generated_page("minimal_project", "Alpha"), {}, None)

    assert '<autoref optional identifier="sklearn.linear_model.Ridge">sklearn.linear_model.Ridge</autoref>' in out, (
        "external name was not deferred to autorefs"
    )
    # The project symbol is still resolved here, against the page set we own.
    assert '<a href="../minimal_project.models.Beta/">Beta</a>' in out


def test_see_also_bare_unresolvable_name_is_left_alone(copie_session_minimal):
    """A bare name that misses the project lookup is not offered to autorefs.

    It could resolve to an unrelated symbol sharing the name in some configured
    inventory, and a wrong link is worse than no link.
    """
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "seealso_bare")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    html = _see_also_page("minimal_project", "Alpha", "NotAThing : Unknown bare name.")
    out = hooks.on_page_content(html, _generated_page("minimal_project", "Alpha"), {}, None)

    assert "<autoref" not in out, "a bare name was offered to autorefs"
    assert "NotAThing : Unknown bare name." in out, "bare unresolvable entry was altered"


def test_see_also_qualified_name_matches_bare_form(copie_session_minimal):
    """A fully qualified project entry links to the same page as the bare form."""
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "seealso_qualified")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    html = _see_also_page("minimal_project", "Alpha", "minimal_project.models.Beta : Qualified.")
    out = hooks.on_page_content(html, _generated_page("minimal_project", "Alpha"), {}, None)

    assert '<a href="../minimal_project.models.Beta/">minimal_project.models.Beta</a>' in out, (
        "qualified project name did not resolve to the same page as the bare form"
    )


def _write_notebook(project_dir, stem, gallery_body, imports=""):
    nb = project_dir / "examples" / f"{stem}.py"
    nb.parent.mkdir(parents=True, exist_ok=True)
    nb.write_text(f"import marimo\n\n{imports}\n__gallery__ = {{{gallery_body}}}\n", encoding="utf-8")
    return nb


def test_notebook_export_is_cached_by_source_hash(copie_session_default):
    """An unchanged notebook is not re-exported; an edited one is.

    Exporting means executing the notebook, which dominates the docs build, so
    this is the difference between a fast rebuild and a slow one under
    `mkdocs serve`.
    """
    project_dir = copie_session_default.project_dir
    hooks = _load_hooks(project_dir, "nbcache")

    notebook = project_dir / "examples" / "cache_probe.py"
    notebook.parent.mkdir(parents=True, exist_ok=True)
    notebook.write_text("x = 1\n", encoding="utf-8")
    output_dir = project_dir / "docs" / "examples" / "cache_probe"
    output_dir.mkdir(parents=True, exist_ok=True)

    digest = hooks._notebook_content_hash(notebook)

    # Nothing exported yet.
    assert not hooks._is_cached(output_dir, digest), "claimed a cache hit with no exported page"

    # A hash with no rendered page must not count: the export may have died
    # before writing the html, and reusing that ships a missing page.
    (output_dir / hooks._SOURCE_HASH_FILE).write_text(digest, encoding="utf-8")
    assert not hooks._is_cached(output_dir, digest), "claimed a cache hit with no index.html"

    (output_dir / "index.html").write_text("<html></html>", encoding="utf-8")
    assert hooks._is_cached(output_dir, digest), "did not reuse an unchanged export"

    # Editing the notebook must invalidate it, or the site serves a stale render.
    notebook.write_text("x = 2\n", encoding="utf-8")
    assert not hooks._is_cached(output_dir, hooks._notebook_content_hash(notebook)), (
        "reused the export of an edited notebook"
    )


def test_notebook_cache_is_absent_without_examples(copie_session_minimal):
    """The caching code ships only where notebooks do."""
    hooks_source = (copie_session_minimal.project_dir / "docs" / "hooks.py").read_text(encoding="utf-8")
    assert "_notebook_content_hash" not in hooks_source, "notebook caching leaked into a no-examples project"
    assert "import hashlib" not in hooks_source, "hashlib imported with nothing to hash"


def _reset_gallery_caches(hooks):
    hooks._GALLERY_CACHE = None
    hooks._NOTEBOOK_API_USAGE_CACHE = None
    hooks._COMPANION_INDEX_CACHE = None
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None


def test_declared_api_references_override_imports(copie_session_default):
    """A declared api_references list wins over what the notebook imports."""
    project_dir = copie_session_default.project_dir
    _write_models_module(project_dir, "test_project")
    _write_notebook(
        project_dir,
        "declared_nb",
        '"title": "Declared", "description": "d", "category": "tutorial", "api_references": ["Beta"]',
        imports="from test_project.models import Alpha, Gamma\n",
    )
    hooks = _load_hooks(project_dir, "egl_declared")
    _reset_gallery_caches(hooks)

    usage = hooks._get_notebook_api_usage(project_dir)
    stems = {q: {i["stem"] for i in items} for q, items in usage.items()}

    assert "declared_nb" in stems.get("test_project.models.Beta", set()), "declared reference not used"
    assert "declared_nb" not in stems.get("test_project.models.Alpha", set()), "import won over declaration"
    assert "declared_nb" not in stems.get("test_project.models.Gamma", set()), "import won over declaration"


def test_absent_api_references_falls_back_to_imports(copie_session_default):
    """A notebook declaring nothing still gets cross-referenced.

    This is the day-one path: a fresh project has no metadata, and the feature
    must be visible before anyone opts in.
    """
    project_dir = copie_session_default.project_dir
    _write_models_module(project_dir, "test_project")
    _write_notebook(
        project_dir,
        "fallback_nb",
        '"title": "Fallback", "description": "d", "category": "tutorial"',
        imports="from test_project.models import Alpha\n",
    )
    hooks = _load_hooks(project_dir, "egl_fallback")
    _reset_gallery_caches(hooks)

    usage = hooks._get_notebook_api_usage(project_dir)
    stems = {i["stem"] for i in usage.get("test_project.models.Alpha", [])}

    assert "fallback_nb" in stems, "notebook without api_references was not inferred from imports"


def test_empty_api_references_means_no_pages(copie_session_default):
    """An empty list is a statement ('nowhere'), not an omission ('infer')."""
    project_dir = copie_session_default.project_dir
    _write_models_module(project_dir, "test_project")
    _write_notebook(
        project_dir,
        "optout_nb",
        '"title": "Optout", "description": "d", "category": "tutorial", "api_references": []',
        imports="from test_project.models import Alpha\n",
    )
    hooks = _load_hooks(project_dir, "egl_empty")
    _reset_gallery_caches(hooks)

    usage = hooks._get_notebook_api_usage(project_dir)
    appearances = {q for q, items in usage.items() if any(i["stem"] == "optout_nb" for i in items)}

    assert not appearances, f"api_references: [] still produced cards on {appearances}"


def test_unresolvable_api_reference_is_ignored(copie_session_default):
    """A declared name that resolves to nothing is dropped, not fatal."""
    project_dir = copie_session_default.project_dir
    _write_models_module(project_dir, "test_project")
    _write_notebook(
        project_dir,
        "bogus_nb",
        '"title": "Bogus", "description": "d", "category": "tutorial", "api_references": ["NotAThing", "Beta"]',
    )
    hooks = _load_hooks(project_dir, "egl_bogus")
    _reset_gallery_caches(hooks)

    usage = hooks._get_notebook_api_usage(project_dir)

    assert not [q for q in usage if "NotAThing" in q], "unresolvable name produced an entry"
    assert any(i["stem"] == "bogus_nb" for i in usage.get("test_project.models.Beta", [])), "valid name was dropped too"


def test_api_example_cards_are_capped(copie_session_default):
    """The card list is bounded, with the remainder reachable via the gallery."""
    project_dir = copie_session_default.project_dir
    # A symbol only this test references: the session project is shared, so
    # reusing one would let another test's notebooks into the card list.
    (project_dir / "src" / "test_project" / "capped.py").write_text(
        '"""Capped."""\n\n\nclass Capstone:\n    """Capstone."""\n', encoding="utf-8"
    )
    notebook_count = 9
    for i in range(notebook_count):
        _write_notebook(
            project_dir,
            f"capped_{i:02d}",
            f'"title": "Capped {i:02d}", "description": "d", "category": "tutorial", "api_references": ["Capstone"]',
        )
    hooks = _load_hooks(project_dir, "egl_cap")
    _reset_gallery_caches(hooks)

    html = hooks._build_api_examples_html(project_dir, "test_project.capped.Capstone")

    assert notebook_count > hooks._API_EXAMPLES_CAP, "test does not actually exceed the cap"
    assert html.count("**Capped") == hooks._API_EXAMPLES_CAP, "card list was not capped"
    assert "See all" in html and "in the gallery" in html, "no overflow link past the cap"
    # Stable order: same input, same cards, so builds are reproducible. The
    # caches must be cleared between calls -- re-reading a warm cache returns
    # the same object and the assertion cannot fail.
    _reset_gallery_caches(hooks)
    assert hooks._build_api_examples_html(project_dir, "test_project.capped.Capstone") == html


def test_api_example_cards_under_cap_have_no_gallery_link(copie_session_default):
    """Below the cap, nothing is hidden, so no overflow link is shown."""
    project_dir = copie_session_default.project_dir
    _write_models_module(project_dir, "test_project")
    _write_notebook(
        project_dir,
        "solo_nb",
        '"title": "Solo", "description": "d", "category": "tutorial", "api_references": ["Gamma"]',
    )
    hooks = _load_hooks(project_dir, "egl_undercap")
    _reset_gallery_caches(hooks)

    html = hooks._build_api_examples_html(project_dir, "test_project.models.Gamma")

    assert "**Solo**" in html
    assert "See all" not in html, "overflow link shown when nothing was hidden"


def test_companion_path_variants_match_same_page(copie_session_default):
    """companion is hand-written, so authored spellings must all match."""
    hooks = _load_hooks(copie_session_default.project_dir, "egl_norm")
    variants = [
        "/pages/how-to/x/",
        "pages/how-to/x",
        "pages/how-to/x.md",
        "/pages/how-to/x",
    ]
    normalized = {hooks._normalize_companion_path(v) for v in variants}
    assert len(normalized) == 1, f"companion path variants did not normalize together: {normalized}"


def test_companion_placeholder_renders_nothing_when_unmatched(copie_session_default):
    """A page with the placeholder and no companion notebooks renders empty."""
    project_dir = copie_session_default.project_dir
    hooks = _load_hooks(project_dir, "egl_nocompanion")
    _reset_gallery_caches(hooks)

    html = hooks._build_companion_cards_html(project_dir, "pages/how-to/nobody-references-me.md")

    assert html == "", "unmatched placeholder produced output"


def test_companion_cache_is_registered_by_name(copie_session_default):
    """The companion cache must carry the _CACHE suffix.

    The per-build reset's registration test discovers caches by that suffix, so
    a cache named otherwise (the natural `_COMPANION_INDEX`) is invisible to it
    and the stale-read bug returns silently.
    """
    hooks_source = (copie_session_default.project_dir / "docs" / "hooks.py").read_text(encoding="utf-8")
    assert "_COMPANION_INDEX_CACHE" in hooks_source, "companion cache does not follow the *_CACHE convention"


def test_gallery_features_absent_without_examples(copie_session_minimal):
    """The whole feature is gated behind include_examples."""
    hooks_source = (copie_session_minimal.project_dir / "docs" / "hooks.py").read_text(encoding="utf-8")
    for symbol in ("_COMPANION_INDEX_CACHE", "_API_EXAMPLES_CAP", "_build_companion_cards_html"):
        assert symbol not in hooks_source, f"{symbol} leaked into a project generated without examples"


def _mkdocs_config(project_dir):
    import yaml

    class _Loader(yaml.SafeLoader):
        pass

    _Loader.add_multi_constructor("tag:yaml.org,2002:python/name:", lambda loader, suffix, node: suffix)
    _Loader.add_constructor("!ENV", lambda loader, node: None)
    return yaml.load((project_dir / "mkdocs.yml").read_text(encoding="utf-8"), Loader=_Loader)


def test_snippets_resolve_docs_and_repo_root(copie_session_default):
    """base_path must reach the repo root as well as docs/.

    Narrowing this to [docs] breaks any project that includes a file from the
    repo root or src/ -- which real projects do.
    """
    config = _mkdocs_config(copie_session_default.project_dir)
    snippets = next(x["pymdownx.snippets"] for x in config["markdown_extensions"] if "pymdownx.snippets" in str(x))

    assert snippets["base_path"] == ["docs", "."], "base_path must search docs first, then the repo root"
    assert snippets["check_paths"] is True, "a missing include must fail the build, not vanish"


def test_changelog_include_resolves(copie_session_default):
    """The changelog page must actually render the changelog.

    A green build is not evidence here: without check_paths the include is
    dropped silently and the page renders as a heading with nothing under it.
    """
    import markdown

    project_dir = copie_session_default.project_dir
    page = project_dir / "docs" / "pages" / "reference" / "changelog.md"
    assert page.is_file(), "changelog page not generated"

    md = markdown.Markdown(
        extensions=["pymdownx.snippets"],
        extension_configs={"pymdownx.snippets": {"base_path": ["docs", "."], "check_paths": True}},
    )
    cwd = os.getcwd()
    try:
        os.chdir(project_dir)
        rendered = md.convert(page.read_text(encoding="utf-8"))
    finally:
        os.chdir(cwd)

    # Assert on text only the root CHANGELOG.md supplies. "Changelog" alone is a
    # word a page with no include at all would provide for free, so it cannot
    # fail for the defect this guards.
    assert "Keep a Changelog" in rendered, "root CHANGELOG.md content did not render -- the include resolved to nothing"
    assert "Semantic Versioning" in rendered, "changelog body missing"
    assert rendered.count("<h1") == 1, "changelog page renders a duplicate <h1> (own heading plus the include's)"


def test_python_inventory_configured(copie_session_default):
    """Signatures reference stdlib types, so that inventory earns its place."""
    config = _mkdocs_config(copie_session_default.project_dir)
    handler = next(p["mkdocstrings"] for p in config["plugins"] if isinstance(p, dict) and "mkdocstrings" in p)
    inventories = handler["handlers"]["python"]["inventories"]

    assert any("docs.python.org" in str(i) for i in inventories), "Python inventory not configured"


def test_quadrant_index_pages_exist_and_lead_nav(copie_session_default):
    """navigation.indexes is on, so each quadrant needs a landing page first."""
    project_dir = copie_session_default.project_dir
    config = _mkdocs_config(project_dir)

    for quadrant in ("tutorials", "how-to", "reference", "explanation"):
        assert (project_dir / "docs" / "pages" / quadrant / "index.md").is_file(), f"{quadrant}/index.md missing"

    sections = {k: v for entry in config["nav"] if isinstance(entry, dict) for k, v in entry.items()}
    for label, quadrant in (
        ("Tutorials", "tutorials"),
        ("How-to Guides", "how-to"),
        ("Reference", "reference"),
        ("Explanation", "explanation"),
    ):
        assert sections[label][0] == f"pages/{quadrant}/index.md", f"{label} nav must start with its index page"


def test_quadrant_indexes_are_local_owned(copie_session_default):
    """The template's skeleton must never overwrite a project's own landing page.

    Four of the seven repos generated from this template already maintain
    hand-written index pages; an update that replaces them is a regression
    shipped as an upgrade.
    """
    classification = (
        copie_session_default.project_dir
        / ".github"
        / "skills"
        / "update-from-template"
        / "references"
        / "file-classification.md"
    )
    if not classification.is_file():
        pytest.skip("update-from-template skill not shipped to generated projects")
    text = classification.read_text(encoding="utf-8")
    # Slice to the section end, not EOF: running to EOF would let a path
    # listed in a LATER section satisfy this assertion.
    start = text.index("## Tier 3")
    nxt = text.find("\n## ", start + 1)
    tier3 = text[start : nxt if nxt > 0 else len(text)]

    for quadrant in ("tutorials", "how-to", "reference", "explanation"):
        assert f"docs/pages/{quadrant}/index.md" in tier3, f"{quadrant}/index.md not listed as local-owned"


def _is_ignored(project_dir, path):
    """Whether git would ignore `path`, judged by the generated .gitignore itself."""
    result = subprocess.run(
        ["git", "check-ignore", "-q", path],
        cwd=project_dir,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _git_init(project_dir):
    """A throwaway repo, so `git check-ignore` has a worktree to answer against."""
    subprocess.run(["git", "init", "-q"], cwd=project_dir, capture_output=True, check=True)


def test_only_the_claude_skills_copy_is_tracked(copie):
    """.claude/skills is the tracked source of truth; the Copilot mirror is not.

    The two copies are byte-identical by design, so tracking both doubles every
    skill edit and its review. Judged with `git check-ignore` against the
    generated .gitignore rather than by reading it: the rule that matters is the
    one git actually applies, and this file's negation (`.claude/*` then
    `!.claude/skills/`) is exactly the kind that looks right and silently is not.
    """
    project_dir = copie.copy().project_dir
    _git_init(project_dir)

    assert not _is_ignored(project_dir, ".claude/skills/update-from-template/SKILL.md"), (
        ".claude/skills must be tracked -- it is the source of truth for the skills"
    )
    assert _is_ignored(project_dir, ".github/skills/update-from-template/SKILL.md"), (
        ".github/skills is a byte-identical mirror of .claude/skills and must not be tracked"
    )


def test_openspec_skills_are_never_tracked(copie):
    """openspec rewrites its own skills; they are tool state, not project content.

    The `!.claude/skills/` negation would otherwise pull them in, so this needs
    its own rule -- and needs testing, because the interaction between a
    negation and a later ignore is where this silently goes wrong.
    """
    project_dir = copie.copy().project_dir
    _git_init(project_dir)

    assert _is_ignored(project_dir, ".claude/skills/openspec-propose/SKILL.md"), (
        "an openspec skill under .claude/skills must stay untracked"
    )
    assert _is_ignored(project_dir, ".github/skills/openspec-review/SKILL.md"), (
        "an openspec skill under .github/skills must stay untracked"
    )
    # The rule must not swallow the skills the template does ship.
    assert not _is_ignored(project_dir, ".claude/skills/diataxis-howto-writer/SKILL.md"), (
        "the openspec rule is too broad -- it is hiding a template-shipped skill"
    )


def test_contribute_guide_carries_no_other_projects_domain(copie_session_default):
    """The notebook examples must not name another project's API.

    Every generated project gets this page. Examples written around one
    package's domain read as nonsense in the rest of the fleet -- a kedro plugin
    told to document `OptunaSearchCV` -- and quietly invite copying the wrong
    thing.
    """
    contribute = (copie_session_default.project_dir / "docs" / "pages" / "how-to" / "contribute.md").read_text(
        encoding="utf-8"
    )
    for foreign in ("OptunaSearchCV", "Optuna", "Hyperparameter Search", "sklearn_optuna"):
        assert foreign not in contribute, f"the contribute guide hardcodes another project's domain: {foreign!r}"


def test_project_branding_assets_are_local_owned(copie_session_default):
    """A project's logo and favicon must survive a template update.

    The template seeds placeholder branding, and a project replaces it with its
    own. These files are binary, so a template update overwrites them with no
    conflict and no signal -- the project's brand is silently reverted to the
    placeholder. Classifying them Tier 1 (template-managed) is what caused that;
    they belong in Tier 3. ``made_by_stateful-y.png`` is the exception: it is the
    template's own mark and stays Tier 1.
    """
    classification = (
        copie_session_default.project_dir
        / ".github"
        / "skills"
        / "update-from-template"
        / "references"
        / "file-classification.md"
    )
    if not classification.is_file():
        pytest.skip("update-from-template skill not shipped to generated projects")
    text = classification.read_text(encoding="utf-8")
    t3_start = text.index("## Tier 3")
    t3_end = text.find("\n## ", t3_start + 1)
    tier3 = text[t3_start : t3_end if t3_end > 0 else len(text)]
    t1_start = text.index("## Tier 1")
    t1_end = text.find("\n## ", t1_start + 1)
    tier1 = text[t1_start:t1_end]

    for asset in ("favicon.png", "logo.png", "logo_dark.png", "logo_light.png"):
        assert f"docs/assets/{asset}" in tier3, f"{asset} is not local-owned; a template update would overwrite it"
        assert f"docs/assets/{asset}" not in tier1, f"{asset} is still Tier 1 (template-managed)"
    # The template's own mark is genuinely template-managed.
    assert "docs/assets/made_by_stateful-y.png" in tier1, "the made-by mark should stay template-managed"


def _cache_names(hooks_module):
    return [n for n in vars(hooks_module) if n.endswith("_CACHE") and not n.startswith("__")]


@pytest.mark.parametrize(
    ("fixture_name", "expects_gallery"),
    [("copie_session_default", True), ("copie_session_minimal", False)],
)
def test_on_config_resets_every_cache(request, fixture_name, expects_gallery):
    """Sentinel round-trip: populate every cache, reset, assert all cleared.

    Deliberately not a presence check on the source. Asserting that the cache
    names appear in on_config's body passes even against an empty function, so
    it would verify nothing. Each variant is loaded under a unique module name:
    importing both under one name makes sys.modules return the first, and the
    second variant is never actually exercised.
    """
    project_dir = request.getfixturevalue(fixture_name).project_dir
    hooks = _load_hooks(project_dir, f"reset_{fixture_name}")

    names = _cache_names(hooks)
    assert names, "no *_CACHE globals discovered"
    assert ("_GALLERY_CACHE" in names) is expects_gallery, (
        f"gallery cache presence should follow include_examples; found {sorted(names)}"
    )

    sentinel = object()
    for name in names:
        setattr(hooks, name, sentinel)

    hooks.on_config({})

    still_set = [n for n in names if getattr(hooks, n) is sentinel]
    assert not still_set, f"on_config did not clear: {still_set}"


def test_on_config_returns_config(copie_session_default):
    """The mkdocs contract allows returning None, but the config is clearer."""
    hooks = _load_hooks(copie_session_default.project_dir, "reset_returns")
    config = {"marker": True}
    assert hooks.on_config(config) is config


def test_hooks_define_on_config_not_on_startup(copie_session_default):
    """on_startup runs once per invocation, so a reset there never fires again.

    That is the bug this change exists to fix; defining it would reintroduce it.
    """
    source = (copie_session_default.project_dir / "docs" / "hooks.py").read_text(encoding="utf-8")
    assert "def on_config(" in source, "no per-build reset"
    assert "def on_startup(" not in source, "on_startup fires once per invocation, not per build"


def test_no_phantom_cache_without_examples(copie_session_minimal):
    """The reset must not name caches a project does not define.

    `global X; X = None` creates the binding rather than raising, so an
    ungated reset silently grows module attributes nothing reads -- and the
    discovery test would then dutifully confirm they are cleared.
    """
    hooks = _load_hooks(copie_session_minimal.project_dir, "reset_phantom")
    hooks.on_config({})

    for gallery_cache in ("_GALLERY_CACHE", "_COMPANION_INDEX_CACHE", "_NOTEBOOK_API_USAGE_CACHE"):
        assert not hasattr(hooks, gallery_cache), f"{gallery_cache} phantom-created in a no-examples project"


def test_shipped_skill_mirrors_are_byte_identical(copie_session_default):
    """The two shipped skill trees must not drift.

    .github/skills and .claude/skills are hand-maintained duplicates: Copilot
    reads one, Claude Code reads the other. Comparing directory names only
    (the previous check) passes while their contents diverge, so an edit to one
    copy ships a stale other -- and inside a generated project it is the
    .claude copy that Claude Code actually loads.
    """
    project_dir = copie_session_default.project_dir
    gh, cl = project_dir / ".github" / "skills", project_dir / ".claude" / "skills"
    if not (gh.is_dir() and cl.is_dir()):
        pytest.skip("skills not shipped to generated projects")

    gh_files = {p.relative_to(gh): p for p in gh.rglob("*") if p.is_file()}
    cl_files = {p.relative_to(cl): p for p in cl.rglob("*") if p.is_file()}

    assert set(gh_files) == set(cl_files), "shipped skill trees have different files"
    drifted = [str(rel) for rel, p in gh_files.items() if p.read_bytes() != cl_files[rel].read_bytes()]
    assert not drifted, f"shipped skill copies have drifted: {drifted}"


def test_see_also_links_list_form_entries(copie_session_minimal):
    """Entries written as a markdown list link too.

    numpydoc renders See Also as a paragraph, but authors also write the
    entries as a list, which renders as <li> rather than <p>. Handling only
    paragraphs silently drops links for every list-style docstring.
    """
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "seealso_list")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    html = (
        '<h2 id="minimal_project.Alpha">Alpha</h2><div class="doc doc-contents">'
        '<details class="see-also" open><summary>See Also</summary>'
        "<ul><li>Beta : A list entry.</li></ul></details></div>"
        '<div class="doc doc-children"></div>'
    )
    out = hooks.on_page_content(html, _generated_page("minimal_project", "Alpha"), {}, None)

    assert '<a href="../minimal_project.models.Beta/">Beta</a>' in out, "list-form entry was not linked"


def test_see_also_leaves_explicit_cross_references_alone(copie_session_minimal):
    """An author's explicit [Name][target] reference is not rewritten.

    autorefs turns explicit references into <autoref>/<a> before this hook runs
    and resolves them later. Rewriting them would double-link, and the author
    has already said exactly what they mean.
    """
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "seealso_explicit")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    inner = '<li><autoref identifier="minimal_project.models.Beta"><code>Beta</code></autoref> : Explicit.</li>'
    html = (
        '<h2 id="minimal_project.Alpha">Alpha</h2><div class="doc doc-contents">'
        f'<details class="see-also" open><summary>See Also</summary><ul>{inner}</ul></details></div>'
        '<div class="doc doc-children"></div>'
    )
    out = hooks.on_page_content(html, _generated_page("minimal_project", "Alpha"), {}, None)

    assert inner in out, "an explicit cross-reference was rewritten"
    assert out.count("minimal_project.models.Beta") == 1, "explicit reference was double-linked"


def test_reexported_members_render_in_the_api_page_table(copie_session_minimal):
    """The change's observable fix: the members TABLE is non-empty.

    Asserting that _get_public_members returns entries is not this. A lookup can
    resolve every symbol while the rendered page stays empty -- the per-member
    detail pages are written from a separate code path, so the interlock test
    passes too. This asserts the rendered markdown a reader actually sees, and
    fails if _build_members_tables stops emitting rows.
    """
    project_dir = copie_session_minimal.project_dir
    _write_reexport_package(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "table_render")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    hooks._generate_api_pages(project_dir)
    page = (project_dir / "docs" / "pages" / "api" / "shapes.md").read_text(encoding="utf-8")

    assert "### Classes" in page, "members table missing its Classes heading"
    assert "Circle" in page, "re-exported class absent from the rendered members table"
    assert "A round shape." in page, "row is missing the description lifted from the declaring module"
    assert "generated/minimal_project.shapes.Circle.md" in page, "row does not link to the member page"


def test_api_name_lookup_prefers_the_published_path(copie_session_minimal):
    """One symbol reachable by two paths resolves to the one users write."""
    project_dir = copie_session_minimal.project_dir
    (project_dir / "src" / "minimal_project" / "naive.py").write_text(
        '"""Naive."""\n\n\nclass SeasonalNaive:\n    """Repeat last season."""\n', encoding="utf-8"
    )
    pub = project_dir / "src" / "minimal_project" / "point"
    pub.mkdir(parents=True, exist_ok=True)
    (pub / "__init__.py").write_text(
        '"""Point."""\n\nfrom minimal_project.naive import SeasonalNaive\n\n__all__ = ["SeasonalNaive"]\n',
        encoding="utf-8",
    )
    hooks = _load_hooks(project_dir, "prefer_public")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    lookup = hooks._get_api_name_lookup(project_dir)

    assert lookup.get("SeasonalNaive") == "minimal_project.point.SeasonalNaive", (
        f"published path not preferred; got {lookup.get('SeasonalNaive')!r}"
    )


def test_api_name_lookup_refuses_a_genuine_collision(copie_session_minimal):
    """Two different symbols sharing a short name resolve to nothing.

    A wrong link is worse than no link, so an ambiguous name degrades to plain
    text rather than pointing at whichever module happened to be scanned last.
    """
    project_dir = copie_session_minimal.project_dir
    for mod in ("dup_a", "dup_b"):
        (project_dir / "src" / "minimal_project" / f"{mod}.py").write_text(
            f'"""{mod}."""\n\n\nclass Duplicated:\n    """From {mod}."""\n', encoding="utf-8"
        )
    hooks = _load_hooks(project_dir, "collision")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    lookup = hooks._get_api_name_lookup(project_dir)

    assert "Duplicated" not in lookup, (
        f"an ambiguous short name resolved to {lookup.get('Duplicated')!r} instead of being refused"
    )


def test_gallery_overflow_link_targets_the_real_gallery_page(copie_session_default):
    """The overflow link resolves to wherever the gallery page actually is.

    The gallery page is local-owned, so a project may move it; a hardcoded path
    404s silently. It is located by the <!-- GALLERY --> placeholder instead.
    """
    project_dir = copie_session_default.project_dir
    hooks = _load_hooks(project_dir, "gallery_url")
    hooks._GALLERY_PAGE_CACHE = None

    url = hooks._get_gallery_page_url(project_dir)

    assert url, "gallery page not found by its GALLERY placeholder"
    page = project_dir / "docs" / (url.strip("/") + ".md")
    assert page.is_file(), f"overflow link {url} points at a page that does not exist"
    assert "<!-- GALLERY -->" in page.read_text(encoding="utf-8"), "located page is not the gallery"


def test_see_also_leaves_description_text_alone(copie_session_minimal):
    """A colon-terminated word in an entry's DESCRIPTION is not linked.

    Entry names sit at the start of their line. Without anchoring there, any
    "Word:" in prose is treated as another entry -- so "Target : Note: see
    below" linkifies "Note", rewriting text the spec says is left unchanged.
    """
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    # A class whose name also appears, colon-terminated, inside a description.
    (project_dir / "src" / "minimal_project" / "prose.py").write_text(
        '"""Prose."""\n\n\nclass Note:\n    """Named Note."""\n', encoding="utf-8"
    )
    hooks = _load_hooks(project_dir, "seealso_desc")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    html = _see_also_page("minimal_project", "Alpha", "Beta : Note: a colon-terminated word in the description.")
    out = hooks.on_page_content(html, _generated_page("minimal_project", "Alpha"), {}, None)

    assert '<a href="../minimal_project.models.Beta/">Beta</a>' in out, "the entry name was not linked"
    assert not re.search(r"<a[^>]*>Note</a>", out), "a word in the description was linkified as an entry"
    assert "Note: a colon-terminated word in the description." in out, "description text was altered"


def test_docs_watch_includes_package_source(copie_session_default):
    """`mkdocs serve` must rebuild when the package source changes.

    The API pages are generated from src/, so without it in `watch` an author
    adding a class sees nothing until they restart the server -- which is the
    scenario the per-build cache reset exists to satisfy.
    """
    config = _mkdocs_config(copie_session_default.project_dir)
    assert "src" in config["watch"], f"src not watched; serve will not rebuild on source edits: {config['watch']}"


def test_see_also_does_not_linkify_names_outside_the_section(copie_session_minimal):
    """A symbol name elsewhere on the page is left alone.

    Symbol names appear throughout rendered docs -- in Notes, parameter tables,
    source listings. Scoping to the See Also block is what stops the linkifier
    rewriting all of them.
    """
    project_dir = copie_session_minimal.project_dir
    _write_models_module(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "seealso_scope_name")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    html = (
        '<h2 id="minimal_project.Alpha">Alpha</h2><div class="doc doc-contents">'
        "<h3>Notes</h3><p>Beta : mentioned in prose, not a See Also entry.</p>"
        '<details class="see-also" open><summary>See Also</summary><p>Gamma : A real entry.</p></details>'
        '</div><div class="doc doc-children"></div>'
    )
    out = hooks.on_page_content(html, _generated_page("minimal_project", "Alpha"), {}, None)

    assert '<a href="../minimal_project.models.Gamma/">Gamma</a>' in out, "the See Also entry was not linked"
    assert not re.search(r"<a[^>]*>Beta</a>", out), "a name outside the See Also section was linkified"


def test_companion_card_renders_with_resolved_links(copie_session_default):
    """The primary companion path: a card with working links, end to end.

    The cards are emitted as markdown so the [View]/[Open in marimo] rewrites
    below them resolve the URLs. Emitting resolved HTML instead would bypass
    those rewrites and ship literal placeholders -- which is why this asserts
    the rendered hrefs, not just that a card appeared.
    """
    project_dir = copie_session_default.project_dir
    _write_notebook(
        project_dir,
        "companion_nb",
        '"title": "Companion NB", "description": "Demo.", "category": "how-to",'
        ' "companion": "pages/how-to/configure.md"',
    )
    hooks = _load_hooks(project_dir, "companion_render")
    _reset_gallery_caches(hooks)

    page = _FakePage("pages/how-to/configure.md", "pages/how-to/configure/index.html")
    config = {"repo_url": "https://github.com/s/p"}
    out = hooks.on_page_markdown("<!-- COMPANION_NOTEBOOKS -->", page, config, None)

    assert "COMPANION_NOTEBOOKS" not in out, "placeholder was not consumed"
    assert "## Try it interactively" in out, "heading not emitted with the cards"
    assert "Companion NB" in out, "companion card did not render"
    # pages/how-to/configure.md is three deep, so the rewrite prefixes ../../../
    assert "](../../../examples/companion_nb/" in out, f"View link not resolved to a relative path: {out[:200]}"
    assert "marimo.app" in out, "Open-in-marimo link not resolved to a playground URL"
    assert "](/examples/" not in out, "an unresolved absolute example path survived"


def test_changelog_page_has_a_populated_toc(copie_session_default):
    """The changelog is the page that most needs a ToC.

    Material's ToC partial takes first.children when the first heading is level
    1, so a page with two h1s renders an empty ToC -- silently, on the one page
    with a heading per release.
    """
    import markdown

    project_dir = copie_session_default.project_dir
    page = project_dir / "docs" / "pages" / "reference" / "changelog.md"
    md = markdown.Markdown(
        extensions=["pymdownx.snippets", "toc"],
        extension_configs={"pymdownx.snippets": {"base_path": ["docs", "."], "check_paths": True}},
    )
    cwd = os.getcwd()
    try:
        os.chdir(project_dir)
        md.convert(page.read_text(encoding="utf-8"))
    finally:
        os.chdir(cwd)

    tokens = md.toc_tokens
    assert tokens, "changelog page produced no table of contents"
    assert len([t for t in tokens if t["level"] == 1]) == 1, "more than one level-1 heading collapses Material's ToC"


def test_reexported_symbols_appear_in_the_api_index(copie_session_minimal):
    """The searchable API index lists re-exported symbols too.

    The index, the package pages and the name lookup must all be fed by the
    same member scan. Feeding the index from a scan that cannot see re-exports
    leaves it blind to exactly the symbols this resolution exists to surface:
    their pages exist and the lookup resolves them, while the index shows
    nothing.
    """
    project_dir = copie_session_minimal.project_dir
    _write_reexport_package(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "api_index")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    prefix = hooks._site_root_prefix(_FakePage("pages/reference/api.md", "pages/reference/api/index.html"))
    html = hooks._build_api_table_html(project_dir, prefix)

    assert "Circle" in html, "re-exported class absent from the searchable API index"
    assert "area" in html, "re-exported function absent from the searchable API index"

    # From pages/reference/api/, three levels reach the site root, then down to
    # pages/api/. Get this wrong and the table still renders fully populated
    # while every link 404s -- mkdocs does not validate hook-injected raw HTML.
    assert '<a href="../../../pages/api/generated/minimal_project.shapes.Circle/">' in html, (
        "symbol link does not resolve from pages/reference/api/ to the generated page"
    )
    assert '<a href="../../../pages/api/shapes/">' in html, (
        "module link does not resolve from pages/reference/api/ to the submodule page"
    )


@pytest.mark.parametrize(
    ("src_path", "dest_path", "prefix"),
    [
        ("pages/reference/api.md", "pages/reference/api/index.html", "../../../"),
        ("pages/api/index.md", "pages/api/index.html", "../../"),
    ],
)
def test_api_index_links_resolve_wherever_the_index_lives(copie_session_minimal, src_path, dest_path, prefix):
    """The API table's links work from any page the index is placed on.

    The template seeds the index at pages/reference/api.md, but a project may
    move it -- yohou keeps it at pages/api/index.md, one level shallower. A
    hardcoded `../../` is right for the seeded location and silently 404s every
    one of the other's links: the table renders fully populated, and mkdocs
    cannot catch it because it does not validate raw HTML injected by a hook.

    So the prefix is derived from the page, and this checks both layouts by
    resolving each href against the page's own URL -- the arithmetic is the
    whole point, and asserting on a literal string would just restate it.
    """
    project_dir = copie_session_minimal.project_dir
    _write_reexport_package(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, f"api_index_{src_path.count('/')}_{len(prefix)}")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    page = _FakePage(src_path, dest_path)
    assert hooks._site_root_prefix(page) == prefix

    html = hooks._build_api_table_html(project_dir, hooks._site_root_prefix(page))
    hrefs = re.findall(r'<a href="([^"]+)"', html)
    assert hrefs, "the API table emitted no links at all"

    page_dir = posixpath.dirname(dest_path)
    for href in hrefs:
        resolved = posixpath.normpath(posixpath.join(page_dir, href))
        assert resolved.startswith("pages/api/"), (
            f"from {dest_path}, href {href!r} resolves to {resolved!r} -- outside pages/api/, so it 404s"
        )


def _write_dependency_shim(project_dir, package_name):
    """A plain module whose public API is re-exported from outside the package.

    Uses stdlib modules as the "dependency": they are outside the generated
    package exactly as a third-party one is, and they are always installed, so
    the test does not depend on the resolver finding some optional extra.
    """
    pkg = project_dir / "src" / package_name
    (pkg / "shim.py").write_text(
        '"""Convenience re-exports."""\n\n'
        "from dataclasses import dataclass\n"
        "from fractions import Fraction\n\n"
        '__all__ = ["Fraction", "dataclass"]\n',
        encoding="utf-8",
    )
    (pkg / "helpers.py").write_text(
        '"""Helpers."""\n\n\nclass Helper:\n    """A helper."""\n',
        encoding="utf-8",
    )
    # A plain module with no __all__ importing a sibling for its own use. The
    # import is IN-package, so it resolves -- nothing but the missing __all__
    # keeps it out of the API. An out-of-package import would not test this:
    # the external resolver already refuses to run without __all__.
    (pkg / "internal.py").write_text(
        '"""Uses a helper; exports nothing."""\n\n'
        "from .helpers import Helper\n\n\n"
        "def ratio():\n"
        '    """Build a helper."""\n'
        "    return Helper()\n",
        encoding="utf-8",
    )
    return pkg


def test_dependency_reexports_stay_in_the_api(copie_session_minimal):
    """A name re-exported from a dependency and named in __all__ is public API.

    A convenience shim (``from otherpkg import Widget`` under this package's
    ``__all__``) declares nothing itself and its source lives outside the
    package, so resolution that only follows in-package imports drops the name
    entirely: gone from the index, and no page. Measured on a real project, that
    silently removed three of its four public symbols and rendered its module
    page as a bare docstring.

    The kind and docstring must come from the declaring module rather than being
    guessed, so a class stays a class and carries its real summary.
    """
    project_dir = copie_session_minimal.project_dir
    pkg = _write_dependency_shim(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "depshim")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    members = hooks._get_public_members(pkg / "shim.py", pkg)

    assert {e["name"] for e in members["classes"]} == {"Fraction"}, "a re-exported dependency class was dropped"
    assert {e["name"] for e in members["functions"]} == {"dataclass"}, "a re-exported dependency function was dropped"
    fraction = next(e for e in members["classes"] if e["name"] == "Fraction")
    assert fraction["doc"], "the docstring was not read from the declaring module"
    assert fraction["reexported"] is True


def test_plain_module_imports_are_not_api_without_dunder_all(copie_session_minimal):
    """Without __all__, a plain module's imports stay private.

    Re-export resolution is not limited to __init__.py, because a plain module
    can be a shim. That generality is what makes this necessary: in an ordinary
    module an import is a private detail (imported to be *used*), and treating it
    as API would publish every helper a module happens to import.

    The import here is in-package on purpose. It resolves, so only the absent
    __all__ stands between it and the API -- an out-of-package import would pass
    this test without exercising anything, since the external resolver already
    refuses to run without __all__.
    """
    project_dir = copie_session_minimal.project_dir
    pkg = _write_dependency_shim(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "depshim_internal")
    hooks._API_NAME_LOOKUP_CACHE = None
    hooks._SUBMODULE_CACHE = None

    members = hooks._get_public_members(pkg / "internal.py", pkg)
    names = {e["name"] for e in members["classes"] + members["functions"]}

    assert "ratio" in names, "the module's own function is missing"
    assert "Helper" not in names, "a sibling imported for internal use leaked into the API without __all__"


def test_third_party_import_rejected_without_dunder_all(copie_session_minimal):
    """Without __all__, the package-root guard is what excludes stdlib imports.

    The __all__-bearing fixture cannot show this: the filter rejects Path before
    the guard is consulted. This exercises the guard itself.
    """
    project_dir = copie_session_minimal.project_dir
    pkg = _write_reexport_package(project_dir, "minimal_project")
    hooks = _load_hooks(project_dir, "noall")

    members = hooks._get_public_members(pkg / "noall" / "__init__.py", pkg)
    names = {e["name"] for e in members["classes"] + members["functions"]}

    assert "Gadget" in names, "first-party re-export not resolved without __all__"
    assert "Path" not in names, "a stdlib import was resolved as package API"


def test_companion_placeholder_renders_no_dangling_heading(copie_session_default):
    """A page with no matching notebooks renders nothing -- not a bare heading.

    The heading is emitted with the cards rather than written into the page, so
    removing a notebook's companion cannot leave an empty section behind.
    """
    project_dir = copie_session_default.project_dir
    hooks = _load_hooks(project_dir, "companion_empty")
    _reset_gallery_caches(hooks)

    page = _FakePage("pages/how-to/troubleshooting.md", "pages/how-to/troubleshooting/index.html")
    out = hooks.on_page_markdown("<!-- COMPANION_NOTEBOOKS -->", page, {"repo_url": "https://github.com/s/p"}, None)

    assert out.strip() == "", f"an unmatched placeholder left content behind: {out!r}"


_CLASSIFICATION_PATTERNS = (
    "src/",
    "tests/",
    "examples/",
    "docs/examples/",
    ".github/skills/",
    ".claude/skills/",
)


def _unclassified_files(project_dir, package_name):
    """Generated files that the update classification does not cover."""
    classification = (
        project_dir / ".github" / "skills" / "update-from-template" / "references" / "file-classification.md"
    ).read_text(encoding="utf-8")
    missing = []
    for path in sorted(project_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(project_dir).as_posix()
        if rel.startswith(".git/"):
            continue
        # Pattern entries (src/<package_name>/**, tests/**, ...) cover whole
        # trees; requiring a line per file there would be unmaintainable in the
        # opposite direction.
        if rel.startswith(_CLASSIFICATION_PATTERNS) or rel.startswith(f"src/{package_name}/"):
            continue
        if rel not in classification:
            missing.append(rel)
    return missing


@pytest.mark.parametrize("include_examples", [True, False])
def test_every_generated_file_is_classified(copie, include_examples):
    """Every file the template ships has an update tier.

    The classification tells whoever resolves an update conflict whether the
    template's version or the project's wins. A file with no tier gives them no
    rule at the moment they most need one -- and the list is maintained by hand,
    so nothing notices a new file arriving without an entry. That is how two
    shipped pages went unclassified, one of which a real update wanted to strip
    212 lines from.

    Generates a fresh project rather than reusing a session fixture: this asks
    what the TEMPLATE ships, and a shared fixture accumulates build artifacts
    (.nox, __pycache__, generated API pages) from whichever tests ran first.

    Both include_examples values run: a file behind that gate ships in only one
    variant.
    """
    result = copie.copy(extra_answers={"include_examples": include_examples})
    project_dir = result.project_dir
    missing = _unclassified_files(project_dir, "test_project")

    assert not missing, (
        f"these generated files have no update tier, so a conflict on them has no resolution rule: {missing}"
    )


@pytest.mark.parametrize("include_examples", [True, False])
def test_generated_project_is_ruff_format_clean(copie, include_examples):
    """A freshly generated project passes ``ruff format --check``.

    The template's Python is authored in ``.jinja`` files, which ruff does not
    recognise as Python and never formats in this repo. So unformatted code can
    ship, and because the generated ``pyproject.toml`` enables preview-style
    formatting, a generated project's first ``pre-commit run`` reformats
    template-owned files (``docs/hooks.py`` chief among them) and reds its CI on
    arrival -- the fix then drifts the file from the template, guaranteeing a
    conflict at the next update. This checks the emitted code, not the code the
    template happens to be.

    Both include_examples values run: the gallery hooks ship in only one variant,
    so a formatting slip behind that gate is invisible to the other.

    Runs ruff via the project's own config (discovered from its pyproject.toml),
    so the check matches what the project would run.
    """
    ruff = shutil.which("ruff")
    if ruff is None:
        pytest.skip("ruff is not installed in the test environment")

    result = copie.copy(extra_answers={"include_examples": include_examples})
    project_dir = result.project_dir

    check = subprocess.run(
        [ruff, "format", "--check", "."],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    diff = subprocess.run(
        [ruff, "format", "--check", "--diff", "."],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check.returncode == 0, (
        "the template ships Python that ruff would reformat, so a generated "
        f"project's first `pre-commit run` reds CI:\n{diff.stdout}{check.stdout}{check.stderr}"
    )


@pytest.mark.parametrize("include_examples", [True, False])
def test_generated_project_passes_ruff_check(copie, include_examples):
    """A freshly generated project passes ``ruff check``.

    The format guard above is not enough: it proved the template's Python is
    *shaped* right, while nothing checked whether it *lints*. A class-based hook
    shipped with three ARG002 violations under exactly that blind spot, and every
    generated project without a local ARG002 ignore failed its first
    `pre-commit run` -- the same failure the format guard exists to prevent,
    through the other half of the same door.

    Runs ruff with the project's own config, so this is what the project runs.
    """
    ruff = shutil.which("ruff")
    if ruff is None:
        pytest.skip("ruff is not installed in the test environment")

    result = copie.copy(extra_answers={"include_examples": include_examples})
    check = subprocess.run(
        [ruff, "check", "--force-exclude", "--no-fix", "."],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check.returncode == 0, (
        "the template ships Python that fails `ruff check`, so a generated "
        f"project's first `pre-commit run` reds CI:\n{check.stdout}{check.stderr}"
    )


def test_update_guidance_restores_local_owned_files(copie_session_default):
    """The local-owned remedy must restore, not merely discard the rejection.

    A rejected-hunks update applies every hunk that applies and rejects only the
    rest, so a conflicted file is already partially updated. Guidance that treats
    the rejection's presence as evidence the file is untouched leads to keeping
    the template's changes in a file the project owns -- silently, with the
    update reporting success. Measured once: a local-owned page went 184 lines to
    78.
    """
    skill_dir = copie_session_default.project_dir / ".github" / "skills" / "update-from-template"
    if not skill_dir.is_dir():
        pytest.skip("update-from-template skill not shipped to generated projects")
    skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    conflicts = (skill_dir / "references" / "conflict-resolution.md").read_text(encoding="utf-8")

    assert "git checkout HEAD -- <file>" in skill, "the local-owned remedy does not restore the project's version"
    assert "Delete `.rej` without applying" not in skill, (
        "the local-owned remedy discards the rejection without undoing the hunks that already applied"
    )
    for wrong in ("Keeps local file intact", "local file is clean", "local file** unchanged"):
        assert wrong not in conflicts, f"the guidance still claims a conflicted file is untouched: {wrong!r}"
