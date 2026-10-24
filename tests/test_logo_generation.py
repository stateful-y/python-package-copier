"""Logo generation at copy time (`logo_text`, `generate_logos`, the `_tasks` entry).

A new project used to inherit the template's own `python-package[copier]_` wordmark,
and `_skip_if_exists` then froze it there for good. The copy task now renders the
project's wordmark instead. These tests pin the three things that make that safe:
it renders on a fresh copy, it never replaces a logo the project owns (an update
does not run it, and a recopy, which copier also reports as "copy", is stopped by
the generator's placeholder check), and when it fails it says how to opt out.

Most of the suite copies with `generate_logos=False` (see conftest.py). The tests
here that render run the real task, `uv run --script`, so they need uv and, on a cold
cache, the network to resolve Pillow -- both of which the fast tier already has. They
stay in the fast tier on purpose: a few seconds each, and the only place a regression
in the copy-time behaviour would show on a pull request.
"""

import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from copier import run_copy, run_recopy, run_update
from copier.errors import TaskError
from PIL import Image

TEMPLATE_ROOT = Path(__file__).parent.parent
PLACEHOLDERS = TEMPLATE_ROOT / "template" / "docs" / "assets"
WIDE_LOGOS = ("logo_light.png", "logo_dark.png")

ANSWERS = {
    "project_name": "Sklearn Wrap",
    "project_slug": "sklearn-wrap",
    "package_name": "sklearn_wrap",
    "description": "d",
    "author_name": "A",
    "author_email": "a@b.c",
    "github_username": "u",
    "min_python_version": "3.11",
    "max_python_version": "3.14",
    "license": "MIT",
    "include_actions": False,
    "include_examples": False,
}


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_logos", TEMPLATE_ROOT / "brand" / "generate_logos.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = _load_generator()


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True, capture_output=True
    )


def _snapshot_template(dest: Path, drop: tuple[str, ...] = ()) -> Path:
    """Commit the working tree of this template, as it is now, into a fresh repo.

    Update and recopy read the template's location from the project's answers file,
    which this template hardcodes to `gh:stateful-y/python-package-copier`, and update
    needs the recorded `_commit` to exist. A local, clean, committed snapshot gives
    both without touching the network, and carries uncommitted work under test.
    """
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=TEMPLATE_ROOT,
        check=True,
        capture_output=True,
    ).stdout.decode()
    for rel in filter(None, listed.split("\0")):
        src = TEMPLATE_ROOT / rel
        if rel in drop or not src.is_file():
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    _git(dest, "init", "-q")
    _git(dest, "add", "-A")
    _git(dest, "commit", "-q", "-m", "snapshot")
    return dest


def _point_answers_at(project: Path, template: Path) -> None:
    answers_file = project / ".copier-answers.yml"
    answers = yaml.safe_load(answers_file.read_text(encoding="utf-8"))
    answers["_src_path"] = str(template)
    answers_file.write_text(yaml.safe_dump(answers, sort_keys=False), encoding="utf-8")


def _assert_rendered(path: Path) -> None:
    with Image.open(path) as image:
        assert image.mode == "RGBA", f"{path.name} must keep a transparent background"
        assert image.height == 400
        width = image.width
        alpha = image.getchannel("A")
        corners = [(0, 0), (width - 1, 0), (0, 399), (width - 1, 399)]
        assert all(alpha.getpixel(xy) == 0 for xy in corners), f"{path.name} corners are not transparent"
        assert alpha.getextrema()[1] == 255, f"{path.name} has no opaque text pixels"


# --- logo_text answer -------------------------------------------------------


def _copier_question(name: str) -> dict:
    return yaml.safe_load((TEMPLATE_ROOT / "copier.yml").read_text(encoding="utf-8"))[name]


@pytest.mark.parametrize(
    ("slug", "expected"),
    [
        ("sklearn-wrap", "sklearn[wrap]_"),
        ("python-package-copier", "python-package[copier]_"),
        ("yohou", "[yohou]_"),
    ],
)
def test_logo_text_default_brackets_the_last_word(copie, slug, expected):
    """The default reproduces the fleet's existing marks from the slug alone."""
    result = copie.copy(extra_answers={"project_slug": slug})
    worker_answers = result.result.answers.combined
    assert worker_answers["logo_text"] == expected


