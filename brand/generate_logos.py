#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pillow>=10.1",
# ]
# ///
"""Render a project's wide light/dark wordmark logos.

The wordmark is written in bracket notation, ``prefix[content]infix_``: the brackets
and the trailing underscore are drawn in the brand colours, and the bracketed part is
the highlighted word. ``sklearn[wrap]_`` and ``[y]ohou_`` are both valid.

Copier runs this as a task when a project is created (see ``_tasks`` in
``copier.yml``). It lives outside ``template/`` so it is never shipped into a
generated project. Run by hand, it regenerates a project's logos::

    uv run --script brand/generate_logos.py --text "sklearn[wrap]_" --out docs/assets --force

A logo is only written when it is missing, still byte-identical to the template's
placeholder in ``--placeholder-dir``, or ``--force`` is given. Copier reports a
``copier recopy`` as a copy, so this check, not the task's ``when``, is what keeps a
recopy from replacing a project's own logo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

FONT_PATH = Path(__file__).parent / "fonts" / "KarmaFuture.otf"

OPT_OUT_HINT = "re-run with -d generate_logos=false to keep the placeholder logos"

# Mirrors the logo colours in internal/templates/brand/company_config.yaml
# (`colors.<theme>.text`, `primary-dark` and `secondary`). Change both together.
PALETTE = {
    "light": {"text": "#1f2937", "bracket": "#a78bfa", "content": "#000000", "suffix": "#136f63"},
    "dark": {"text": "#ffffff", "bracket": "#8b5cf6", "content": "#ffffff", "suffix": "#136f63"},
}

LOGO_FILES = {"light": "logo_light.png", "dark": "logo_dark.png"}


class LogoError(Exception):
    """A failure the user can act on, reported without a traceback."""


def parse_wordmark(text: str) -> list[tuple[str, str]]:
    """Split a bracket-notation wordmark into ``(text, palette role)`` parts.

    Args:
        text: The wordmark, e.g. ``sklearn[wrap]_``.

    Returns:
        The non-empty parts in drawing order, each paired with its palette role.

    Raises:
        LogoError: If ``text`` does not hold exactly one ``[`` before one ``]``.
    """
    if text.count("[") != 1 or text.count("]") != 1 or text.index("[") > text.index("]"):
        raise LogoError(f"logo text {text!r} needs exactly one [highlighted] part, e.g. 'sklearn[wrap]_'")
    prefix, rest = text.split("[")
    content, infix = rest.split("]")
    suffix = ""
    if infix.endswith("_"):
        infix, suffix = infix[:-1], "_"
    parts = [
        (prefix, "text"),
        ("[", "bracket"),
        (content, "content"),
        ("]", "bracket"),
        (infix, "text"),
        (suffix, "suffix"),
    ]
    return [(part, role) for part, role in parts if part]


def render_logo(text: str, theme: str, height: int):
    """Draw the wordmark on a transparent canvas, ``height`` pixels tall.

    Args:
        text: The wordmark in bracket notation.
        theme: ``"light"`` or ``"dark"``.
        height: Image height in pixels; the font size and padding scale with it.

    Returns:
        A ``PIL.Image.Image`` in RGBA mode.
    """
    from PIL import Image, ImageDraw, ImageFont

    if not FONT_PATH.is_file():
        raise LogoError(f"font not found at {FONT_PATH}")
    font = ImageFont.truetype(str(FONT_PATH), int(height * 0.5))
    colours = PALETTE[theme]
    parts = parse_wordmark(text)

    measure = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

    def width_of(s: str) -> int:
        left, _, right, _ = measure.textbbox((0, 0), s, font=font)
        return right - left

    text_width = sum(width_of(part) for part, _ in parts)
    padding = int(width_of("n") * 1.5)
    image = Image.new("RGBA", (text_width + 2 * padding, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Centre vertically on the first part's ink, so the baseline does not move with
    # descenders further along the wordmark.
    _, top, _, bottom = draw.textbbox((0, 0), parts[0][0], font=font)
    y = height / 2 - (bottom - top) / 2 - top
    x = padding
    for part, role in parts:
        draw.text((x, y), part, fill=colours[role], font=font)
        x += width_of(part)
    return image


def should_write(target: Path, placeholder_dir: Path | None, force: bool) -> bool:
    """Decide whether ``target`` may be (over)written.

    Args:
        target: The logo file about to be written.
        placeholder_dir: Directory holding the template's placeholder of the same name.
        force: Write regardless of what is on disk.

    Returns:
        True when the target is missing, is still the placeholder, or ``force`` is set.
    """
    if force or not target.exists():
        return True
    if placeholder_dir is None:
        return False
    placeholder = placeholder_dir / target.name
    return placeholder.is_file() and placeholder.read_bytes() == target.read_bytes()


def main(argv: list[str] | None = None) -> int:
    """Generate the logos; return the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--text", required=True, help="wordmark in bracket notation, e.g. 'sklearn[wrap]_'")
    parser.add_argument("--out", required=True, type=Path, help="directory to write logo_light.png / logo_dark.png")
    parser.add_argument(
        "--placeholder-dir", type=Path, help="template assets; files identical to these are treated as placeholders"
    )
    parser.add_argument("--force", action="store_true", help="overwrite existing logos")
    parser.add_argument("--height", type=int, default=400, help="image height in pixels (default: 400)")
    args = parser.parse_args(argv)

    try:
        parse_wordmark(args.text)
        args.out.mkdir(parents=True, exist_ok=True)
        for theme, filename in LOGO_FILES.items():
            target = args.out / filename
            if not should_write(target, args.placeholder_dir, args.force):
                sys.stdout.write(f"kept existing {target}\n")
                continue
            render_logo(args.text, theme, args.height).save(target, optimize=True)
            sys.stdout.write(f"wrote {target}\n")
    except (LogoError, OSError) as exc:
        sys.stderr.write(f"error: logo generation failed: {exc}\n{OPT_OUT_HINT}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
