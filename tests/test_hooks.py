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
    hooks_content = hooks_file.read_text(encoding="utf-8")
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
    hooks_content = hooks_file.read_text(encoding="utf-8")
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


@pytest.mark.integration
@pytest.mark.slow
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


@pytest.mark.integration
@pytest.mark.slow
def test_on_pre_build_exports_notebooks(copie_with_examples):
    """Test that on_pre_build exports marimo notebooks."""
    import subprocess

    # Build docs which triggers on_pre_build
    result = subprocess.run(
        ["uvx", "nox", "-s", "build_docs"],
        cwd=copie_with_examples.project_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, f"build_docs failed: {result.stderr}"

    # Verify exported HTML exists
    html_file = copie_with_examples.project_dir / "docs" / "examples" / "hello" / "index.html"
    assert html_file.is_file(), "Notebook not exported to HTML"

    # Verify it's a valid HTML file
    html_content = html_file.read_text(encoding="utf-8")
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
    content = mkdocs_yml.read_text(encoding="utf-8")

    assert "hooks:" in content, "hooks section not found in mkdocs.yml"
    assert "docs/hooks.py" in content, "hooks.py not referenced in mkdocs.yml"


@pytest.mark.integration
@pytest.mark.slow
def test_on_post_build_converts_html_to_markdown(copie_with_examples, tmp_path):
    """Test that on_post_build converts HTML to markdown for LLM consumption."""
    import subprocess

    # Build docs to generate both HTML and markdown
    result = subprocess.run(
        ["uvx", "nox", "-s", "build_docs"],
        cwd=copie_with_examples.project_dir,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, f"build_docs failed: {result.stderr}"

    # Verify markdown files exist in site directory
    site_dir = copie_with_examples.project_dir / "site"
    assert (site_dir / "index.md").is_file(), "index.md not found in site"
    assert (site_dir / "pages" / "getting-started.md").is_file(), "getting-started.md not found in site"
    assert (site_dir / "pages" / "api-reference.md").is_file(), "api-reference.md not found"

    # Verify markdown content is cleaned (not just raw source)
    index_md = (site_dir / "index.md").read_text(encoding="utf-8")
    assert len(index_md) > 100, "Markdown file is too short"
    assert "# " in index_md, "Markdown doesn't contain headers"


def test_on_post_build_copies_llms_txt_if_exists(copie_with_examples, tmp_path):
    """Test that on_post_build copies llms.txt if it exists."""
    import sys

    # Add project to path
    sys.path.insert(0, str(copie_with_examples.project_dir / "docs"))

    try:
        import hooks

        # Create llms.txt in docs
        docs_dir = copie_with_examples.project_dir / "docs"
        llms_txt = docs_dir / "llms.txt"
        llms_txt.write_text("# LLM Context\nProject documentation", encoding="utf-8")

        site_dir = tmp_path / "site"
        site_dir.mkdir()

        config = {
            "site_dir": str(site_dir),
            "docs_dir": str(docs_dir),
        }

        # Call on_post_build
        hooks.on_post_build(config)

        # Verify llms.txt was copied
        assert (site_dir / "llms.txt").is_file(), "llms.txt not copied to site"
        content = (site_dir / "llms.txt").read_text(encoding="utf-8")
        assert "LLM Context" in content, "llms.txt content not preserved"

    finally:
        sys.path.pop(0)


def test_on_post_build_removes_legacy_llm_directory(copie_with_examples, tmp_path):
    """Test that on_post_build removes legacy llm/ directory."""
    import sys

    sys.path.insert(0, str(copie_with_examples.project_dir / "docs"))

    try:
        import hooks

        docs_dir = copie_with_examples.project_dir / "docs"
        site_dir = tmp_path / "site"
        site_dir.mkdir()

        # Create legacy llm directory
        legacy_dir = site_dir / "llm"
        legacy_dir.mkdir()
        (legacy_dir / "old_file.md").write_text("old content", encoding="utf-8")

        config = {
            "site_dir": str(site_dir),
            "docs_dir": str(docs_dir),
        }

        # Call on_post_build
        hooks.on_post_build(config)

        # Verify legacy directory was removed
        assert not legacy_dir.exists(), "Legacy llm/ directory not removed"

    finally:
        sys.path.pop(0)


def test_html_to_markdown_conversion_preserves_structure(copie_with_examples):
    """Test that HTML to markdown conversion preserves document structure."""
    import sys

    sys.path.insert(0, str(copie_with_examples.project_dir / "docs"))

    try:
        import hooks

        # Test HTML with various elements
        test_html = """
        <h1>Main Title</h1>
        <p>This is a paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
        <pre><code class="language-python">def example():
    return "hello"</code></pre>
        <ul>
            <li>First item</li>
            <li>Second item</li>
        </ul>
        """

        markdown = hooks._html_to_markdown(test_html)

        # Verify structure is preserved
        assert "# Main Title" in markdown, "H1 not converted"
        assert "**bold**" in markdown, "Bold not converted"
        assert "*italic*" in markdown, "Italic not converted"
        assert "```python" in markdown, "Code fence not created"
        assert "def example():" in markdown, "Code content not preserved"
        assert "- First item" in markdown or "- First item" in markdown, "List not converted"

    finally:
        sys.path.pop(0)


def test_html_to_markdown_handles_tables(copie_with_examples):
    """Test that HTML to markdown conversion handles tables correctly."""
    import sys

    sys.path.insert(0, str(copie_with_examples.project_dir / "docs"))

    try:
        import hooks

        test_html = """
        <table>
            <tr>
                <th>Header 1</th>
                <th>Header 2</th>
            </tr>
            <tr>
                <td>Cell 1</td>
                <td>Cell 2</td>
            </tr>
        </table>
        """

        markdown = hooks._html_to_markdown(test_html)

        # Verify table structure
        assert "|" in markdown, "Table pipes not found"
        assert "---" in markdown, "Table separator not found"
        assert "Header 1" in markdown, "Table headers not preserved"
        assert "Cell 1" in markdown, "Table cells not preserved"

    finally:
        sys.path.pop(0)


@pytest.mark.integration
@pytest.mark.slow
def test_markdown_accessible_after_docs_build(copie_with_examples):
    """Test that markdown files are accessible after docs build completes."""
    import subprocess

    # Build docs
    result = subprocess.run(
        ["uvx", "nox", "-s", "build_docs"],
        cwd=copie_with_examples.project_dir,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, f"build_docs failed: {result.stderr}"

    site_dir = copie_with_examples.project_dir / "site"

    # Verify both HTML and markdown exist for each page
    pages = [
        "index",
        "pages/getting-started",
        "pages/user-guide",
        "pages/api-reference",
        "pages/contributing",
    ]

    for page in pages:
        html_path = (
            site_dir / f"{page if page == 'index' else page}/index.html" if page != "index" else site_dir / "index.html"
        )
        md_path = site_dir / f"{page}.md"

        assert html_path.is_file(), f"HTML not found: {html_path}"
        assert md_path.is_file(), f"Markdown not found: {md_path}"

        # Verify markdown is not empty
        md_content = md_path.read_text(encoding="utf-8")
        assert len(md_content) > 50, f"Markdown too short for {page}"
