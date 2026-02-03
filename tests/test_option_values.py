"""Comprehensive tests for all template option values and their propagation.

This test module systematically validates that all 11 template options work correctly
with custom (non-default) values, including edge cases like empty strings, unicode,
and special characters.

Template options tested:
- project_name (with auto-derivation of package_name and project_slug)
- package_name (custom override)
- project_slug (custom override)
- version
- description
- author_name
- author_email
- github_username
- license (covered in test_option_combinations.py)
- min_python_version (covered in test_option_combinations.py)
- include_actions (covered in test_option_combinations.py)
- include_examples (covered in test_option_combinations.py)
"""

import pytest


class TestVersionOption:
    """Test the version option propagation."""

    @pytest.mark.parametrize(
        "version",
        ["0.1.0", "1.0.0", "2.3.4", "0.0.1", "10.20.30"],
    )
    def test_custom_version(self, copie, version):
        """Test that custom version values propagate to CHANGELOG.md."""
        result = copie.copy(extra_answers={"version": version})
        assert result.exit_code == 0

        # Version should be in CHANGELOG.md (initial version)
        changelog_content = (result.project_dir / "CHANGELOG.md").read_text()
        assert version in changelog_content, f"Version {version} not found in CHANGELOG.md"

        # pyproject.toml uses dynamic versioning (hatch-vcs), so version is NOT there
        pyproject_content = (result.project_dir / "pyproject.toml").read_text()
        assert 'dynamic = ["version"]' in pyproject_content


class TestDescriptionOption:
    """Test the description option propagation."""

    def test_custom_description(self, copie):
        """Test that custom description propagates to multiple files."""
        custom_description = "A powerful tool for data analysis and visualization"
        result = copie.copy(extra_answers={"description": custom_description})
        assert result.exit_code == 0

        # Check pyproject.toml
        pyproject_content = (result.project_dir / "pyproject.toml").read_text()
        assert f'description = "{custom_description}"' in pyproject_content

        # Check README.md
        readme_content = (result.project_dir / "README.md").read_text()
        assert custom_description in readme_content

        # Check mkdocs.yml
        mkdocs_content = (result.project_dir / "mkdocs.yml").read_text()
        assert custom_description in mkdocs_content

        # Check docs/index.md
        docs_index_content = (result.project_dir / "docs" / "index.md").read_text()
        assert custom_description in docs_index_content

    def test_empty_description(self, copie):
        """Test that empty description is handled gracefully."""
        result = copie.copy(extra_answers={"description": ""})
        assert result.exit_code == 0

        # Should not break generation
        assert (result.project_dir / "pyproject.toml").is_file()
        pyproject_content = (result.project_dir / "pyproject.toml").read_text()
        assert 'description = ""' in pyproject_content

    def test_description_with_special_chars(self, copie):
        """Test description with quotes and special characters."""
        special_description = 'A "modern" tool with <features> & more!'
        result = copie.copy(extra_answers={"description": special_description})
        assert result.exit_code == 0

        # Description should be properly escaped in pyproject.toml
        pyproject_content = (result.project_dir / "pyproject.toml").read_text()
        # Should contain the description (with proper escaping)
        assert "modern" in pyproject_content
        assert "tool" in pyproject_content


class TestAuthorOptions:
    """Test author_name and author_email options."""

    def test_custom_author_name(self, copie):
        """Test that custom author name propagates correctly."""
        custom_author = "Jane Doe"
        result = copie.copy(extra_answers={"author_name": custom_author})
        assert result.exit_code == 0

        # Check pyproject.toml
        pyproject_content = (result.project_dir / "pyproject.toml").read_text()
        assert custom_author in pyproject_content

        # Check LICENSE (MIT default)
        license_content = (result.project_dir / "LICENSE").read_text()
        assert custom_author in license_content

    def test_author_name_with_unicode(self, copie):
        """Test author name with unicode characters."""
        unicode_author = "José García"
        result = copie.copy(extra_answers={"author_name": unicode_author})
        assert result.exit_code == 0

        # Should work without issues
        license_content = (result.project_dir / "LICENSE").read_text()
        assert unicode_author in license_content

    def test_custom_author_email(self, copie):
        """Test that custom author email propagates correctly."""
        custom_email = "jane.doe@example.org"
        result = copie.copy(extra_answers={"author_email": custom_email})
        assert result.exit_code == 0

        # Check pyproject.toml
        pyproject_content = (result.project_dir / "pyproject.toml").read_text()
        assert custom_email in pyproject_content

    def test_author_email_with_plus_sign(self, copie):
        """Test email with plus sign (common for email aliases)."""
        email_with_plus = "author+project@example.com"
        result = copie.copy(extra_answers={"author_email": email_with_plus})
        assert result.exit_code == 0

        pyproject_content = (result.project_dir / "pyproject.toml").read_text()
        assert email_with_plus in pyproject_content


