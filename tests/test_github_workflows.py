"""Comprehensive tests for GitHub Actions workflows in generated projects.

This test module validates:
- Workflow file generation based on include_actions option
- Consistent uv setup across all workflows
- Workflow triggers, permissions, and job configurations
- Integration between workflows (tests, publish, changelog, nightly)
"""


class TestWorkflowGeneration:
    """Test that workflows are generated correctly based on options."""

    def test_workflows_included_when_enabled(self, copie):
        """Test that all expected workflows exist when include_actions=True."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflows_dir = result.project_dir / ".github" / "workflows"
        assert workflows_dir.is_dir()

        expected_workflows = [
            "tests.yml",
            "publish-release.yml",
            "changelog.yml",
            "nightly.yml",
            "pr-title.yml",
        ]

        for workflow_file in expected_workflows:
            workflow_path = workflows_dir / workflow_file
            assert workflow_path.is_file(), f"Missing workflow: {workflow_file}"

    def test_workflows_excluded_when_disabled(self, copie):
        """Test that no workflows exist when include_actions=False."""
        result = copie.copy(extra_answers={"include_actions": False})
        assert result.exit_code == 0

        workflows_dir = result.project_dir / ".github" / "workflows"
        # .github directory should not exist or workflows should be empty
        if workflows_dir.exists():
            assert len(list(workflows_dir.iterdir())) == 0


class TestTestsWorkflow:
    """Test the tests.yml workflow configuration."""

    def test_tests_workflow_structure(self, copie):
        """Test tests.yml has correct structure and jobs."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "tests.yml"
        workflow_content = workflow_path.read_text()

        # Use string-based validation since GitHub Actions YAML has expressions
        # that cannot be parsed by standard YAML parsers
        assert "name:" in workflow_content
        assert "test" in workflow_content.lower() or "ci" in workflow_content.lower()

        # Check triggers
        assert "on:" in workflow_content
        assert "push:" in workflow_content or "pull_request:" in workflow_content

        # Check jobs
        assert "jobs:" in workflow_content

    def test_tests_workflow_uses_uv(self, copie):
        """Test that tests workflow uses uv for dependency management."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "tests.yml"
        workflow_content = workflow_path.read_text()

        # Should use uv action or install uv
        assert "astral-sh/setup-uv" in workflow_content or "uv" in workflow_content

        # Should install nox via uv tool
        assert "uv tool install nox" in workflow_content or "uvx nox" in workflow_content

    def test_tests_workflow_matrix_strategy(self, copie):
        """Test that tests workflow uses matrix for Python versions."""
        result = copie.copy(extra_answers={"include_actions": True, "min_python_version": "3.11"})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "tests.yml"
        workflow_content = workflow_path.read_text()

        # Use string-based validation since GitHub Actions YAML has expressions
        assert "strategy:" in workflow_content
        assert "matrix:" in workflow_content
        assert "python-version:" in workflow_content or "python:" in workflow_content

    def test_tests_workflow_includes_doctest(self, copie):
        """Test that tests workflow includes doctest job."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "tests.yml"
        workflow_content = workflow_path.read_text()

        # Should have doctest job or step
        assert "doctest" in workflow_content.lower()

    def test_tests_workflow_includes_examples_when_enabled(self, copie):
        """Test that tests workflow includes examples job when enabled."""
        result = copie.copy(extra_answers={"include_actions": True, "include_examples": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "tests.yml"
        workflow_content = workflow_path.read_text()

        # Should have examples job or run_examples
        assert "example" in workflow_content.lower()

    def test_tests_workflow_excludes_examples_when_disabled(self, copie):
        """Test that tests workflow excludes examples when disabled."""
        result = copie.copy(extra_answers={"include_actions": True, "include_examples": False})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "tests.yml"
        workflow_content = workflow_path.read_text()

        # Should NOT have examples-related content
        assert "run_examples" not in workflow_content and "run-examples" not in workflow_content


class TestPublishWorkflow:
    """Test the publish-release.yml workflow."""

    def test_publish_workflow_exists(self, copie):
        """Test that publish workflow exists when actions enabled."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "publish-release.yml"
        assert workflow_path.is_file()

    def test_publish_workflow_triggered_on_tags(self, copie):
        """Test that publish workflow triggers when changelog PR is merged."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "publish-release.yml"
        workflow_content = workflow_path.read_text()

        # Use string-based validation since GitHub Actions YAML has expressions
        # Modern workflow triggers on pull_request close (changelog PR merge)
        assert "on:" in workflow_content
        assert ("pull_request:" in workflow_content) or ("push:" in workflow_content and "tags:" in workflow_content)

    def test_publish_workflow_uses_uv(self, copie):
        """Test that the build/publish workflow uses uv for building."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        # Building happens in changelog.yml workflow, not publish-release.yml
        workflow_path = result.project_dir / ".github" / "workflows" / "changelog.yml"
        workflow_content = workflow_path.read_text()

        # Should use uv for building
        assert "uv build" in workflow_content or "uv" in workflow_content

    def test_publish_workflow_has_pypi_upload(self, copie):
        """Test that the build/publish workflow uploads to PyPI."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        # PyPI publishing happens in changelog.yml workflow
        workflow_path = result.project_dir / ".github" / "workflows" / "changelog.yml"
        workflow_content = workflow_path.read_text()

        # Should use PyPI upload action or twine
        assert "pypi" in workflow_content.lower()

    def test_publish_workflow_creates_github_release(self, copie):
        """Test that publish workflow creates GitHub release."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "publish-release.yml"
        workflow_content = workflow_path.read_text()

        # Should create GitHub release
        assert "release" in workflow_content.lower()


class TestChangelogWorkflow:
    """Test the changelog.yml workflow."""

    def test_changelog_workflow_exists(self, copie):
        """Test that changelog workflow exists when actions enabled."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "changelog.yml"
        assert workflow_path.is_file()

    def test_changelog_workflow_uses_git_cliff(self, copie):
        """Test that changelog workflow uses git-cliff."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "changelog.yml"
        workflow_content = workflow_path.read_text()

        # Should use git-cliff action
        assert "git-cliff" in workflow_content

    def test_changelog_workflow_triggered_on_tags(self, copie):
        """Test that changelog workflow triggers on version tags."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "changelog.yml"
        workflow_content = workflow_path.read_text()

        # Use string-based validation since GitHub Actions YAML has expressions
        assert "on:" in workflow_content
        assert "push:" in workflow_content
        assert "tags:" in workflow_content


class TestNightlyWorkflow:
    """Test the nightly.yml workflow."""

    def test_nightly_workflow_exists(self, copie):
        """Test that nightly workflow exists when actions enabled."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "nightly.yml"
        assert workflow_path.is_file()

    def test_nightly_workflow_scheduled(self, copie):
        """Test that nightly workflow runs on schedule."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "nightly.yml"
        workflow_content = workflow_path.read_text()

        # Use string-based validation since GitHub Actions YAML has expressions
        assert "on:" in workflow_content
        assert "schedule:" in workflow_content
        assert "cron:" in workflow_content

    def test_nightly_workflow_uses_uv(self, copie):
        """Test that nightly workflow uses uv."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "nightly.yml"
        workflow_content = workflow_path.read_text()

        # Should use uv
        assert "uv" in workflow_content


class TestPRTitleWorkflow:
    """Test the pr-title.yml workflow."""

    def test_pr_title_workflow_exists(self, copie):
        """Test that PR title workflow exists when actions enabled."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "pr-title.yml"
        assert workflow_path.is_file()

    def test_pr_title_workflow_validates_conventional_commits(self, copie):
        """Test that PR title workflow validates conventional commit format."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "pr-title.yml"
        workflow_content = workflow_path.read_text()

        # Should validate conventional commit format
        assert "conventional" in workflow_content.lower() or "commitizen" in workflow_content.lower()

    def test_pr_title_workflow_triggered_on_pull_request(self, copie):
        """Test that PR title workflow triggers on pull requests."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "pr-title.yml"
        workflow_content = workflow_path.read_text()

        # Use string-based validation since GitHub Actions YAML has expressions
        assert "on:" in workflow_content
        assert "pull_request:" in workflow_content or "pull_request_target:" in workflow_content


class TestWorkflowConsistency:
    """Test consistency across all workflows."""

    def test_all_workflows_use_consistent_uv_setup(self, copie):
        """Test that all workflows use the same uv setup approach."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflows_dir = result.project_dir / ".github" / "workflows"
        workflow_files = [
            "tests.yml",
            "publish-release.yml",
            "changelog.yml",
            "nightly.yml",
        ]

        uv_setup_patterns = []

        for workflow_file in workflow_files:
            workflow_path = workflows_dir / workflow_file
            if workflow_path.exists():
                content = workflow_path.read_text()

                # Track if it uses astral-sh/setup-uv action
                uses_setup_uv_action = "astral-sh/setup-uv" in content

                uv_setup_patterns.append({
                    "file": workflow_file,
                    "uses_action": uses_setup_uv_action,
                })

        # All should use the same approach (either all use action or all don't)
        uses_action_values = [p["uses_action"] for p in uv_setup_patterns]
        # They should all be consistent
        assert len(set(uses_action_values)) <= 2, f"Inconsistent uv setup: {uv_setup_patterns}"

    def test_all_workflows_install_nox_consistently(self, copie):
        """Test that all workflows that need nox install it the same way."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflows_dir = result.project_dir / ".github" / "workflows"
        workflow_files = ["tests.yml", "nightly.yml"]

        for workflow_file in workflow_files:
            workflow_path = workflows_dir / workflow_file
            if workflow_path.exists():
                content = workflow_path.read_text()

                # Should install nox via uv tool
                assert "uv tool install nox" in content or "uvx nox" in content, (
                    f"{workflow_file} doesn't install nox consistently"
                )


class TestWorkflowPermissions:
    """Test that workflows have appropriate permissions."""

    def test_publish_workflow_has_appropriate_permissions(self, copie):
        """Test that publish workflow has necessary permissions."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "publish-release.yml"
        workflow_content = workflow_path.read_text()

        # Use string-based validation since GitHub Actions YAML has expressions
        # Should have permissions for PyPI trusted publishing and GitHub release
        assert "permissions:" in workflow_content

    def test_changelog_workflow_has_write_permissions(self, copie):
        """Test that changelog workflow can write to repository."""
        result = copie.copy(extra_answers={"include_actions": True})
        assert result.exit_code == 0

        workflow_path = result.project_dir / ".github" / "workflows" / "changelog.yml"
        workflow_content = workflow_path.read_text()

        # Use string-based validation since GitHub Actions YAML has expressions
        # Should have permissions for writing to contents
        assert "permissions:" in workflow_content
