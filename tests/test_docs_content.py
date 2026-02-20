"""Comprehensive tests for documentation content in generated projects.

This test module validates:
- Documentation page content and structure
- Variable substitution in documentation
- mkdocs.yml navigation structure
- Documentation build consistency
- Examples documentation (when enabled)
"""

import yaml


class SafeMkdocsLoader(yaml.SafeLoader):
    """Custom YAML loader that handles !!python/name: tags without importing modules.

    This is needed because mkdocs.yml contains Material for MkDocs emoji configuration
    with !!python/name: tags that reference Python modules that may not be installed
    during testing. We convert these tags to plain strings for validation purposes.
    """

    pass


def construct_python_name(loader, suffix, node):
    """Convert !!python/name: tags to strings instead of importing the modules."""
    return loader.construct_scalar(node)


# Register multi constructor to handle any python/name: tag
SafeMkdocsLoader.add_multi_constructor("tag:yaml.org,2002:python/name:", construct_python_name)


class TestDocsIndexContent:
    """Test the main documentation index page."""

    def test_docs_index_includes_project_info(self, copie):
        """Test that docs index includes project metadata."""
        custom_answers = {
            "project_name": "My Awesome Tool",
            "description": "A powerful tool for data analysis",
            "author_name": "Jane Smith",
        }
        result = copie.copy(extra_answers=custom_answers)
        assert result.exit_code == 0

        docs_index = result.project_dir / "docs" / "index.md"
        assert docs_index.is_file()

        content = docs_index.read_text(encoding="utf-8")

        # Should include project name in welcome heading and throughout
        assert "My Awesome Tool" in content
        assert "Welcome to My Awesome Tool's documentation" in content

        # Should include CTA cards with proper structure
        assert "Get Started in 5 Minutes" in content
        assert "Need Help?" in content
        assert "Learn the Concepts" in content

    def test_docs_index_structure(self, copie):
        """Test that docs index has proper markdown structure."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        docs_index = result.project_dir / "docs" / "index.md"
        content = docs_index.read_text(encoding="utf-8")

        # Should have headings
        assert "#" in content

        # Should not be empty
        assert len(content.strip()) > 100


class TestGettingStartedPage:
    """Test the getting started documentation page."""

    def test_getting_started_exists(self, copie):
        """Test that getting started page exists."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        getting_started = result.project_dir / "docs" / "pages" / "getting-started.md"
        assert getting_started.is_file()

    def test_getting_started_includes_installation(self, copie):
        """Test that getting started includes installation instructions."""
        result = copie.copy(extra_answers={"package_name": "my_package"})
        assert result.exit_code == 0

        getting_started = result.project_dir / "docs" / "pages" / "getting-started.md"
        content = getting_started.read_text(encoding="utf-8")

        # Should mention installation
        assert "install" in content.lower()

        # Should include package name in code blocks
        assert "my_package" in content or "my-package" in content

    def test_getting_started_includes_usage_example(self, copie):
        """Test that getting started includes basic usage examples."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        getting_started = result.project_dir / "docs" / "pages" / "getting-started.md"
        content = getting_started.read_text(encoding="utf-8")

        # Should have code blocks
        assert "```" in content

        # Should mention usage or example
        assert "usage" in content.lower() or "example" in content.lower()


class TestUserGuidePage:
    """Test the user guide documentation page."""

    def test_user_guide_exists(self, copie):
        """Test that user guide page exists."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        user_guide = result.project_dir / "docs" / "pages" / "user-guide.md"
        assert user_guide.is_file()

    def test_user_guide_has_substantial_content(self, copie):
        """Test that user guide has meaningful content."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        user_guide = result.project_dir / "docs" / "pages" / "user-guide.md"
        content = user_guide.read_text(encoding="utf-8")

        # Should be non-trivial
        assert len(content.strip()) > 200

        # Should have multiple sections
        assert content.count("#") >= 2


class TestAPIReferencePage:
    """Test the API reference documentation page."""

    def test_api_reference_exists(self, copie):
        """Test that API reference page exists."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        api_reference = result.project_dir / "docs" / "pages" / "api-reference.md"
        assert api_reference.is_file()

    def test_api_reference_includes_package_name(self, copie):
        """Test that API reference mentions the package name."""
        result = copie.copy(extra_answers={"package_name": "custom_pkg"})
        assert result.exit_code == 0

        api_reference = result.project_dir / "docs" / "pages" / "api-reference.md"
        content = api_reference.read_text(encoding="utf-8")

        # Should reference the package
        assert "custom_pkg" in content

    def test_api_reference_has_code_documentation(self, copie):
        """Test that API reference includes code documentation."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        api_reference = result.project_dir / "docs" / "pages" / "api-reference.md"
        content = api_reference.read_text(encoding="utf-8")

        # Should have code blocks or API documentation syntax
        assert "```" in content or "::: " in content  # mkdocstrings syntax


class TestContributingPage:
    """Test the contributing documentation page."""

    def test_contributing_page_exists(self, copie):
        """Test that contributing page exists."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        contributing = result.project_dir / "docs" / "pages" / "contributing.md"
        assert contributing.is_file()

    def test_contributing_includes_development_setup(self, copie):
        """Test that contributing page includes development setup."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        contributing = result.project_dir / "docs" / "pages" / "contributing.md"
        content = contributing.read_text(encoding="utf-8")

        # Should mention development setup
        assert "develop" in content.lower()

        # Should mention uv (the dependency manager)
        assert "uv" in content

    def test_contributing_includes_testing_info(self, copie):
        """Test that contributing page includes testing information."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        contributing = result.project_dir / "docs" / "pages" / "contributing.md"
        content = contributing.read_text(encoding="utf-8")

        # Should mention testing
        assert "test" in content.lower()

        # Should mention nox or pytest
        assert "nox" in content or "pytest" in content

    def test_contributing_includes_lint_documentation(self, copie):
        """Test that contributing page documents the lint command with all three interfaces."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        contributing = result.project_dir / "docs" / "pages" / "contributing.md"
        content = contributing.read_text(encoding="utf-8")

        # Should have lint section
        assert "Run linters and type checkers" in content or "lint" in content.lower()

        # Should document all three ways to run lint
        assert "just lint" in content
        assert "uvx nox -s lint" in content
        assert "uv run ruff check src tests" in content
        assert "uv run ty check src" in content

    def test_contributing_has_github_links_in_questions_section(self, copie):
        """Test that Questions section has clickable GitHub links."""
        custom_answers = {
            "github_username": "testuser",
            "project_slug": "test-project",
        }
        result = copie.copy(extra_answers=custom_answers)
        assert result.exit_code == 0

        contributing = result.project_dir / "docs" / "pages" / "contributing.md"
        content = contributing.read_text(encoding="utf-8")

        # Should have Questions section
        assert "## Questions?" in content

        # Should have GitHub issue link
        assert "[Open an issue on GitHub](https://github.com/testuser/test-project/issues/new)" in content

        # Should have GitHub discussions link
        assert "[Start a discussion in the repository](https://github.com/testuser/test-project/discussions)" in content

    def test_contributing_has_proper_semver_list_formatting(self, copie):
        """Test that Semantic Versioning section has properly formatted list."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        contributing = result.project_dir / "docs" / "pages" / "contributing.md"
        content = contributing.read_text(encoding="utf-8")

        # Should have Version Numbering section with Semantic Versioning
        assert "### Version Numbering" in content
        assert "[Semantic Versioning](https://semver.org/)" in content

        # Check that there's a blank line before the list (proper markdown formatting)
        lines = content.split("\n")
        semver_line_idx = None
        for i, line in enumerate(lines):
            if "[Semantic Versioning](https://semver.org/):" in line:
                semver_line_idx = i
                break

        assert semver_line_idx is not None, "Semantic Versioning line not found"

        # Next line should be blank, then the list items
        assert lines[semver_line_idx + 1].strip() == "", "Missing blank line before list"
        assert "- **Major**" in lines[semver_line_idx + 2]

    def test_contributing_has_improved_mermaid_colors(self, copie):
        """Test that release process mermaid diagram has improved colors for visibility."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        contributing = result.project_dir / "docs" / "pages" / "contributing.md"
        content = contributing.read_text(encoding="utf-8")

        # Should have mermaid diagram with improved styling
        assert "```mermaid" in content

        # Check for improved color styling (amber/orange and emerald green with white text)
        assert "fill:#f59e0b" in content  # Amber/orange color
        assert "fill:#10b981" in content  # Emerald green color
        assert "color:#fff" in content  # White text color for contrast


class TestExamplesPage:
    """Test the examples documentation page (when enabled)."""

    def test_examples_page_exists_when_enabled(self, copie):
        """Test that examples page exists when include_examples=True."""
        result = copie.copy(extra_answers={"include_examples": True})
        assert result.exit_code == 0

        examples_page = result.project_dir / "docs" / "pages" / "examples.md"
        assert examples_page.is_file()

    def test_examples_page_not_exists_when_disabled(self, copie):
        """Test that examples page doesn't exist when include_examples=False."""
        result = copie.copy(extra_answers={"include_examples": False})
        assert result.exit_code == 0

        examples_page = result.project_dir / "docs" / "pages" / "examples.md"
        assert not examples_page.exists()

    def test_examples_page_references_notebooks(self, copie):
        """Test that examples page references marimo notebooks."""
        result = copie.copy(extra_answers={"include_examples": True})
        assert result.exit_code == 0

        examples_page = result.project_dir / "docs" / "pages" / "examples.md"
        content = examples_page.read_text(encoding="utf-8")

        # Should reference examples or notebooks
        assert "example" in content.lower()

        # Should have iframe or links to examples
        assert "examples/" in content or "iframe" in content.lower()

    def test_examples_page_uses_marimo_embed_with_inline_code(self, copie):
        """Test that examples page has interactive demo section with standalone notebook link."""
        result = copie.copy(extra_answers={"include_examples": True})
        assert result.exit_code == 0

        examples_page = result.project_dir / "docs" / "pages" / "examples.md"
        assert examples_page.is_file()

        content = examples_page.read_text(encoding="utf-8")

        # Should have Interactive Demo section with View/Editable links
        assert "## Interactive Demo" in content
        assert "/examples/hello/" in content
        assert "/examples/hello/edit/" in content
        assert "WASM" in content
        # Should have Running Examples Locally section
        assert "## Running Examples Locally" in content
        assert "just example" in content


