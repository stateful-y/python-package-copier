"""Tests for features propagated from yohou PR #18.

Validates: MathJax, stylesheets, rumdl, autorefs, hypothesis,
API auto-gen, gallery system, justfile recipes, lfs, and bug fixes.
"""


class TestPyprojectNewDeps:
    """Test new dependencies in pyproject.toml."""

    def test_hypothesis_in_tests_group(self, copie_session_default):
        """Test that hypothesis is in the tests dependency group."""
        result = copie_session_default
        content = (result.project_dir / "pyproject.toml").read_text()
        assert '"hypothesis>=' in content

    def test_mkdocs_autorefs_in_docs_group(self, copie_session_default):
        """Test that mkdocs-autorefs is in the docs dependency group."""
        result = copie_session_default
        content = (result.project_dir / "pyproject.toml").read_text()
        assert '"mkdocs-autorefs>=' in content

    def test_rumdl_config_present(self, copie_session_default):
        """Test that [tool.rumdl] section exists in pyproject.toml."""
        result = copie_session_default
        content = (result.project_dir / "pyproject.toml").read_text()
        assert "[tool.rumdl]" in content
        assert 'flavor = "mkdocs"' in content
        assert '"MD013"' in content  # disabled rule
        assert '"MD033"' in content
        assert "[tool.rumdl.per-file-ignores]" in content

    def test_ruff_docs_per_file_ignores_expanded(self, copie_session_default):
        """Test that ruff per-file-ignores for docs/ includes PLW0603, SIM105, SIM108."""
        result = copie_session_default
        content = (result.project_dir / "pyproject.toml").read_text()
        assert "PLW0603" in content
        assert "SIM105" in content
        assert "SIM108" in content


class TestMkdocsYmlFeatures:
    """Test new mkdocs.yml features."""

    def test_navigation_indexes_feature(self, copie_session_default):
        """Test that navigation.indexes feature is enabled."""
        result = copie_session_default
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "navigation.indexes" in content

    def test_navigation_prune_feature(self, copie_session_default):
        """Test that navigation.prune feature is enabled."""
        result = copie_session_default
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "navigation.prune" in content

    def test_autorefs_plugin(self, copie_session_default):
        """Test that autorefs plugin is configured."""
        result = copie_session_default
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "autorefs" in content

    def test_mathjax_javascript(self, copie_session_default):
        """Test that MathJax JavaScript is included."""
        result = copie_session_default
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "mathjax.js" in content
        assert "tex-mml-chtml.js" in content  # MathJax CDN

    def test_extra_css_theme(self, copie_session_default):
        """Test that theme.css is always in extra_css."""
        result = copie_session_default
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "stylesheets/theme.css" in content

    def test_extra_css_gallery_when_examples(self, copie):
        """Test that gallery.css is in extra_css when include_examples=True."""
        result = copie.copy(extra_answers={"include_examples": True})
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "stylesheets/gallery.css" in content

    def test_extra_css_no_gallery_when_no_examples(self, copie):
        """Test that gallery.css is NOT in extra_css when include_examples=False."""
        result = copie.copy(extra_answers={"include_examples": False})
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "stylesheets/gallery.css" not in content

    def test_mkdocstrings_crossrefs(self, copie_session_default):
        """Test that mkdocstrings cross-reference options are configured."""
        result = copie_session_default
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "signature_crossrefs: true" in content
        assert "scoped_crossrefs: true" in content
        assert "relative_crossrefs: true" in content

    def test_not_in_nav_block(self, copie_session_default):
        """Test that not_in_nav block exists with API wildcard."""
        result = copie_session_default
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "not_in_nav" in content
        assert "pages/api/*.md" in content

    def test_exclude_docs_has_api_submodule(self, copie_session_default):
        """Test that exclude_docs excludes api-submodule.html."""
        result = copie_session_default
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "api-submodule.html" in content

    def test_nav_uses_api_reference(self, copie_session_default):
        """Test that nav points to pages/api-reference.md."""
        result = copie_session_default
        content = (result.project_dir / "mkdocs.yml").read_text()
        assert "pages/api-reference.md" in content


