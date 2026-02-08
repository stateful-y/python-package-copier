"""Tests for the copier template."""

import pytest


def test_template_creates_project(copie):
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

    result = copie.copy()

    assert result.exit_code == 0, result.exception
    assert result.exception is None
    assert result.project_dir.is_dir()

    for path in expected_files:
        assert (result.project_dir / path).is_file(), f"Missing file: {path}"

    for path in expected_dirs:
        assert (result.project_dir / path).is_dir(), f"Missing directory: {path}"

    # git-cliff config should be included with GitHub Actions
    assert (result.project_dir / ".git-cliff.toml").is_file()


def test_readthedocs_config_included(copie):
    """Test that ReadTheDocs config is always included."""
    result = copie.copy()

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


def test_generated_project_structure(copie):
    """Test that the generated project has the correct structure."""
    result = copie.copy()

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
    assert (docs_dir / "pages" / "contributing.md").is_file()

    # Check GitHub workflows
    workflows_dir = result.project_dir / ".github" / "workflows"
    assert (workflows_dir / "tests.yml").is_file()
    assert (workflows_dir / "changelog.yml").is_file()
    assert (workflows_dir / "publish-release.yml").is_file()
    assert (workflows_dir / "nightly.yml").is_file()


def test_generated_pyproject_uses_correct_tools(copie):
    """Test that the generated pyproject.toml uses the correct tools."""
    result = copie.copy()

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

    # nox should NOT be in pyproject.toml - it's installed globally via uvx
    assert "nox" not in content, "nox should not be in pyproject.toml (install globally with uvx)"


def test_pyproject_has_interrogate_config(copie):
    """Test that pyproject.toml includes interrogate configuration."""
    result = copie.copy()

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


def test_noxfile_configuration(copie):
    """Test that noxfile is properly configured."""
    result = copie.copy()

    noxfile_path = result.project_dir / "noxfile.py"
    assert noxfile_path.is_file()

    content = noxfile_path.read_text(encoding="utf-8")

    # Check for uv backend
    assert 'default_venv_backend = "uv|virtualenv"' in content

    # Check for ty
    assert "ty" in content, "ty not found in noxfile.py"


def test_precommit_configuration(copie):
    """Test that pre-commit config is properly set up."""
    result = copie.copy()

    precommit_path = result.project_dir / ".pre-commit-config.yaml"
    assert precommit_path.is_file()

    content = precommit_path.read_text(encoding="utf-8")

    # Check for ruff
    assert "ruff-pre-commit" in content or "ruff" in content

    # Check for ty
    assert "ty" in content, "ty not found in pre-commit config"

    # Check for commitizen
    assert "commitizen" in content, "commitizen not found in pre-commit config"


def test_precommit_interrogate_checks_only_src(copie):
    """Test that interrogate pre-commit hook only checks src/ directory."""
    result = copie.copy()

    precommit_path = result.project_dir / ".pre-commit-config.yaml"
    assert precommit_path.is_file()

    content = precommit_path.read_text(encoding="utf-8")

    # Should have interrogate configured to check only src/
    assert "interrogate" in content
    assert "files: ^src/" in content
    assert r"exclude: .*_version\.py$" in content


def test_precommit_ty_uses_uv_run(copie):
    """Test that ty pre-commit hook uses uv run with proper configuration."""
    result = copie.copy()

    precommit_path = result.project_dir / ".pre-commit-config.yaml"
    assert precommit_path.is_file()

    content = precommit_path.read_text(encoding="utf-8")

    # Should have ty configured with uv run
    assert "id: ty" in content
    assert "entry: uv run ty check src" in content
    assert "pass_filenames: false" in content


def test_github_workflows(copie):
    """Test that GitHub workflows are properly configured."""
    result = copie.copy()

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

    # Check PR title validation workflow
    pr_title_workflow = result.project_dir / ".github" / "workflows" / "pr-title.yml"
    assert pr_title_workflow.is_file(), "PR title validation workflow not found"

    pr_title_content = pr_title_workflow.read_text(encoding="utf-8")
    assert "amannn/action-semantic-pull-request" in pr_title_content
    assert "feat" in pr_title_content
    assert "fix" in pr_title_content
    assert "docs" in pr_title_content


