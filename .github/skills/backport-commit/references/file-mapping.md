# File Mapping: Generated Project → Template Source

## Path Translation Rules

### Rule 1: Strip `.jinja` suffix
Template files ending in `.jinja` produce output files without it.
- `pyproject.toml.jinja` → `pyproject.toml`
- `noxfile.py.jinja` → `noxfile.py`

### Rule 2: Replace literal package name with `{{ package_name }}`
The `src/<actual_name>/` directory maps to `template/src/{{ package_name }}/`.
- `src/my_pkg/hello.py` → `template/src/{{ package_name }}/hello.py.jinja`

### Rule 3: Conditional directory names
Some directories exist only when a copier variable is true.

| Generated Path | Template Path |
|---|---|
| `examples/` | `template/{% if include_examples %}examples{% endif %}/` |
| `docs/examples/` | `template/docs/{% if include_examples %}examples{% endif %}/` |
| `.github/workflows/` | `template/.github/{% if include_actions %}workflows{% endif %}/` |

### Rule 4: Conditional file names
Some files use conditionals in the filename itself.

| Generated Path | Template Path |
|---|---|
| `docs/pages/tutorials/examples.md` | `template/docs/pages/tutorials/{% if include_examples %}examples.md{% endif %}.jinja` |
| `docs/stylesheets/gallery.css` | `template/docs/stylesheets/{% if include_examples %}gallery.css{% endif %}` |
| `tests/test_examples.py` | `template/tests/{% if include_examples %}test_examples.py{% endif %}.jinja` |

### Rule 5: Static files (no `.jinja` suffix)
Some template files are copied verbatim — no `.jinja` extension.
- `CONTRIBUTING.md` → `template/CONTRIBUTING.md`
- `docs/assets/README.md` → `template/docs/assets/README.md`
- `docs/javascripts/mathjax.js` → `template/docs/javascripts/mathjax.js`

### Rule 6: Binary files
PNG images and similar binaries are copied as-is. Do not modify these.

## Copier Variables (from copier.yml)

| Variable | Type | Default | Usage |
|---|---|---|---|
| `project_name` | str | *(required)* | README, docs |
| `package_name` | str | auto from project_name | `src/` dir, pyproject.toml name, imports, .gitignore |
| `project_slug` | str | auto from project_name | GitHub URLs, badges |
| `description` | str | `""` | pyproject.toml, README |
| `author_name` | str | *(required)* | pyproject.toml maintainers |
| `author_email` | str | *(required)* | pyproject.toml maintainers |
| `github_username` | str | `"stateful-y"` | GitHub URLs, badges, mkdocs.yml |
| `license` | str | `"MIT"` | LICENSE file content, pyproject.toml |
| `min_python_version` | str | `"3.11"` | classifiers, ruff target, noxfile matrix |
| `max_python_version` | str | `"3.14"` | classifiers, noxfile matrix |
| `include_actions` | bool | `true` | .github/workflows/ dir, .git-cliff.toml, commitizen hook |
| `include_examples` | bool | `true` | examples/, gallery.css, marimo deps, test markers |

## Reverse Substitution

When backporting, convert literal values back to template variables:

| Literal in generated project | Replace with |
|---|---|
| The actual package name (e.g., `my_pkg`) | `{{ package_name }}` |
| The actual project name (e.g., `My Package`) | `{{ project_name }}` |
| The actual slug (e.g., `my-package`) | `{{ project_slug }}` |
| The actual GitHub username | `{{ github_username }}` |
| The actual author name | `{{ author_name }}` |
| The actual author email | `{{ author_email }}` |
| The actual description | `{{ description }}` |
| A hardcoded Python version like `3.11` in version contexts | `{{ min_python_version }}` or `{{ max_python_version }}` |

**Important:** Only substitute values that originated from a template variable. Not every occurrence of a package name in code should become `{{ package_name }}` — only those Copier would have generated.