class TestAPISubmodulePages:
    """Test API submodule page generation infrastructure."""

    def test_api_submodule_template_exists(self, copie_session_default):
        """Test that api-submodule.html template file exists."""
        result = copie_session_default
        template = result.project_dir / "docs" / "api-submodule.html"
        assert template.is_file()

    def test_api_submodule_template_has_placeholders(self, copie_session_default):
        """Test that api-submodule.html has the expected placeholders."""
        result = copie_session_default
        content = (result.project_dir / "docs" / "api-submodule.html").read_text()
        assert "{package_name}" in content
        assert "{module_name}" in content
        assert "{module_doc}" in content
        assert "{members_tables}" in content

    def test_api_index_has_table_placeholder(self, copie_session_default):
        """Test that API reference page has the API_TABLE placeholder."""
        result = copie_session_default
        content = (result.project_dir / "docs" / "pages" / "api-reference.md").read_text()
        assert "<!-- API_TABLE -->" in content
        assert "# API Reference" in content

    def test_hooks_has_api_discovery_functions(self, copie_session_default):
        """Test that hooks.py has API submodule discovery functions."""
        result = copie_session_default
        content = (result.project_dir / "docs" / "hooks.py").read_text()
        assert "_get_submodules" in content
        assert "_generate_api_pages" in content
        assert "_build_api_table_html" in content
        assert "_extract_module_docstring" in content
        assert "_get_module_members" in content
        assert "_build_members_tables" in content

    def test_hooks_on_pre_build_generates_api_pages(self, copie_session_default):
        """Test that on_pre_build always exists for API page generation."""
        result = copie_session_default
        content = (result.project_dir / "docs" / "hooks.py").read_text()
        assert "on_pre_build" in content
        assert "_generate_api_pages" in content

    def test_gitignore_excludes_generated_api_pages(self, copie_session_default):
        """Test that .gitignore excludes generated API pages."""
        result = copie_session_default
        content = (result.project_dir / ".gitignore").read_text()
        assert "docs/pages/api/" in content


class TestNewStaticFiles:
    """Test newly created static files."""

    def test_mathjax_js_exists(self, copie_session_default):
        """Test that mathjax.js exists with correct content."""
        result = copie_session_default
        mathjax = result.project_dir / "docs" / "javascripts" / "mathjax.js"
        assert mathjax.is_file()
        content = mathjax.read_text()
        assert "MathJax" in content
        assert "document$.subscribe" in content

    def test_theme_css_exists(self, copie_session_default):
        """Test that theme.css exists with CSS custom properties."""
        result = copie_session_default
        theme_css = result.project_dir / "docs" / "stylesheets" / "theme.css"
        assert theme_css.is_file()
        content = theme_css.read_text()
        assert "--md-primary-fg-color" in content
        assert "--md-accent-fg-color" in content

    def test_gallery_css_when_examples(self, copie):
        """Test that gallery.css exists when include_examples=True."""
        result = copie.copy(extra_answers={"include_examples": True})
        gallery_css = result.project_dir / "docs" / "stylesheets" / "gallery.css"
        assert gallery_css.is_file()
        content = gallery_css.read_text()
        assert "grid-template-columns" in content

    def test_no_gallery_css_when_no_examples(self, copie):
        """Test that gallery.css does NOT exist when include_examples=False."""
        result = copie.copy(extra_answers={"include_examples": False})
        gallery_css = result.project_dir / "docs" / "stylesheets" / "gallery.css"
        assert not gallery_css.exists()


class TestGallerySystem:
    """Test gallery system (conditional on include_examples)."""

    def test_examples_page_has_gallery_placeholder(self, copie):
        """Test that examples.md uses the GALLERY placeholder."""
        result = copie.copy(extra_answers={"include_examples": True})
        content = (result.project_dir / "docs" / "pages" / "examples.md").read_text()
        assert "<!-- GALLERY -->" in content

    def test_hello_notebook_has_gallery_metadata(self, copie):
        """Test that hello.py has __gallery__ metadata."""
        result = copie.copy(extra_answers={"include_examples": True})
        content = (result.project_dir / "examples" / "hello.py").read_text()
        assert "__gallery__" in content
        assert '"title"' in content
        assert '"description"' in content

    def test_hooks_has_gallery_functions_when_examples(self, copie):
        """Test that hooks.py includes gallery functions when examples enabled."""
        result = copie.copy(extra_answers={"include_examples": True})
        content = (result.project_dir / "docs" / "hooks.py").read_text()
        assert "_get_gallery_items" in content
        assert "_build_gallery_html" in content

    def test_hooks_no_gallery_when_no_examples(self, copie):
        """Test that hooks.py omits gallery functions when examples disabled."""
        result = copie.copy(extra_answers={"include_examples": False})
        content = (result.project_dir / "docs" / "hooks.py").read_text()
        assert "_get_gallery_items" not in content
        assert "_build_gallery_html" not in content


