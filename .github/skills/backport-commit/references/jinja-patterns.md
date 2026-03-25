# Jinja2 Patterns in This Template

## When to Use Conditional Logic

### Unconditional (no `{% if %}` needed)
Apply changes unconditionally when they:
- Benefit all generated projects regardless of configuration
- Don't depend on any copier.yml variable
- Are bug fixes, dependency updates, or tooling improvements

### Conditional (`{% if %}` required)
Wrap in `{% if %}` when the change:
- Only applies when `include_examples=True` (marimo, gallery, example tests)
- Only applies when `include_actions=True` (workflows, git-cliff, commitizen)
- Depends on `license` value
- Depends on Python version range

### Decision flowchart
1. Does the change touch examples/ or marimo-related code? → `{% if include_examples %}`
2. Does the change touch .github/workflows/? → `{% if include_actions %}`
3. Does the change touch license-specific content? → Use license conditionals
4. Otherwise → likely unconditional

## Syntax Patterns Used in This Template

### Block conditional
```jinja
{% if include_examples %}
    "marimo",
{% endif %}
```

### Inline conditional
```jinja
{{ "marimo" if include_examples else "" }}
```

### Conditional in TOML arrays (with trailing comma)
```jinja
    {% if include_examples %}"example: marimo example tests",{% endif %}
```

### Variable substitution
```jinja
name = "{{ package_name }}"
requires-python = ">={{ min_python_version }}"
```

### Python version range loop
```jinja
{%- for version in ["3.11", "3.12", "3.13", "3.14"] %}
{%- if version >= min_python_version and version <= max_python_version %}
    "Programming Language :: Python :: {{ version }}",
{%- endif %}
{%- endfor %}
```

### Conditional directory names (in filesystem paths, not file content)
These are encoded in the template directory structure itself:
```text
template/{% if include_examples %}examples{% endif %}/
template/.github/{% if include_actions %}workflows{% endif %}/
```

## Whitespace Control

This template uses standard Jinja2 whitespace handling:
- `{%-` strips whitespace before the tag
- `-%}` strips whitespace after the tag
- Used primarily in loops and version range blocks to avoid blank lines

## Common Pitfalls

1. **Don't forget `.jinja` suffix** on new template files that contain `{{ }}` or `{% %}` tags
2. **Static files** (no Jinja syntax inside) should NOT have `.jinja` suffix
3. **Conditional directories** use the `{% if %}` pattern in the directory name itself — Copier handles this
4. **Trailing commas** in TOML/YAML arrays inside `{% if %}` blocks — ensure valid syntax when condition is both true and false
5. **Indentation matters** — match the surrounding file's indentation style when inserting conditional blocks
