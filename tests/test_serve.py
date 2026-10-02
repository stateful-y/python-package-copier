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


def _api_page_states(project_dir):
    """Map each API page to its inode and modification time.

    A page that was deleted and written again has a new inode, and a page that was
    rewritten in place has a new modification time, so an equal state means the
    regeneration did not touch the file.
    """
    api_dir = project_dir / "docs" / "pages" / "api"
    return {
        p.relative_to(api_dir).as_posix(): (p.stat().st_ino, p.stat().st_mtime_ns)
        for p in sorted(api_dir.rglob("*.md"))
    }


def _event(event_type, src_path, dest_path="", is_directory=False):
    from types import SimpleNamespace

    return SimpleNamespace(event_type=event_type, src_path=src_path, dest_path=dest_path, is_directory=is_directory)


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


def test_serve_regenerate_touches_no_page_when_the_source_is_unchanged(copie):
    """A regeneration with no source change writes and deletes nothing.

    The docs server rebuilds the site on every change under `docs/`. A
    regeneration that deleted every page and wrote it again made the server build
    while pages were missing, and it stopped on a missing file. It also started a
    build for every regeneration, changed or not.
    """
    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0
    project_dir = result.project_dir

    serve = _load_serve(project_dir, "unchanged")
    serve.regenerate()
    before = _api_page_states(project_dir)
    assert any(name.startswith("generated/") for name in before)

    serve.regenerate()

    assert _api_page_states(project_dir) == before


def test_serve_regenerate_removes_only_the_page_of_a_removed_class(copie):
    """A class that leaves the source loses its page, and no other page is touched."""
    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0
    project_dir = result.project_dir
    hello = project_dir / "src" / "test_project" / "hello.py"
    original = hello.read_text(encoding="utf-8")

    serve = _load_serve(project_dir, "removed")
    _add_public_class(project_dir, "test_project", "ShortLivedWidget")
    serve.regenerate()
    before = _api_page_states(project_dir)
    page = "generated/test_project.hello.ShortLivedWidget.md"
    assert page in before

    hello.write_text(original, encoding="utf-8")
    serve.regenerate()
    after = _api_page_states(project_dir)

    assert page not in after
    # The module page lists the class, so it is rewritten. Every member page stays as it was.
    untouched = {name for name in after if name.startswith("generated/")}
    assert {name: after[name] for name in untouched} == {name: before[name] for name in untouched}


def test_serve_handler_counts_a_write_and_not_a_read(copie):
    """Only a write of a Python file is a change.

    The docs build and the regeneration read the source, and inotify reports each
    read as the events `opened` and `closed_no_write`. A read counted as a change
    made each regeneration start the next one. A save by rename gives one `moved`
    event whose source is the temporary file, so the destination counts too.
    """
    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0
    serve = _load_serve(result.project_dir, "handler")
    serve._DEBOUNCE_SECONDS = 0
    module = "src/test_project/hello.py"

    cases = [
        (_event("modified", module), True),
        (_event("created", module), True),
        (_event("deleted", module), True),
        (_event("closed", module), True),
        (_event("moved", "src/test_project/sedAbC123", dest_path=module), True),
        (_event("opened", module), False),
        (_event("closed_no_write", module), False),
        (_event("modified", "src/test_project", is_directory=True), False),
        (_event("modified", "src/test_project/data.yml"), False),
        (_event("moved", "src/test_project/a.yml", dest_path="src/test_project/b.yml"), False),
    ]
    for event, is_change in cases:
        handler = serve._SourceChangeHandler()
        handler.on_any_event(event)
        assert handler.take_due() is is_change, f"{event.event_type} {event.src_path} -> {event.dest_path}"


@pytest.mark.integration
@pytest.mark.slow
def test_serve_watcher_ignores_a_read_and_sees_a_save_by_rename(copie):
    """The same rule against the real observer of the platform."""
    import time

    from watchdog.observers import Observer

    result = copie.copy(extra_answers={"include_examples": False})
    assert result.exit_code == 0
    project_dir = result.project_dir
    hello = project_dir / "src" / "test_project" / "hello.py"

    serve = _load_serve(project_dir, "readwrite")
    serve._DEBOUNCE_SECONDS = 0

    def wait_until_due(timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if handler.take_due():
                return True
            time.sleep(0.05)
        return False

    handler = serve._SourceChangeHandler()
    observer = Observer()
    observer.schedule(handler, str(project_dir / "src"), recursive=True)
    observer.start()
    try:
        content = hello.read_text(encoding="utf-8")
        assert not wait_until_due(1.0), "a read of a source file was counted as a change"

        temporary = hello.with_name("hello.tmp")
        temporary.write_text(content + "\n", encoding="utf-8")
        temporary.replace(hello)
        assert wait_until_due(5.0), "a save by rename was not seen"
    finally:
        observer.stop()
        observer.join()


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