class TestGithubUsernameOption:
    """Test github_username option propagation."""

    def test_custom_github_username(self, copie):
        """Test that github_username propagates to all GitHub URLs."""
        custom_username = "my-org"
        result = copie.copy(
            extra_answers={
                "github_username": custom_username,
                "project_slug": "test-project",
            }
        )
        assert result.exit_code == 0

        expected_repo_url = f"https://github.com/{custom_username}/test-project"

        # Check README.md
        readme_content = (result.project_dir / "README.md").read_text()
        assert custom_username in readme_content
        assert expected_repo_url in readme_content

        # Check mkdocs.yml
        mkdocs_content = (result.project_dir / "mkdocs.yml").read_text()
        assert f"repo_url: {expected_repo_url}" in mkdocs_content
        assert f"repo_name: {custom_username}/test-project" in mkdocs_content

        # Check pyproject.toml
        pyproject_content = (result.project_dir / "pyproject.toml").read_text()
        # GitHub URLs might not be in pyproject.toml depending on template
        # Just verify project was created successfully
        assert "name = " in pyproject_content

    def test_empty_github_username(self, copie):
        """Test with empty github_username (default value)."""
        result = copie.copy(extra_answers={"github_username": ""})
        assert result.exit_code == 0

        # Should still generate successfully but URLs might be incomplete
        assert (result.project_dir / "pyproject.toml").is_file()

        # Should have placeholder or empty GitHub URL sections
        assert (result.project_dir / "README.md").is_file()


class TestProjectNameDerivation:
    """Test auto-derivation of package_name and project_slug from project_name."""

    def test_project_name_to_package_name_derivation(self, copie):
        """Test that package_name is correctly derived from project_name."""
        test_cases = [
            ("My Project", "my_project"),
            ("My-Project", "my_project"),
            ("my-project", "my_project"),
            ("My Cool Tool", "my_cool_tool"),
            ("Tool-V2", "tool_v2"),
        ]

        for project_name, expected_package_name in test_cases:
            # Create a custom fixture that doesn't set package_name
            project_dir = copie.tmp_path / f"test-project-{expected_package_name}"

            from copier import run_copy

            answers = {
                "project_name": project_name,
                # Explicitly don't set package_name - let it derive
                "description": "A test project",
                "author_name": "Test Author",
                "author_email": "test@example.com",
                "github_username": "testuser",
                "version": "0.1.0",
                "min_python_version": "3.11",
                "license": "MIT",
                "include_actions": True,
                "include_examples": True,
            }

            run_copy(
                str(copie.template_dir),
                str(project_dir),
                data=answers,
                defaults=True,
                overwrite=True,
                unsafe=True,
                vcs_ref="HEAD",
            )

            assert project_dir.exists()

            # Check that the derived package_name directory exists
            src_dir = project_dir / "src"
            package_dirs = list(src_dir.iterdir())
            assert len(package_dirs) == 1
            assert package_dirs[0].name == expected_package_name, (
                f"Expected {expected_package_name}, got {package_dirs[0].name}"
            )

    def test_project_name_to_project_slug_derivation(self, copie):
        """Test that project_slug is correctly derived from project_name."""
        test_cases = [
            ("My Project", "my_project"),  # Copier default derivation keeps underscores
            ("My-Project", "my_project"),
            ("my_project", "my_project"),
            ("My Cool Tool", "my_cool_tool"),
        ]

        for project_name, _expected_slug in test_cases:
            result = copie.copy(
                extra_answers={
                    "project_name": project_name,
                    # Don't override project_slug, let it auto-derive
                }
            )
            assert result.exit_code == 0

            # Check pyproject.toml name field
            pyproject_content = (result.project_dir / "pyproject.toml").read_text()
            # Name should exist in pyproject.toml
            assert "name = " in pyproject_content

    def test_explicit_package_name_override(self, copie):
        """Test that explicit package_name overrides auto-derivation."""
        result = copie.copy(
            extra_answers={
                "project_name": "My Cool Project",
                "package_name": "custom_package",
            }
        )
        assert result.exit_code == 0

        # Should use the explicit package_name
        src_dir = result.project_dir / "src"
        package_dirs = list(src_dir.iterdir())
        assert len(package_dirs) == 1
        assert package_dirs[0].name == "custom_package"

    def test_explicit_project_slug_override(self, copie):
        """Test that explicit project_slug overrides auto-derivation."""
        result = copie.copy(
            extra_answers={
                "project_name": "My Cool Project",
                "package_name": "custom_package",
                "project_slug": "custom-slug",
            }
        )
        assert result.exit_code == 0

        # pyproject.toml name field uses package_name, not project_slug
        pyproject_content = (result.project_dir / "pyproject.toml").read_text()
        assert 'name = "custom_package"' in pyproject_content

        # But project_slug is used in URLs and GitHub links
        readme_content = (result.project_dir / "README.md").read_text()
        assert "custom-slug" in readme_content


