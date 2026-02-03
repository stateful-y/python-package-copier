"""Tests for the copier template."""


def test_template_creates_project(copie):
    """Test that the template creates a valid project."""
    expected_files = [
        ".gitignore",
        "README.md",
        "pyproject.toml",
        "noxfile.py",
        "mkdocs.yml",
        ".pre-commit-config.yaml",
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


def test_generated_project_structure(copie):
    """Test that the generated project has the correct structure."""
    result = copie.copy()

    # Check source files
    src_dir = result.project_dir / "src" / "test_project"
    assert (src_dir / "__init__.py").is_file()
    assert (src_dir / "example.py").is_file()
    assert (src_dir / "py.typed").is_file()

    # Check test files
    tests_dir = result.project_dir / "tests"
    assert (tests_dir / "conftest.py").is_file()
    assert (tests_dir / "test_example.py").is_file()

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

    content = pyproject_path.read_text()

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


def test_generated_project_has_correct_license(copie):
    """Test that the generated project has the correct license."""
    result = copie.copy(
        extra_answers={
            "license": "MIT",
        },
    )

    license_path = result.project_dir / "LICENSE"
    assert license_path.is_file()

    content = license_path.read_text()
    assert "MIT" in content


def test_noxfile_configuration(copie):
    """Test that noxfile is properly configured."""
    result = copie.copy()

    noxfile_path = result.project_dir / "noxfile.py"
    assert noxfile_path.is_file()

    content = noxfile_path.read_text()

    # Check for uv backend
    assert 'default_venv_backend = "uv|virtualenv"' in content

    # Check for ty
    assert "ty" in content, "ty not found in noxfile.py"


def test_precommit_configuration(copie):
    """Test that pre-commit config is properly set up."""
    result = copie.copy()

    precommit_path = result.project_dir / ".pre-commit-config.yaml"
    assert precommit_path.is_file()

    content = precommit_path.read_text()

    # Check for ruff
    assert "ruff-pre-commit" in content or "ruff" in content

    # Check for ty
    assert "ty" in content, "ty not found in pre-commit config"

    # Check for commitizen
    assert "commitizen" in content, "commitizen not found in pre-commit config"


def test_github_workflows(copie):
    """Test that GitHub workflows are properly configured."""
    result = copie.copy()

    tests_workflow = result.project_dir / ".github" / "workflows" / "tests.yml"
    assert tests_workflow.is_file()

    content = tests_workflow.read_text()

    # Check for uv usage
    assert "astral-sh/setup-uv" in content

    # Check for ty
    assert "ty" in content, "ty not found in tests workflow"

    # Check for doctest job
    assert "doctest:" in content, "doctest job not found in tests workflow"
    assert "nox -s doctest" in content, "doctest nox session not run in CI"

    # Check PR title validation workflow
    pr_title_workflow = result.project_dir / ".github" / "workflows" / "pr-title.yml"
    assert pr_title_workflow.is_file(), "PR title validation workflow not found"

    pr_title_content = pr_title_workflow.read_text()
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

    changelog_content = changelog_workflow.read_text()

    # Check for git-cliff
    assert "git-cliff" in changelog_content, "git-cliff not found in changelog workflow"

    # Check for changelog job
    assert "changelog" in changelog_content.lower(), "changelog job not found in changelog workflow"

    # Check publish-release.yml workflow
    release_workflow = result.project_dir / ".github" / "workflows" / "publish-release.yml"
    assert release_workflow.is_file()

    release_content = release_workflow.read_text()

    # Check for GitHub release creation
    assert "gh release create" in release_content or "github-release" in release_content.lower(), (
        "GitHub release creation not found"
    )


def test_commitizen_configuration(copie):
    """Test that commitizen is properly configured."""
    result = copie.copy()

    pyproject_path = result.project_dir / "pyproject.toml"
    assert pyproject_path.is_file()

    content = pyproject_path.read_text()

    # Check for commitizen configuration
    assert "[tool.commitizen]" in content, "commitizen config not found in pyproject.toml"
    assert "cz_conventional_commits" in content, "conventional commits not configured"


def test_git_cliff_configuration(copie):
    """Test that git-cliff configuration exists."""
    result = copie.copy()

    cliff_config = result.project_dir / ".git-cliff.toml"
    assert cliff_config.is_file()

    content = cliff_config.read_text()

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
    pyproject_content = (result.project_dir / "pyproject.toml").read_text()
    assert "[tool.pytest.ini_options.doctest]" in pyproject_content
    assert "--doctest-modules" in pyproject_content
    assert "--doctest-continue-on-failure" in pyproject_content

    # Check noxfile has doctest session
    noxfile_content = (result.project_dir / "noxfile.py").read_text()
    assert "def doctest(session:" in noxfile_content
    assert '"--doctest-modules"' in noxfile_content

    # Check justfile has doctest command
    justfile_content = (result.project_dir / "justfile").read_text()
    assert "doctest:" in justfile_content
    assert "--doctest-modules" in justfile_content

    # Check example.py has docstring examples
    example_py = (result.project_dir / "src" / "test_project" / "example.py").read_text()
    assert "Examples:" in example_py
    assert ">>>" in example_py


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
    notebook_content = hello_notebook.read_text()
    assert "import marimo" in notebook_content
    assert "app = marimo.App" in notebook_content
    assert "plotly" in notebook_content
    assert "num_points" in notebook_content

    # Check marimo in dependencies
    pyproject_content = (result.project_dir / "pyproject.toml").read_text()
    assert "marimo" in pyproject_content
    assert "plotly" in pyproject_content
    assert "mkdocs-marimo" in pyproject_content

    # Check noxfile has export_examples and run_examples sessions
    noxfile_content = (result.project_dir / "noxfile.py").read_text()
    assert "def export_examples(session:" in noxfile_content
    assert "def run_examples(session:" in noxfile_content
    assert "examples/hello.py" in noxfile_content
    assert "scripts/export_marimo_examples.py" in noxfile_content

    # Check docs/examples/ directory for exports
    docs_examples_dir = result.project_dir / "docs" / "examples"
    assert docs_examples_dir.is_dir(), "docs/examples/ directory not created"

    # Check export script exists
    export_script = result.project_dir / "scripts" / "export_marimo_examples.py"
    assert export_script.is_file(), "scripts/export_marimo_examples.py not created"

    # Check justfile has example command
    justfile_content = (result.project_dir / "justfile").read_text()
    assert "example:" in justfile_content
    assert "marimo edit" in justfile_content

    # Check examples.md exists and mentions standalone notebooks
    examples_md = result.project_dir / "docs" / "pages" / "examples.md"
    assert examples_md.is_file(), "docs/pages/examples.md not created"
    examples_content = examples_md.read_text()
    assert "Standalone HTML Notebooks" in examples_content
    assert "../examples/hello/" in examples_content

    # Check mkdocs.yml includes examples in nav and has exclude_docs
    mkdocs_content = (result.project_dir / "mkdocs.yml").read_text()
    assert "Examples: pages/examples.md" in mkdocs_content
    # Check for multiline exclude_docs format
    assert "exclude_docs:" in mkdocs_content
    assert "examples/**/index.html" in mkdocs_content
    assert "examples/**/CLAUDE.md" in mkdocs_content

    # Check GitHub workflow includes examples job
    tests_workflow = result.project_dir / ".github" / "workflows" / "tests.yml"
    workflow_content = tests_workflow.read_text()
    assert "examples:" in workflow_content
    assert "nox -s run_examples" in workflow_content

    # Check README mentions examples
    readme_content = (result.project_dir / "README.md").read_text()
    assert "## Examples" in readme_content
    assert "marimo edit examples/hello.py" in readme_content

    # Check CONTRIBUTING mentions adding examples
    contributing_content = (result.project_dir / "docs" / "pages" / "contributing.md").read_text()
    assert "### Adding Examples" in contributing_content
    assert "export_examples" in contributing_content


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
    pyproject_content = (result.project_dir / "pyproject.toml").read_text()
    # examples group should not exist or be empty
    assert (
        "examples = [" not in pyproject_content
        or "examples = []" in pyproject_content
        or "examples = [\n]" in pyproject_content
    )
    # marimo should not be in dependencies
    assert "marimo" not in pyproject_content
    assert "plotly" not in pyproject_content
    # mkdocs-marimo should not be in docs dependencies
    assert "mkdocs-marimo" not in pyproject_content

    # Check noxfile doesn't have run_examples session
    noxfile_content = (result.project_dir / "noxfile.py").read_text()
    assert "def run_examples(session:" not in noxfile_content

    # Check justfile doesn't have example command
    justfile_content = (result.project_dir / "justfile").read_text()
    # Should not have the example command, but might have other content
    lines = justfile_content.split("\n")
    example_command_lines = [line for line in lines if line.strip().startswith("example:")]
    assert len(example_command_lines) == 0, "example command should not exist"

    # Check examples.md doesn't exist or is empty
    examples_md = result.project_dir / "docs" / "examples.md"
    if examples_md.exists():
        content = examples_md.read_text().strip()
        assert content == "", (
            f"docs/examples.md should be empty when examples are disabled, but contains: {content[:100]}"
        )

    # Check mkdocs.yml doesn't include examples in nav
    mkdocs_content = (result.project_dir / "mkdocs.yml").read_text()
    assert "Examples: examples.md" not in mkdocs_content

    # Check GitHub workflow doesn't include examples job
    tests_workflow = result.project_dir / ".github" / "workflows" / "tests.yml"
    workflow_content = tests_workflow.read_text()
    assert "run_examples" not in workflow_content


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
    tests_workflow_content = (workflows_dir / "tests.yml").read_text()
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
        content = git_cliff.read_text().strip()
        assert content == "", ".git-cliff.toml should be empty when GitHub Actions are disabled"


def test_markdown_docs_script_configuration(copie):
    """Test that copy_markdown_docs.py script is properly configured."""
    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )

    assert result.exit_code == 0

    # Verify prepare_site.py script exists
    copy_script = result.project_dir / "scripts" / "prepare_site.py"
    assert copy_script.is_file(), "scripts/prepare_site.py not created"

    # Verify script has correct default docs_dir
    script_content = copy_script.read_text()
    assert 'docs_dir = _parse_top_level_value(lines, "docs_dir") or "docs"' in script_content, (
        "prepare_site.py should default to 'docs' directory"
    )

    # Verify noxfile integrates the script in build_docs
    noxfile_content = (result.project_dir / "noxfile.py").read_text()
    assert 'session.run("python", "scripts/prepare_site.py")' in noxfile_content, (
        "prepare_site.py should be called in noxfile.py"
    )

    # Verify ReadTheDocs config includes build hooks
    rtd_config = result.project_dir / ".readthedocs.yml"
    rtd_content = rtd_config.read_text()
    assert "post_install:" in rtd_content
    assert "python scripts/export_marimo_examples.py" in rtd_content
    assert "build:" in rtd_content
    assert "python scripts/prepare_site.py" in rtd_content


