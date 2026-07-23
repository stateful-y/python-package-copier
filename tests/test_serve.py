"""Tests for the live-preview supervisor (`docs_build/serve.py`).

The supervisor regenerates the API pages when the package source changes during
a preview, replacing what the mkdocs `on_pre_build` hook did in a form that does
not depend on the engine running a hook. These tests exercise the regeneration
and the watch mechanism; the `mkdocs serve` subprocess it also manages is plain
process orchestration and is not started here.
"""

import importlib.util
import sys

import pytest
from _build_layout import BUILD_DIR

# serve.py puts its own directory on sys.path and imports the build steps as
# plain top-level names, which sys.modules caches globally -- so a second project
# loaded in a session would silently reuse the first project's build steps. Purge
# them before each load, the same isolation _load_markers relies on.
_BUILD_STEP_MODULES = ("_api_pages", "_notebooks", "_markdown_export")

_GENERATED = ("docs", "pages", "api", "generated")


def _load_serve(project_dir, unique_suffix):
    """Load a generated `docs_build/serve.py` under a unique module name."""
    for name in _BUILD_STEP_MODULES:
        sys.modules.pop(name, None)
    spec = importlib.util.spec_from_file_location(
        f"generated_serve_{unique_suffix}", project_dir / BUILD_DIR / "serve.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _generated_pages(project_dir):
    return {p.name for p in project_dir.joinpath(*_GENERATED).glob("*.md")}


def _add_public_class(project_dir, package_name, class_name):
    """Append a public class to the walked `hello` submodule."""
    hello = project_dir / "src" / package_name / "hello.py"
    hello.write_text(
        hello.read_text(encoding="utf-8") + f'\n\nclass {class_name}:\n    """Added at runtime."""\n',
        encoding="utf-8",
    )


def test_serve_regenerate_picks_up_a_new_class(copie):
    """A class added after the first regeneration gets a page on the next one.

    This is the live-preview promise, and it specifically guards the cache
    reset. The discovery caches persist for the process lifetime (a single build
    fills them once), so a regeneration that did not reset them would reuse the
    first walk and never see the new class: the preview would silently go stale
    while looking like it worked. `serve.regenerate` resets before generating.
    """
    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0
    project_dir = result.project_dir

    serve = _load_serve(project_dir, "newclass")
    serve.regenerate()
    before = _generated_pages(project_dir)

    _add_public_class(project_dir, "test_project", "FreshWidget")
    serve.regenerate()
    after = _generated_pages(project_dir)

    new = after - before
    assert any("FreshWidget" in name for name in new), (
        f"a class added after the first regeneration produced no page (stale cache?); new pages: {sorted(new)}"
    )


@pytest.mark.integration
@pytest.mark.slow
def test_serve_watcher_regenerates_on_source_change(copie):
    """The watchdog observer regenerates the API pages when `src/` changes.

    Exercises the real watch -> debounce -> regenerate chain that the supervisor
    runs, without starting the docs server (which is plain process
    orchestration): edit a source file, and within a timeout the new class's
    page appears -- the "a new class appears without a restart" scenario.
    """
    import time

    from watchdog.observers import Observer

    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0
    project_dir = result.project_dir

    serve = _load_serve(project_dir, "watcher")
    serve.regenerate()  # initial build, so the watcher only has to catch the change

    handler = serve._SourceChangeHandler()
    observer = Observer()
    observer.schedule(handler, str(project_dir / "src"), recursive=True)
    observer.start()
    try:
        _add_public_class(project_dir, "test_project", "WatchedWidget")
        page = project_dir.joinpath(*_GENERATED) / "test_project.hello.WatchedWidget.md"
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            time.sleep(0.2)
            if handler.take_due():
                serve.regenerate()
            if page.is_file():
                break
        assert page.is_file(), "the watcher did not regenerate the new class's page within the timeout"
    finally:
        observer.stop()
        observer.join()
