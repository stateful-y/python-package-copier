"""Engine-independence invariants for THIS repository's own documentation.

The `docs-engine-portability` change made the docs this template *generates* for
downstream projects survive a migration off Material for MkDocs (EOL 2026-11-05)
to Zensical. This pins the same guarantee for the docs this repo publishes about
*itself* -- the root `mkdocs.yml` and `docs/`.

These docs are pure prose plus the Material theme: no `hooks:`, no markers, no
mkdocstrings rendering, no build-step modules. So the guarantee is mostly
"already true", and most of these assertions pin an invariant rather than test a
fix -- they fail loudly if a future edit reintroduces the engine-locked patterns
the fleet change had to remove.
"""

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parent.parent


def _repo_mkdocs_config():
    """Load the repository's own mkdocs.yml, tolerating custom YAML tags."""

    class _Loader(yaml.SafeLoader):
        pass

    _Loader.add_multi_constructor("tag:yaml.org,2002:python/name:", lambda _loader, suffix, _node: suffix)
    _Loader.add_constructor("!ENV", lambda _loader, _node: None)
    return yaml.load((_REPO / "mkdocs.yml").read_text(encoding="utf-8"), Loader=_Loader)


def test_repo_docs_config_does_not_watch_itself():
    """A config that names itself in `watch:` makes the successor engine build an empty site.

    Zensical treats a self-referencing `watch:` as a signal to watch nothing and
    emits ZERO html at exit 0, `--strict` included. MkDocs watches its own config
    during `serve` regardless, so the entry is pure downside.
    """
    config = _repo_mkdocs_config()
    watch = config.get("watch") or []
    assert "mkdocs.yml" not in watch, "mkdocs.yml watches itself; the successor engine builds an empty site from that"
    assert "docs" in watch, "the docs directory must still be watched during serve"


def test_repo_docs_have_no_engine_hooks_or_in_source_build_tooling():
    """The repo's own docs depend on no mkdocs event hooks and ship no in-docs build tooling.

    Both are already true and pinned here: unlike the generated projects, these
    docs never had a `hooks.py` or a `docs_build/`. A `hooks:` key would not run
    under the successor engine, and any build-tooling `.py` under `docs_dir` would
    be published as a static asset.
    """
    config = _repo_mkdocs_config()
    assert "hooks" not in config, "the repo's own docs declare a hooks: key; the successor engine never runs it"
    stray = sorted(p.relative_to(_REPO).as_posix() for p in (_REPO / "docs").rglob("*.py"))
    assert not stray, f"build-tooling .py under docs/ would be published as a static asset: {stray}"


def test_repo_docs_theme_override_is_excluded_from_publishing():
    """The Material theme override must not be published as a site asset.

    `docs/material/overrides/main.html` sits inside `docs_dir`, so without an
    `exclude_docs` entry mkdocs copies it to `site/material/overrides/main.html`.
    """
    config = _repo_mkdocs_config()
    excluded = config.get("exclude_docs") or ""
    assert "material/overrides/*.html" in excluded, (
        "the theme override is not excluded; it would publish as site/material/overrides/main.html"
    )


@pytest.mark.slow
@pytest.mark.integration
def test_repo_docs_build_ships_content_not_an_empty_site(tmp_path):
    """A real build produces non-empty pages and leaks no theme override.

    A green `--strict` build is not evidence: the empty-site bug and a leaked
    asset both pass at exit 0. This asserts on content instead.
    """
    if shutil.which("uv") is None:
        pytest.skip("uv is required to build the docs")
    site = tmp_path / "site"
    build = subprocess.run(
        ["uv", "run", "--group", "docs", "mkdocs", "build", "--clean", "--strict", "--site-dir", str(site)],
        cwd=_REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert build.returncode == 0, build.stderr[-2000:]

    index = site / "index.html"
    assert index.is_file() and index.stat().st_size > 500, "the home page is missing or empty -- the build shipped nothing"
    assert not list(site.glob("material/overrides/*.html")), "the Material theme override leaked into the built site"
    assert len(list(site.rglob("index.html"))) > 5, "the site has too few pages; content collapsed"
