"""Single source of truth for where a generated project's docs build tooling lives.

The build modules (``build.py`` and its siblings) live in ``docs_build/``, a
sibling of ``docs/``, rather than under ``docs/`` itself. They moved there so
they sit outside ``docs_dir`` and cannot be published as static assets: mkdocs
copies every non-page file under ``docs_dir`` into the site, and the successor
engine ignores the ``exclude_docs`` key that used to suppress that.

Every test that constructs a path to a build module routes through here, so the
next relocation is one edit instead of another few dozen.
"""

BUILD_DIR = "docs_build"


def build_module(project_dir, name):
    """Path to a build-tooling module in a generated project.

    ``name`` is a bare filename, e.g. ``"build.py"`` or ``"_api_pages.py"``.
    """
    return project_dir / BUILD_DIR / name