def test_release_workflow(copie):
    """Test that release workflow includes changelog automation."""
    result = copie.copy()

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


def test_commitizen_configuration(copie):
    """Test that commitizen is properly configured."""
    result = copie.copy()

    pyproject_path = result.project_dir / "pyproject.toml"
    assert pyproject_path.is_file()

    content = pyproject_path.read_text(encoding="utf-8")

    # Check for commitizen configuration
    assert "[tool.commitizen]" in content, "commitizen config not found in pyproject.toml"
    assert "cz_conventional_commits" in content, "conventional commits not configured"


def test_git_cliff_configuration(copie):
    """Test that git-cliff configuration exists."""
    result = copie.copy()

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

    # Check pyproject.toml contains doctest configuration
    pyproject_content = (result.project_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.pytest.ini_options.doctest]" in pyproject_content
    assert "--doctest-modules" in pyproject_content
    assert "--doctest-continue-on-failure" in pyproject_content

    # Check noxfile has test_docstrings session
    noxfile_content = (result.project_dir / "noxfile.py").read_text(encoding="utf-8")
    assert "def test_docstrings(session:" in noxfile_content
    assert '"--doctest-modules"' in noxfile_content

    # Check justfile has test-docstrings command
    justfile_content = (result.project_dir / "justfile").read_text(encoding="utf-8")
    assert "test-docstrings:" in justfile_content
    assert "--doctest-modules" in justfile_content

    # Check hello.py has docstring examples
    hello_py = (result.project_dir / "src" / "test_project" / "hello.py").read_text(encoding="utf-8")
    assert "Examples:" in hello_py
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

    # Check examples.md exists and mentions standalone notebooks
    examples_md = result.project_dir / "docs" / "pages" / "examples.md"
    assert examples_md.is_file(), "docs/pages/examples.md not created"
    examples_content = examples_md.read_text(encoding="utf-8")
    assert "## Interactive Demo" in examples_content
    assert "/examples/hello/" in examples_content

    # Check mkdocs.yml includes examples in nav and has exclude_docs
    mkdocs_content = (result.project_dir / "mkdocs.yml").read_text(encoding="utf-8")
    assert "Examples: pages/examples.md" in mkdocs_content
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
    contributing_content = (result.project_dir / "docs" / "pages" / "contributing.md").read_text(encoding="utf-8")
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
    examples_md = result.project_dir / "docs" / "examples.md"
    if examples_md.exists():
        content = examples_md.read_text(encoding="utf-8").strip()
        assert content == "", (
            f"docs/examples.md should be empty when examples are disabled, but contains: {content[:100]}"
        )

    # Check mkdocs.yml doesn't include examples in nav
    mkdocs_content = (result.project_dir / "mkdocs.yml").read_text(encoding="utf-8")
    assert "Examples: examples.md" not in mkdocs_content

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
    expected_md_files = ["index.md", "getting-started.md", "user-guide.md", "api-reference.md"]
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
    examples_md = result.project_dir / "docs" / "pages" / "examples.md"
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
def test_generated_tests_pass(copie):
    """Smoke test: run the generated project's tests via nox.

    This validates:
    - Generated test files are syntactically correct
    - Tests can be discovered and executed
    - Test infrastructure (pytest, fixtures) works
    """
    import subprocess

    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0

    # Run tests via nox (single Python version for speed)
    test_result = subprocess.run(
        ["uvx", "nox", "-s", "test_coverage"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )

    assert test_result.returncode == 0, (
        f"Generated tests failed:\nSTDOUT:\n{test_result.stdout}\n\nSTDERR:\n{test_result.stderr}"
    )


@pytest.mark.integration
@pytest.mark.slow
def test_lint_session_passes(copie):
    """Smoke test: run lint session to validate code quality tools work.

    This validates:
    - ruff configuration is correct
    - ty type checker works
    - Generated code passes linting and type checking
    """
    import subprocess

    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0

    # Run lint session
    lint_result = subprocess.run(
        ["uvx", "nox", "-s", "lint"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert lint_result.returncode == 0, (
        f"Lint session failed:\nSTDOUT:\n{lint_result.stdout}\n\nSTDERR:\n{lint_result.stderr}"
    )


@pytest.mark.integration
@pytest.mark.slow
def test_doctest_session_passes(copie):
    """Smoke test: run test_docstrings session to validate docstring examples.

    This validates:
    - Docstring examples are syntactically correct
    - Example code in docstrings executes successfully
    """
    import subprocess

    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0

    # Run test_docstrings session
    doctest_result = subprocess.run(
        ["uvx", "nox", "-s", "test_docstrings"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert doctest_result.returncode == 0, (
        f"Doctest session failed:\nSTDOUT:\n{doctest_result.stdout}\n\nSTDERR:\n{doctest_result.stderr}"
    )


@pytest.mark.integration
@pytest.mark.slow
def test_build_docs_session_passes(copie):
    """Smoke test: run build_docs session to validate documentation builds.

    This validates:
    - mkdocs configuration is correct
    - Documentation dependencies are installed
    - Documentation can be built successfully
    """
    import subprocess

    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0

    # Run build_docs session
    docs_result = subprocess.run(
        ["uvx", "nox", "-s", "build_docs"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )

    assert docs_result.returncode == 0, (
        f"build_docs failed:\nSTDOUT:\n{docs_result.stdout}\n\nSTDERR:\n{docs_result.stderr}"
    )

    # Verify site was generated
    site_dir = result.project_dir / "site"
    assert site_dir.is_dir()
    assert (site_dir / "index.html").is_file()


@pytest.mark.integration
@pytest.mark.slow
def test_examples_session_passes(copie):
    """Smoke test: run examples session when examples are enabled.

    This validates:
    - Marimo is properly installed
    - Example notebooks are syntactically correct
    - Notebooks can be executed as scripts
    """
    import subprocess

    result = copie.copy(extra_answers={"include_examples": True})
    assert result.exit_code == 0

    # Run examples session (test_examples in noxfile)
    examples_result = subprocess.run(
        ["uvx", "nox", "-s", "test_examples"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert examples_result.returncode == 0, (
        f"test_examples failed:\nSTDOUT:\n{examples_result.stdout}\n\nSTDERR:\n{examples_result.stderr}"
    )


@pytest.mark.integration
@pytest.mark.slow
def test_full_project_workflow(copie):
    """Ultimate smoke test: run multiple nox sessions in sequence.

    This simulates a complete developer workflow:
    1. Install dependencies
    2. Run linting
    3. Run tests with coverage
    4. Run doctests
    5. Build documentation

    This is the most comprehensive validation that the generated project works.
    """
    import subprocess

    result = copie.copy(extra_answers={"include_examples": True, "include_actions": True})
    assert result.exit_code == 0

    # Session sequence to run
    sessions = [
        ("test_coverage", 180),
        ("test_docstrings", 120),
        ("test_examples", 120),
        ("build_docs", 180),
    ]

    for session_name, timeout in sessions:
        session_result = subprocess.run(
            ["uvx", "nox", "-s", session_name],
            cwd=result.project_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        assert session_result.returncode == 0, (
            f"Session '{session_name}' failed:\nSTDOUT:\n{session_result.stdout}\n\nSTDERR:\n{session_result.stderr}"
        )

    # Verify all expected outputs exist
    assert (result.project_dir / "site" / "index.html").is_file(), "Docs not built"
    assert (result.project_dir / ".coverage").exists() or (result.project_dir / "coverage.xml").exists(), (
        "Coverage not generated"
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

    content = coc_path.read_text()
    assert f"contacting the project team at {custom_email}" in content
    assert "gtauzin@stateful-y.io" not in content
