# How to Regenerate Your Logos

This guide shows you how to redraw your project's wide logos (`docs/assets/logo_light.png` and
`docs/assets/logo_dark.png`) after the project was created: after a rename, to change the highlighted part, or to
replace the template's placeholder wordmark in a project created with `generate_logos=false`.

## Prerequisites

- A project generated from python-package-copier
- [uv](https://docs.astral.sh/uv/) installed
- A local checkout of the template:

```bash
git clone https://github.com/stateful-y/python-package-copier.git
```

## Render the Logos

From your project's root directory, run the template's generator with your wordmark. Square brackets mark the
highlighted part, and a trailing `_` is drawn in teal:

```bash
uv run --script ../python-package-copier/brand/generate_logos.py \
    --text "my-awesome[package]_" \
    --out docs/assets \
    --force
```

Adjust the first path to where you cloned the template. `--force` is what lets the generator replace logos that
already exist; without it, it only writes a logo that is missing.

The generator prints the files it wrote:

```text
wrote docs/assets/logo_light.png
wrote docs/assets/logo_dark.png
```

## Check and Commit

Preview the documentation site to see the new logo in the header and on the home page:

```bash
just serve
```

Then commit both files:

```bash
git add docs/assets/logo_light.png docs/assets/logo_dark.png
git commit -m "docs: regenerate logos"
```

## See Also

- [Template Variables](../reference/template-variables.md#logo_text) for the bracket notation and its defaults
- [Update from Template](update-template.md) for pulling in later template changes
