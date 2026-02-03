"""Tests for mkdocs hooks functionality."""

import pytest


@pytest.fixture
def copie_with_examples(copie):
    """Copy template with examples enabled."""
    result = copie.copy(
        extra_answers={
            "include_examples": True,
        },
    )
    assert result.exit_code == 0
    return result


@pytest.fixture
def copie_without_examples(copie):
    """Copy template with examples disabled."""
    result = copie.copy(
        extra_answers={
            "include_examples": False,
        },
    )
    assert result.exit_code == 0
    return result


def test_hooks_file_created_with_examples(copie_with_examples):
    """Test that hooks.py is created when examples are enabled."""
    hooks_file = copie_with_examples.project_dir / "docs" / "hooks.py"
    assert hooks_file.is_file(), "docs/hooks.py not created"

    # Verify hooks content
    hooks_content = hooks_file.read_text()
    assert "on_pre_build" in hooks_content, "on_pre_build hook not found"
    assert "on_files" in hooks_content, "on_files hook not found"
    assert "on_post_build" in hooks_content, "on_post_build hook not found"

    # Verify marimo export logic is present
    assert "marimo" in hooks_content, "marimo export logic not found"
    assert "export" in hooks_content, "export logic not found"
    assert "html-wasm" in hooks_content, "html-wasm export mode not found"


def test_hooks_file_created_without_examples(copie_without_examples):
    """Test that hooks.py is created even when examples are disabled."""
    hooks_file = copie_without_examples.project_dir / "docs" / "hooks.py"
    assert hooks_file.is_file(), "docs/hooks.py not created"

    # Verify hooks content has minimal implementation
    hooks_content = hooks_file.read_text()
    assert "on_files" in hooks_content, "on_files hook not found"
    assert "on_post_build" in hooks_content, "on_post_build hook not found"

    # on_pre_build should not exist when examples disabled
    assert "on_pre_build" not in hooks_content, "on_pre_build should not exist without examples"


def test_on_post_build_copies_markdown(copie_with_examples, tmp_path):
    """Test that on_post_build hook copies markdown files."""
    import sys

    # Add project to path so we can import hooks
    sys.path.insert(0, str(copie_with_examples.project_dir / "docs"))

    try:
        import hooks

        # Create mock config
        site_dir = tmp_path / "site"
        site_dir.mkdir()
        docs_dir = copie_with_examples.project_dir / "docs"

        config = {
            "site_dir": str(site_dir),
            "docs_dir": str(docs_dir),
        }

        # Call on_post_build
        hooks.on_post_build(config)

        # Verify markdown files were copied
        assert (site_dir / "index.md").is_file(), "index.md not copied"
        assert (site_dir / "pages" / "getting-started.md").is_file(), "getting-started.md not copied"
        assert (site_dir / "pages" / "contributing.md").is_file(), "contributing.md not copied"

    finally:
        sys.path.pop(0)


def test_on_files_copies_html(copie_with_examples, tmp_path):
    """Test that on_files hook copies standalone HTML files."""
    import subprocess

    # First export notebooks using build_docs to trigger hooks
    subprocess.run(
        ["uvx", "nox", "-s", "build_docs"],
        cwd=copie_with_examples.project_dir,
        capture_output=True,
        timeout=60,
        check=True,
    )

    # Verify HTML was exported
    html_file = copie_with_examples.project_dir / "docs" / "examples" / "hello" / "index.html"
    assert html_file.is_file(), "HTML file not exported by on_pre_build"

    # Verify HTML was also copied to site by the full build
    site_html = copie_with_examples.project_dir / "site" / "examples" / "hello" / "index.html"
    assert site_html.is_file(), "Standalone HTML not copied to site"

    # Verify the HTML file is substantial (not just a stub)
    html_size = site_html.stat().st_size
    assert html_size > 10000, f"HTML file too small ({html_size} bytes), may not be properly exported"


def test_on_pre_build_exports_notebooks(copie_with_examples):
    """Test that on_pre_build exports marimo notebooks."""
    import subprocess

    # Build docs which triggers on_pre_build
    result = subprocess.run(
        ["uvx", "nox", "-s", "build_docs"],
        cwd=copie_with_examples.project_dir,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, f"build_docs failed: {result.stderr}"

    # Verify exported HTML exists
    html_file = copie_with_examples.project_dir / "docs" / "examples" / "hello" / "index.html"
    assert html_file.is_file(), "Notebook not exported to HTML"

    # Verify it's a valid HTML file
    html_content = html_file.read_text()
    assert "<html" in html_content, "Exported file is not valid HTML"
    assert "marimo" in html_content.lower(), "HTML doesn't contain marimo runtime"


def test_on_files_handles_missing_examples_dir(copie_with_examples, tmp_path):
    """Test that on_files gracefully handles missing examples directory."""
    import sys

    sys.path.insert(0, str(copie_with_examples.project_dir / "docs"))

    try:
        import hooks

        # Create mock config with non-existent examples
        site_dir = tmp_path / "site"
        site_dir.mkdir()

        config = {
            "site_dir": str(site_dir),
        }

        # Remove examples directory if it exists
        docs_examples = copie_with_examples.project_dir / "docs" / "examples"
        if docs_examples.exists():
            import shutil

            shutil.rmtree(docs_examples)

        # Call on_files - should not raise
        result = hooks.on_files([], config)

        # Should return files unchanged
        assert result == []

    finally:
        sys.path.pop(0)


def test_hooks_integrated_in_mkdocs_yml(copie_with_examples):
    """Test that hooks are properly configured in mkdocs.yml."""
    mkdocs_yml = copie_with_examples.project_dir / "mkdocs.yml"
    content = mkdocs_yml.read_text()

    assert "hooks:" in content, "hooks section not found in mkdocs.yml"
    assert "docs/hooks.py" in content, "hooks.py not referenced in mkdocs.yml"