def test_marimo_notebook_export_to_html(copie):
    """Test that marimo notebooks are properly exported to standalone HTML."""
    import subprocess

    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )

    assert result.exit_code == 0

    # Verify export script exists
    export_script = result.project_dir / "scripts" / "export_marimo_examples.py"
    assert export_script.is_file(), "scripts/export_marimo_examples.py not created"

    # Verify docs/examples directory exists
    docs_examples_dir = result.project_dir / "docs" / "examples"
    assert docs_examples_dir.is_dir(), "docs/examples/ directory not created"

    # Run the export_examples nox session
    export_result = subprocess.run(
        ["uvx", "nox", "-s", "export_examples"],
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
    html_content = hello_html.read_text()
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
        content = md_file.read_text()
        assert len(content) > 0, f"{md_file} is empty"

        # Should not contain raw HTML tags from mkdocs-material
        html_tags_to_check = ["<article", "<div class=", "<nav class=", "<header class="]
        for tag in html_tags_to_check:
            assert tag not in content, f"{md_file.name} contains HTML tag: {tag}"

        # Should contain markdown formatting
        # At least one of these markdown elements should be present
        has_markdown = any(marker in content for marker in ["# ", "## ", "- ", "* ", "[", "```", "**", "__"])
        assert has_markdown, f"{md_file.name} doesn't appear to contain markdown formatting"


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
    examples_content = examples_md.read_text()
    # Check for either marimo embed directive or inline marimo code
    has_marimo = "marimo-embed-file" in examples_content or "```python {marimo}" in examples_content
    assert has_marimo, "Embedded marimo notebook not found in examples.md"

    # Tier 2: Export standalone HTML
    export_result = subprocess.run(
        ["uvx", "nox", "-s", "export_examples"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert export_result.returncode == 0
    standalone_html = result.project_dir / "docs" / "examples" / "hello" / "index.html"
    assert standalone_html.is_file(), "Standalone HTML not created (Tier 2)"

    # Verify examples.md links to standalone HTML
    assert "Standalone HTML Notebooks" in examples_content, "No standalone section in examples.md"
    assert "../examples/hello/" in examples_content, "No link to standalone HTML in examples.md"

    # Verify mkdocs excludes standalone HTML from processing
    mkdocs_yml = result.project_dir / "mkdocs.yml"
    mkdocs_content = mkdocs_yml.read_text()
    assert "exclude_docs:" in mkdocs_content, "mkdocs.yml doesn't have exclude_docs"
    assert "examples/**/index.html" in mkdocs_content, "mkdocs.yml doesn't exclude standalone HTML files"
    assert "examples/**/CLAUDE.md" in mkdocs_content, "mkdocs.yml doesn't exclude CLAUDE.md files"

    # Tier 3: Build docs and create markdown copies
    build_result = subprocess.run(
        ["uvx", "nox", "-s", "build_docs"],
        cwd=result.project_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert build_result.returncode == 0
    markdown_copy = result.project_dir / "site" / "index.md"
    assert markdown_copy.is_file(), "Markdown copy not created (Tier 3)"

    # Verify all three tiers are present
    assert examples_md.is_file(), "Tier 1 (embedded) missing"
    assert standalone_html.is_file(), "Tier 2 (standalone HTML) missing"
    assert markdown_copy.is_file(), "Tier 3 (markdown copies) missing"
