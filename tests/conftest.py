"""Pytest configuration for template tests."""

from pathlib import Path

import pytest
from copier import run_copy


class CopierTestFixture:
    """Helper class for testing copier templates."""

    def __init__(self, template_dir: Path, tmp_path: Path):
        self.template_dir = template_dir
        self.tmp_path = tmp_path

    def copy(self, extra_answers: dict | None = None):
        """Copy the template with given answers."""
        project_dir = self.tmp_path / "test-project"

        # Default answers
        answers = {
            "project_name": "Test Project",
            "project_slug": "test-project",
            "package_name": "test_project",
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

        # Override with extra answers
        if extra_answers:
            answers.update(extra_answers)

        # Run copier - use HEAD to get latest changes
        result = run_copy(
            str(self.template_dir),
            str(project_dir),
            data=answers,
            defaults=True,
            overwrite=True,
            unsafe=True,
            vcs_ref="HEAD",
        )

        return CopierResult(project_dir=project_dir, result=result)


class CopierResult:
    """Result of a copier template copy operation."""

    def __init__(self, project_dir: Path, result):
        self.project_dir = project_dir
        self.result = result
        self.exit_code = 0 if project_dir.exists() else 1
        self.exception = None


@pytest.fixture
def copie(tmp_path):
    """Fixture that provides a copier test helper."""
    template_dir = Path(__file__).parent.parent
    return CopierTestFixture(template_dir, tmp_path)


@pytest.fixture
def copie_custom_values(tmp_path):
    """Fixture that provides a copier helper with custom (non-default) values.

    Useful for testing that template variables propagate correctly
    when users provide their own values.
    """
    template_dir = Path(__file__).parent.parent
    fixture = CopierTestFixture(template_dir, tmp_path)

    # Pre-configured with custom values
    fixture.custom_answers = {
        "project_name": "Custom Package",
        "package_name": "custom_package",
        "project_slug": "custom-package",
        "version": "1.5.0",
        "description": "A custom package for advanced testing scenarios",
        "author_name": "Dr. Jane Doe",
        "author_email": "jane.doe@research.org",
        "github_username": "research-lab",
        "license": "Apache-2.0",
        "min_python_version": "3.12",
        "include_actions": True,
        "include_examples": True,
    }

    return fixture


@pytest.fixture
def copie_edge_cases(tmp_path):
    """Fixture that provides a copier helper with edge case values.

    Tests empty strings, unicode, and special characters to ensure
    robust template handling.
    """
    template_dir = Path(__file__).parent.parent
    fixture = CopierTestFixture(template_dir, tmp_path)

    # Pre-configured with edge case values
    fixture.edge_case_answers = {
        "project_name": "Test Project 🚀",
        "description": "",  # Empty description
        "author_name": "José García-López",  # Unicode
        "author_email": "test+alias@example.com",  # Plus sign
        "github_username": "",  # Empty GitHub username
        "license": "MIT",
        "min_python_version": "3.11",
        "include_actions": True,
        "include_examples": False,
    }

    return fixture


@pytest.fixture
def copie_minimal(tmp_path):
    """Fixture that provides minimal configuration (all optional features disabled).

    Useful for testing the minimal viable generated project.
    """
    template_dir = Path(__file__).parent.parent
    fixture = CopierTestFixture(template_dir, tmp_path)

    fixture.minimal_answers = {
        "project_name": "Minimal Project",
        "description": "",
        "author_name": "Test Author",
        "author_email": "test@example.com",
        "github_username": "",
        "license": "MIT",
        "min_python_version": "3.11",
        "include_actions": False,
        "include_examples": False,
    }

    return fixture


# Constants for test configuration
SUBPROCESS_TIMEOUT = 120  # Timeout for subprocess tests in seconds
INTEGRATION_TEST_MARKER = "integration"  # Marker for integration tests
SLOW_TEST_MARKER = "slow"  # Marker for slow tests