@pytest.mark.parametrize("bad", ["sklearn-wrap_", "a[b]c[d]_", "a]b[_"])
def test_logo_text_rejects_malformed_notation(copie, bad):
    """Anything but one `[...]` pair is refused before a project is written."""
    with pytest.raises(ValueError, match=r"exactly one \[highlighted\] part"):
        copie.copy(extra_answers={"logo_text": bad})


def test_logo_text_help_names_uv_and_the_opt_out():
    """The one failure the generator cannot report (no uv) is stated up front."""
    help_text = _copier_question("logo_text")["help"]
    assert "uv" in help_text
    assert "generate_logos=false" in help_text


def test_logo_text_is_asked_on_copy_only():
    """On an update the question would do nothing, so it is never asked there."""
    assert _copier_question("logo_text")["when"] == "{{ _copier_operation == 'copy' }}"


def test_min_copier_version_is_declared():
    """An older copier refuses the template rather than skipping generation silently."""
    config = yaml.safe_load((TEMPLATE_ROOT / "copier.yml").read_text(encoding="utf-8"))
    declared = tuple(int(part) for part in config["_min_copier_version"].split("."))
    assert declared >= (9, 17, 0)


# --- generator unit behaviour -----------------------------------------------


@pytest.mark.parametrize(
    ("text", "parts"),
    [
        ("sklearn[wrap]_", ["sklearn", "[", "wrap", "]", "_"]),
        ("[y]ohou_", ["[", "y", "]", "ohou", "_"]),
        ("a[b]c", ["a", "[", "b", "]", "c"]),
    ],
)
def test_parse_wordmark(text, parts):
    """The trailing underscore is the suffix; an absent one draws no suffix."""
    assert [part for part, _ in generator.parse_wordmark(text)] == parts


def test_guard_writes_missing_and_placeholder_targets(tmp_path):
    """A missing logo, or one still identical to the placeholder, is replaced."""
    placeholders = tmp_path / "placeholders"
    placeholders.mkdir()
    (placeholders / "logo_light.png").write_bytes(b"PLACEHOLDER")
    out = tmp_path / "out"
    out.mkdir()
    assert generator.should_write(out / "logo_light.png", placeholders, force=False)
    (out / "logo_light.png").write_bytes(b"PLACEHOLDER")
    assert generator.should_write(out / "logo_light.png", placeholders, force=False)


def test_guard_keeps_a_project_logo_unless_forced(tmp_path):
    """A logo that differs from the placeholder is the project's own."""
    placeholders = tmp_path / "placeholders"
    placeholders.mkdir()
    (placeholders / "logo_light.png").write_bytes(b"PLACEHOLDER")
    own = tmp_path / "logo_light.png"
    own.write_bytes(b"OWN")
    assert not generator.should_write(own, placeholders, force=False)
    assert not generator.should_write(own, None, force=False)
    assert generator.should_write(own, placeholders, force=True)


def test_generator_failure_names_the_opt_out(tmp_path, capsys):
    """A generator error exits non-zero and says how to proceed without logos."""
    assert generator.main(["--text", "no-brackets_", "--out", str(tmp_path)]) == 1
    assert "generate_logos=false" in capsys.readouterr().err


# --- copy, update, recopy ---------------------------------------------------


def test_copy_renders_the_project_wordmark(tmp_path):
    """A fresh copy replaces both placeholders with the project's own wordmark."""
    project = tmp_path / "project"
    run_copy(
        str(TEMPLATE_ROOT),
        str(project),
        data=ANSWERS,
        defaults=True,
        overwrite=True,
        unsafe=True,
        vcs_ref="HEAD",
    )
    assets = project / "docs" / "assets"
    for name in WIDE_LOGOS:
        assert assets.joinpath(name).read_bytes() != PLACEHOLDERS.joinpath(name).read_bytes(), (
            f"{name} is still the template's wordmark"
        )
        _assert_rendered(assets / name)
    assert assets.joinpath("logo_light.png").read_bytes() != assets.joinpath("logo_dark.png").read_bytes()

    # The org mark is not the generator's to touch.
    for name in ("logo.png", "favicon.png"):
        assert assets.joinpath(name).read_bytes() == PLACEHOLDERS.joinpath(name).read_bytes()
    # Nothing of the generator ships.
    assert not list(project.rglob("generate_logos.py"))
    assert not [p for p in project.rglob("*") if p.suffix in {".otf", ".ttf"}]