class TestMkdocsConfiguration:
    """Test mkdocs.yml configuration."""

    def test_mkdocs_yml_structure(self, copie):
        """Test that mkdocs.yml has proper structure."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        assert mkdocs_file.is_file()

        mkdocs_data = yaml.load(mkdocs_file.read_text(encoding="utf-8"), Loader=SafeMkdocsLoader)

        # Required fields
        assert "site_name" in mkdocs_data
        assert "nav" in mkdocs_data or "navigation" in mkdocs_data
        assert "theme" in mkdocs_data

    def test_mkdocs_yml_includes_project_metadata(self, copie):
        """Test that mkdocs.yml includes correct project metadata."""
        custom_answers = {
            "project_name": "Custom Project",
            "description": "Custom description",
            "author_name": "Custom Author",
            "github_username": "custom-org",
            "project_slug": "custom-project",
        }
        result = copie.copy(extra_answers=custom_answers)
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        content = mkdocs_file.read_text(encoding="utf-8")
        mkdocs_data = yaml.load(content, Loader=SafeMkdocsLoader)

        # Check site_name
        assert mkdocs_data["site_name"] == "Custom Project"

        # Check site_description
        assert "site_description" in mkdocs_data
        assert mkdocs_data["site_description"] == "Custom description"

        # Check repo_url
        assert "repo_url" in mkdocs_data
        assert "custom-org" in mkdocs_data["repo_url"]
        assert "custom-project" in mkdocs_data["repo_url"]

    def test_mkdocs_yml_navigation_structure(self, copie):
        """Test that mkdocs.yml has proper navigation structure."""
        result = copie.copy(extra_answers={"include_examples": False})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.load(mkdocs_file.read_text(encoding="utf-8"), Loader=SafeMkdocsLoader)

        nav = mkdocs_data.get("nav", [])
        assert len(nav) > 0

        # Should have standard pages
        nav_str = str(nav).lower()
        assert "getting" in nav_str or "start" in nav_str
        assert "contributing" in nav_str
        assert "api" in nav_str or "reference" in nav_str

    def test_mkdocs_yml_navigation_includes_examples_when_enabled(self, copie):
        """Test that navigation includes examples when enabled."""
        result = copie.copy(extra_answers={"include_examples": True})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.load(mkdocs_file.read_text(encoding="utf-8"), Loader=SafeMkdocsLoader)

        nav = mkdocs_data.get("nav", [])
        nav_str = str(nav).lower()

        # Should include examples in navigation
        assert "example" in nav_str

    def test_mkdocs_yml_navigation_excludes_examples_when_disabled(self, copie):
        """Test that navigation excludes examples when disabled."""
        result = copie.copy(extra_answers={"include_examples": False})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.load(mkdocs_file.read_text(encoding="utf-8"), Loader=SafeMkdocsLoader)

        nav = mkdocs_data.get("nav", [])
        nav_str = str(nav).lower()

        # Should NOT include examples in navigation
        assert "example" not in nav_str

    def test_mkdocs_yml_uses_material_theme(self, copie):
        """Test that mkdocs.yml uses Material theme."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.load(mkdocs_file.read_text(encoding="utf-8"), Loader=SafeMkdocsLoader)

        theme = mkdocs_data.get("theme", {})
        if isinstance(theme, dict):
            assert theme.get("name") == "material"
        else:
            assert theme == "material"

    def test_mkdocs_yml_includes_plugins(self, copie):
        """Test that mkdocs.yml includes necessary plugins."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.load(mkdocs_file.read_text(encoding="utf-8"), Loader=SafeMkdocsLoader)

        assert "plugins" in mkdocs_data
        plugins = mkdocs_data["plugins"]

        # Should have search plugin
        plugins_str = str(plugins).lower()
        assert "search" in plugins_str

    def test_mkdocs_yml_includes_marimo_plugin_when_examples_enabled(self, copie):
        """Test that mkdocs.yml does not include marimo plugin (marimo embed is used instead)."""
        result = copie.copy(extra_answers={"include_examples": True})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.load(mkdocs_file.read_text(encoding="utf-8"), Loader=SafeMkdocsLoader)

        plugins = mkdocs_data.get("plugins", [])
        plugins_str = str(plugins).lower()

        # marimo plugin is not used - we use marimo-embed directive instead
        assert "marimo" not in plugins_str

    def test_mkdocs_yml_excludes_marimo_plugin_when_examples_disabled(self, copie):
        """Test that mkdocs.yml excludes marimo plugin when examples disabled."""
        result = copie.copy(extra_answers={"include_examples": False})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.load(mkdocs_file.read_text(encoding="utf-8"), Loader=SafeMkdocsLoader)

        plugins = mkdocs_data.get("plugins", [])
        plugins_str = str(plugins).lower()

        # Should NOT include marimo plugin
        assert "marimo" not in plugins_str

    def test_mkdocs_yml_has_hooks_configured(self, copie):
        """Test that mkdocs.yml has hooks configured."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.load(mkdocs_file.read_text(encoding="utf-8"), Loader=SafeMkdocsLoader)

        # Should have hooks section
        assert "hooks" in mkdocs_data
        hooks = mkdocs_data["hooks"]

        # Should reference docs/hooks.py
        assert "docs/hooks.py" in hooks

    def test_mkdocs_yml_has_emoji_extension_configured(self, copie):
        """Test that mkdocs.yml has emoji extension configured."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        assert mkdocs_file.is_file()

        # Read as text to check for the emoji extension
        content = mkdocs_file.read_text(encoding="utf-8")

        # Check that pymdownx.emoji is configured (simplified config without Python name resolution)
        assert "pymdownx.emoji" in content
        # Should NOT have !!python/name tags (these cause issues with some YAML parsers)
        assert "!!python/name:" not in content


class TestDocumentationVariableSubstitution:
    """Test that template variables are correctly substituted in all docs."""

    def test_all_docs_use_correct_package_name(self, copie):
        """Test that all documentation uses the correct package name."""
        result = copie.copy(extra_answers={"package_name": "my_custom_pkg"})
        assert result.exit_code == 0

        docs_pages = [
            result.project_dir / "docs" / "index.md",
            result.project_dir / "docs" / "pages" / "getting-started.md",
            result.project_dir / "docs" / "pages" / "api-reference.md",
        ]

        for page in docs_pages:
            if page.exists():
                content = page.read_text(encoding="utf-8")

                # Should not have template placeholders
                assert "{{" not in content
                assert "}}" not in content
                assert "package_name" not in content or "my_custom_pkg" in content

    def test_docs_use_correct_github_username(self, copie):
        """Test that documentation uses correct GitHub username in URLs."""
        result = copie.copy(
            extra_answers={
                "github_username": "my-custom-org",
                "project_slug": "my-project",
            }
        )
        assert result.exit_code == 0

        # Check mkdocs.yml
        mkdocs_file = result.project_dir / "mkdocs.yml"
        content = mkdocs_file.read_text(encoding="utf-8")

        assert "my-custom-org" in content
        assert "github.com/my-custom-org/my-project" in content

        # Check contributing page
        contributing = result.project_dir / "docs" / "pages" / "contributing.md"
        if contributing.exists():
            contrib_content = contributing.read_text(encoding="utf-8")
            # Should reference the correct repository
            assert "my-custom-org" in contrib_content or "my-project" in contrib_content