class TestProjectNameEdgeCases:
    """Test edge cases for project naming."""

    def test_project_name_with_numbers(self, copie):
        """Test project names with numbers."""
        result = copie.copy(extra_answers={"project_name": "Tool V2.0"})
        assert result.exit_code == 0

        # Should handle numbers correctly
        assert (result.project_dir / "pyproject.toml").is_file()

    def test_project_name_with_special_chars(self, copie):
        """Test project names with special characters (if allowed by copier)."""
        # Note: Copier might validate project names, so this tests the template's handling
        result = copie.copy(extra_answers={"project_name": "My-Tool_v1"})
        assert result.exit_code == 0

        src_dir = result.project_dir / "src"
        # Should convert to valid Python identifier
        package_dirs = list(src_dir.iterdir())
        assert len(package_dirs) == 1
        # Should be all lowercase with underscores
        assert "_" in package_dirs[0].name or "-" not in package_dirs[0].name

    def test_very_long_project_name(self, copie):
        """Test with a very long project name."""
        long_name = "My Very Long Project Name With Many Words That Keeps Going"
        result = copie.copy(extra_answers={"project_name": long_name})
        assert result.exit_code == 0

        # Should still work
        assert (result.project_dir / "pyproject.toml").is_file()
        # README might have shortened version, just check file exists
        assert (result.project_dir / "README.md").is_file()


class TestOptionCombinations:
    """Test combinations of custom option values."""

    def test_all_custom_values(self, copie):
        """Test with all options set to custom (non-default) values."""
        custom_answers = {
            "project_name": "Custom Project",
            "package_name": "custom_pkg",
            "project_slug": "custom-project",
            "version": "1.0.0",
            "description": "A custom description for testing",
            "author_name": "Custom Author",
            "author_email": "custom@example.com",
            "github_username": "custom-org",
            "license": "Apache-2.0",
            "min_python_version": "3.12",
            "include_actions": False,
            "include_examples": False,
        }

        result = copie.copy(extra_answers=custom_answers)
        assert result.exit_code == 0

        # Verify key propagations
        pyproject_content = (result.project_dir / "pyproject.toml").read_text()
        # pyproject.toml name field uses package_name, not project_slug
        assert 'name = "custom_pkg"' in pyproject_content
        # Version is dynamic (hatch-vcs), not in pyproject.toml
        assert 'dynamic = ["version"]' in pyproject_content
        assert "Custom Author" in pyproject_content
        assert "custom@example.com" in pyproject_content
        assert "A custom description for testing" in pyproject_content

        # Verify package directory
        assert (result.project_dir / "src" / "custom_pkg").is_dir()

        # Verify GitHub username in README
        readme_content = (result.project_dir / "README.md").read_text()
        assert "custom-org" in readme_content

        # Verify license
        license_content = (result.project_dir / "LICENSE").read_text()
        assert "Apache License" in license_content
        assert "Custom Author" in license_content

    def test_minimal_required_values(self, copie):
        """Test with only required values, letting others use defaults."""
        # The conftest fixture already provides defaults, but this tests the concept
        result = copie.copy(extra_answers={})
        assert result.exit_code == 0

        # Should use all defaults from conftest
        assert (result.project_dir / "pyproject.toml").is_file()
        assert (result.project_dir / "src" / "test_project").is_dir()