def test_opt_out_keeps_the_placeholders(copie):
    """`generate_logos=false` skips the task and records nothing."""
    result = copie.copy()
    assets = result.project_dir / "docs" / "assets"
    for name in WIDE_LOGOS:
        assert assets.joinpath(name).read_bytes() == PLACEHOLDERS.joinpath(name).read_bytes()
    assert "generate_logos" in result.result.answers.hidden
    assert "generate_logos" not in (result.project_dir / ".copier-answers.yml").read_text(encoding="utf-8")


def test_generator_failure_fails_the_copy(tmp_path, capfd):
    """With the font gone the task fails, the copy aborts, and the hint is shown."""
    template = _snapshot_template(tmp_path / "template", drop=("brand/fonts/KarmaFuture.otf",))
    project = tmp_path / "project"
    with pytest.raises(TaskError):
        run_copy(str(template), str(project), data=ANSWERS, defaults=True, unsafe=True, vcs_ref="HEAD")
    assert "generate_logos=false" in capfd.readouterr().err


def test_update_never_runs_the_generator(tmp_path, capfd):
    """An update leaves the project's logo alone and neither asks nor runs anything.

    The copy opts out, so the test needs no rendering; the update then runs with
    `generate_logos` at its default (on), so only the operation guard keeps the task
    from running.
    """
    template = _snapshot_template(tmp_path / "template")
    project = tmp_path / "project"
    opted_out = {**ANSWERS, "generate_logos": False}
    run_copy(str(template), str(project), data=opted_out, defaults=True, unsafe=True, vcs_ref="HEAD")
    own = b"THIS-PROJECT-OWN-LOGO-LIGHT"
    (project / "docs" / "assets" / "logo_light.png").write_bytes(own)
    _point_answers_at(project, template)
    _git(project, "init", "-q")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "project")

    # A newer template version, so the update has something to apply.
    (template / "CHANGES-SINCE-COPY.md").write_text("x\n", encoding="utf-8")
    _git(template, "add", "-A")
    _git(template, "commit", "-q", "-m", "newer")
    capfd.readouterr()

    worker = run_update(str(project), defaults=True, overwrite=True, unsafe=True, vcs_ref="HEAD")

    assert (project / "docs" / "assets" / "logo_light.png").read_bytes() == own
    # Copier does not announce tasks during an update, so look for the generator's own
    # report: it prints "wrote" or "kept existing" for every logo it considers.
    captured = capfd.readouterr()
    assert "docs/assets/logo_" not in captured.out + captured.err, "the logo task ran during an update"
    assert "logo_text" in worker.answers.hidden, "logo_text was asked during an update"
    assert "logo_text" not in (project / ".copier-answers.yml").read_text(encoding="utf-8")


def test_recopy_keeps_a_project_logo(tmp_path):
    """Copier reports a recopy as "copy"; the placeholder check is what holds."""
    template = _snapshot_template(tmp_path / "template")
    project = tmp_path / "project"
    run_copy(str(template), str(project), data=ANSWERS, defaults=True, unsafe=True, vcs_ref="HEAD")
    assets = project / "docs" / "assets"
    own = {name: f"OWN-{name}".encode() for name in WIDE_LOGOS}
    for name, content in own.items():
        assets.joinpath(name).write_bytes(content)
    _point_answers_at(project, template)

    run_recopy(str(project), data=ANSWERS, defaults=True, overwrite=True, unsafe=True, vcs_ref="HEAD")

    for name, content in own.items():
        assert assets.joinpath(name).read_bytes() == content, f"recopy replaced the project's {name}"


def test_recopy_fixes_a_project_still_on_the_placeholder(tmp_path):
    """A project that never got its logo gets it on recopy."""
    template = _snapshot_template(tmp_path / "template")
    project = tmp_path / "project"
    opted_out = {**ANSWERS, "generate_logos": False}
    run_copy(str(template), str(project), data=opted_out, defaults=True, unsafe=True, vcs_ref="HEAD")
    assets = project / "docs" / "assets"
    assert assets.joinpath("logo_light.png").read_bytes() == PLACEHOLDERS.joinpath("logo_light.png").read_bytes()
    _point_answers_at(project, template)

    run_recopy(str(project), data=ANSWERS, defaults=True, overwrite=True, unsafe=True, vcs_ref="HEAD")

    for name in WIDE_LOGOS:
        assert assets.joinpath(name).read_bytes() != PLACEHOLDERS.joinpath(name).read_bytes()
        _assert_rendered(assets / name)
