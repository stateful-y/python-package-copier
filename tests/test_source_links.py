"""Tests for the source-link Griffe extension (`docs_build/_source_links.py`).

The extension attaches a "View on GitHub" URL to each documented object at
collection time, which the Source Code heading override renders. It replaces the
HTML post-processing `_add_source_links` did, in a hook-free form. The old
transform had no test; this closes that gap.
"""

import importlib.util
import sys

from _build_layout import BUILD_DIR


def _load_extension(project_dir, suffix):
    """Load the generated `_source_links` extension under a unique module name."""
    sys.modules.pop("_source_links", None)
    spec = importlib.util.spec_from_file_location(
        f"generated_source_links_{suffix}", project_dir / BUILD_DIR / "_source_links.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_package(project_dir, extension_module, package_name):
    import griffe

    extensions = griffe.load_extensions(extension_module.SourceLinkExtension())
    loader = griffe.GriffeLoader(search_paths=[str(project_dir / "src")], extensions=extensions)
    return loader.load(package_name)


def test_source_url_is_attached_from_repo_url_and_relative_path(copie, monkeypatch):
    """Each object gets a repo/blob/ref/<relative path> URL on `obj.extra`.

    The URL is derived from the object's own `relative_filepath` (not a guess
    from the page filename, which the old transform used), and `repo_url` comes
    from mkdocs.yml. No `.git` here, so the ref falls back to `main`.
    """
    result = copie.copy(extra_answers={"include_examples": False, "github_username": "acme", "project_slug": "widget"})
    assert result.exit_code == 0
    project_dir = result.project_dir
    ext = _load_extension(project_dir, "url")

    # The extension reads mkdocs.yml relative to the working directory.
    monkeypatch.chdir(project_dir)
    package = _load_package(project_dir, ext, "test_project")

    url = package["hello.Greeter"].extra["docs"]["github_source_url"]
    assert url == "https://github.com/acme/widget/blob/main/src/test_project/hello.py", url


def test_no_repo_url_means_no_source_urls(copie, monkeypatch):
    """With no `repo_url`, nothing is attached, so the template renders no link."""
    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0
    project_dir = result.project_dir

    # Blank out repo_url in the rendered config, as a project with no remote has.
    mkdocs = project_dir / "mkdocs.yml"
    mkdocs.write_text(
        "\n".join(line for line in mkdocs.read_text(encoding="utf-8").splitlines() if not line.startswith("repo_url:")),
        encoding="utf-8",
    )
    ext = _load_extension(project_dir, "norepo")
    monkeypatch.chdir(project_dir)
    package = _load_package(project_dir, ext, "test_project")

    assert "github_source_url" not in package["hello.Greeter"].extra.get("docs", {})
