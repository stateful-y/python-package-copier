"""Comprehensive tests for documentation content in generated projects.

This test module validates:
- Documentation page content and structure
- Variable substitution in documentation
- mkdocs.yml navigation structure
- Documentation build consistency
- Examples documentation (when enabled)
"""

import pytest
import yaml


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

        content = docs_index.read_text()

        # Should include project name
        assert "My Awesome Tool" in content

        # Should include description
        assert "A powerful tool for data analysis" in content

    def test_docs_index_structure(self, copie):
        """Test that docs index has proper markdown structure."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        docs_index = result.project_dir / "docs" / "index.md"
        content = docs_index.read_text()

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
        content = getting_started.read_text()

        # Should mention installation
        assert "install" in content.lower()

        # Should include package name in code blocks
        assert "my_package" in content or "my-package" in content

    def test_getting_started_includes_usage_example(self, copie):
        """Test that getting started includes basic usage examples."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        getting_started = result.project_dir / "docs" / "pages" / "getting-started.md"
        content = getting_started.read_text()

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
        content = user_guide.read_text()

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
        content = api_reference.read_text()

        # Should reference the package
        assert "custom_pkg" in content

    def test_api_reference_has_code_documentation(self, copie):
        """Test that API reference includes code documentation."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        api_reference = result.project_dir / "docs" / "pages" / "api-reference.md"
        content = api_reference.read_text()

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
        content = contributing.read_text()

        # Should mention development setup
        assert "develop" in content.lower()

        # Should mention uv (the dependency manager)
        assert "uv" in content

    def test_contributing_includes_testing_info(self, copie):
        """Test that contributing page includes testing information."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        contributing = result.project_dir / "docs" / "pages" / "contributing.md"
        content = contributing.read_text()

        # Should mention testing
        assert "test" in content.lower()

        # Should mention nox or pytest
        assert "nox" in content or "pytest" in content


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
        content = examples_page.read_text()

        # Should reference examples or notebooks
        assert "example" in content.lower()

        # Should have iframe or links to examples
        assert "examples/" in content or "iframe" in content.lower()


class TestMkdocsConfiguration:
    """Test mkdocs.yml configuration."""

    def test_mkdocs_yml_structure(self, copie):
        """Test that mkdocs.yml has proper structure."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        assert mkdocs_file.is_file()

        mkdocs_data = yaml.safe_load(mkdocs_file.read_text())

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
        content = mkdocs_file.read_text()
        mkdocs_data = yaml.safe_load(content)

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
        mkdocs_data = yaml.safe_load(mkdocs_file.read_text())

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
        mkdocs_data = yaml.safe_load(mkdocs_file.read_text())

        nav = mkdocs_data.get("nav", [])
        nav_str = str(nav).lower()

        # Should include examples in navigation
        assert "example" in nav_str

    def test_mkdocs_yml_navigation_excludes_examples_when_disabled(self, copie):
        """Test that navigation excludes examples when disabled."""
        result = copie.copy(extra_answers={"include_examples": False})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.safe_load(mkdocs_file.read_text())

        nav = mkdocs_data.get("nav", [])
        nav_str = str(nav).lower()

        # Should NOT include examples in navigation
        assert "example" not in nav_str

    def test_mkdocs_yml_uses_material_theme(self, copie):
        """Test that mkdocs.yml uses Material theme."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.safe_load(mkdocs_file.read_text())

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
        mkdocs_data = yaml.safe_load(mkdocs_file.read_text())

        assert "plugins" in mkdocs_data
        plugins = mkdocs_data["plugins"]

        # Should have search plugin
        plugins_str = str(plugins).lower()
        assert "search" in plugins_str

    def test_mkdocs_yml_includes_marimo_plugin_when_examples_enabled(self, copie):
        """Test that mkdocs.yml includes marimo plugin when examples enabled."""
        result = copie.copy(extra_answers={"include_examples": True})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.safe_load(mkdocs_file.read_text())

        plugins = mkdocs_data.get("plugins", [])
        plugins_str = str(plugins).lower()

        # Should include marimo plugin
        assert "marimo" in plugins_str

    def test_mkdocs_yml_excludes_marimo_plugin_when_examples_disabled(self, copie):
        """Test that mkdocs.yml excludes marimo plugin when examples disabled."""
        result = copie.copy(extra_answers={"include_examples": False})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.safe_load(mkdocs_file.read_text())

        plugins = mkdocs_data.get("plugins", [])
        plugins_str = str(plugins).lower()

        # Should NOT include marimo plugin
        assert "marimo" not in plugins_str

    def test_mkdocs_yml_has_hooks_configured(self, copie):
        """Test that mkdocs.yml has hooks configured."""
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        mkdocs_file = result.project_dir / "mkdocs.yml"
        mkdocs_data = yaml.safe_load(mkdocs_file.read_text())

        # Should have hooks section
        assert "hooks" in mkdocs_data
        hooks = mkdocs_data["hooks"]

        # Should reference docs/hooks.py
        assert "docs/hooks.py" in hooks


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
                content = page.read_text()

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
        content = mkdocs_file.read_text()

        assert "my-custom-org" in content
        assert "github.com/my-custom-org/my-project" in content

        # Check contributing page
        contributing = result.project_dir / "docs" / "pages" / "contributing.md"
        if contributing.exists():
            contrib_content = contributing.read_text()
            # Should reference the correct repository
            assert "my-custom-org" in contrib_content or "my-project" in contrib_content


class TestDocumentationBuildIntegration:
    """Integration tests for documentation building."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_docs_build_succeeds_with_examples(self, copie):
        """Test that docs build successfully with examples enabled."""
        import subprocess

        result = copie.copy(extra_answers={"include_examples": True})
        assert result.exit_code == 0

        # Try to build docs
        build_result = subprocess.run(
            ["uvx", "nox", "-s", "build_docs"],
            cwd=result.project_dir,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        assert build_result.returncode == 0, f"Docs build failed: {build_result.stderr}"

        # Check that site was generated
        site_dir = result.project_dir / "site"
        assert site_dir.is_dir()
        assert (site_dir / "index.html").is_file()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_docs_build_succeeds_without_examples(self, copie):
        """Test that docs build successfully without examples."""
        import subprocess

        result = copie.copy(extra_answers={"include_examples": False})
        assert result.exit_code == 0

        # Try to build docs
        build_result = subprocess.run(
            ["uvx", "nox", "-s", "build_docs"],
            cwd=result.project_dir,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        assert build_result.returncode == 0, f"Docs build failed: {build_result.stderr}"

        # Check that site was generated
        site_dir = result.project_dir / "site"
        assert site_dir.is_dir()
        assert (site_dir / "index.html").is_file()