class TestJustfileRecipes:
    """Test new justfile recipes."""

    def test_lint_includes_rumdl(self, copie_session_default):
        """Test that lint recipe includes rumdl."""
        result = copie_session_default
        content = (result.project_dir / "justfile").read_text()
        assert "rumdl" in content

    def test_link_recipe_exists(self, copie_session_default):
        """Test that link recipe exists for linkchecker."""
        result = copie_session_default
        content = (result.project_dir / "justfile").read_text()
        assert "linkchecker" in content
        assert "link:" in content

    def test_build_fast_when_examples(self, copie):
        """Test that build-fast recipe exists when examples enabled."""
        result = copie.copy(extra_answers={"include_examples": True})
        content = (result.project_dir / "justfile").read_text()
        assert "build-fast:" in content
        assert "MKDOCS_SKIP_NOTEBOOKS" in content

    def test_serve_fast_when_examples(self, copie):
        """Test that serve-fast recipe exists when examples enabled."""
        result = copie.copy(extra_answers={"include_examples": True})
        content = (result.project_dir / "justfile").read_text()
        assert "serve-fast:" in content

    def test_no_build_fast_when_no_examples(self, copie):
        """Test that build-fast/serve-fast are absent when examples disabled."""
        result = copie.copy(extra_answers={"include_examples": False})
        content = (result.project_dir / "justfile").read_text()
        assert "build-fast:" not in content
        assert "serve-fast:" not in content


class TestPreCommitRumdl:
    """Test rumdl pre-commit hook."""

    def test_precommit_has_rumdl(self, copie_session_default):
        """Test that pre-commit config includes rumdl hook."""
        result = copie_session_default
        content = (result.project_dir / ".pre-commit-config.yaml").read_text()
        assert "rumdl" in content


class TestNoxfileChanges:
    """Test noxfile.py changes."""

    def test_nox_lint_includes_rumdl(self, copie_session_default):
        """Test that nox lint session runs rumdl."""
        result = copie_session_default
        content = (result.project_dir / "noxfile.py").read_text()
        assert "rumdl" in content

    def test_nox_link_docs_session(self, copie_session_default):
        """Test that nox link_docs session exists."""
        result = copie_session_default
        content = (result.project_dir / "noxfile.py").read_text()
        assert "link_docs" in content
        assert "linkchecker" in content


class TestWorkflowFixes:
    """Test workflow bug fixes and improvements."""

    def test_tests_yml_no_undefined_python_version(self, copie):
        """Test that tests.yml lint job no longer uses undefined {{ python_version }}."""
        result = copie.copy(extra_answers={"include_actions": True})
        content = (result.project_dir / ".github" / "workflows" / "tests.yml").read_text()

        # The lint job should use 'uv python install' (no version arg)
        # not 'uv python install <undefined>'
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "Set up Python" in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith("run: uv python install"):
                    # Should be exactly 'uv python install' for lint step
                    # or 'uv python install ${{ matrix.python-version }}' for matrix steps
                    assert "python_version" not in next_line or "${{" in next_line

    def test_tests_yml_has_lfs(self, copie):
        """Test that checkout steps in tests.yml have lfs: true."""
        result = copie.copy(extra_answers={"include_actions": True})
        content = (result.project_dir / ".github" / "workflows" / "tests.yml").read_text()
        assert "lfs: true" in content


class TestPRTemplate:
    """Test PR template fixes."""

    def test_pr_template_uses_just_fix(self, copie):
        """Test that PR template references 'just fix' not 'just format'."""
        result = copie.copy(extra_answers={"include_actions": True})
        content = (result.project_dir / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text()
        assert "just fix" in content
        assert "just format" not in content

    def test_pr_template_uses_just_lint(self, copie):
        """Test that PR template references 'just lint' not 'just check'."""
        result = copie.copy(extra_answers={"include_actions": True})
        content = (result.project_dir / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text()
        assert "just lint" in content
        assert "just check" not in content


class TestContributingFix:
    """Test contributing.md fix."""

    def test_contributing_uses_min_python_version(self, copie):
        """Test that contributing.md uses min_python_version, not undefined python_version."""
        result = copie.copy(extra_answers={"min_python_version": "3.12"})
        content = (result.project_dir / "docs" / "pages" / "contributing.md").read_text()
        assert "Python 3.12+" in content


class TestHooksSkipNotebooks:
    """Test MKDOCS_SKIP_NOTEBOOKS support."""

    def test_hooks_supports_skip_notebooks(self, copie):
        """Test that hooks.py checks MKDOCS_SKIP_NOTEBOOKS env var."""
        result = copie.copy(extra_answers={"include_examples": True})
        content = (result.project_dir / "docs" / "hooks.py").read_text()
        assert "MKDOCS_SKIP_NOTEBOOKS" in content
