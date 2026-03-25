# Test Patterns for Template Changes

## Test Infrastructure

### Fixtures (defined in tests/conftest.py)

| Fixture | Scope | Purpose |
|---|---|---|
| `copie` | function | Fresh project per test — use for parameterized/custom tests |
| `copie_session_default` | session | Shared default project (all features ON) — read-only checks |
| `copie_session_minimal` | session | Shared minimal project (examples=False, actions=False) |
| `copie_session_custom` | session | Custom values (Apache-2.0, py3.12+) |

### DEFAULT_ANSWERS

```python
{
    "project_name": "Test Project",
    "package_name": "test_project",
    "project_slug": "test-project",
    "description": "A test project",
    "author_name": "Test Author",
    "author_email": "test@example.com",
    "github_username": "testuser",
    "min_python_version": "3.11",
    "max_python_version": "3.14",
    "license": "MIT",
    "include_actions": True,
    "include_examples": True,
}
```

## Test Patterns

### Pattern 1: File existence

```python
def test_new_file_exists(copie_session_default):
    result = copie_session_default
    assert (result.project_dir / "path/to/new_file.py").is_file()
```

### Pattern 2: Content assertion

```python
def test_file_contains_expected_content(copie_session_default):
    result = copie_session_default
    content = (result.project_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert "expected_string" in content
    assert "should_not_appear" not in content
```

### Pattern 3: Variable substitution verification

```python
def test_variable_substituted_correctly(copie):
    result = copie.copy(extra_answers={"package_name": "custom_pkg"})
    content = (result.project_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert "custom_pkg" in content
    assert "{{ package_name }}" not in content  # raw Jinja must not leak
```

### Pattern 4: Conditional feature (parametrized)

```python
@pytest.mark.parametrize("include_examples", [True, False])
def test_conditional_content(copie, include_examples):
    result = copie.copy(extra_answers={"include_examples": include_examples})
    content = (result.project_dir / "some_file.toml").read_text(encoding="utf-8")
    if include_examples:
        assert "marimo" in content
    else:
        assert "marimo" not in content
```

### Pattern 5: Option combination matrix

```python
@pytest.mark.parametrize(
    "include_examples,include_actions",
    [(True, True), (True, False), (False, True), (False, False)],
)
def test_option_combo(copie, include_examples, include_actions):
    result = copie.copy(extra_answers={
        "include_examples": include_examples,
        "include_actions": include_actions,
    })
    # assertions vary by combination
```

## Which Test File to Use

| Change type | Add test to |
|---|---|
| General file existence/content | `tests/test_template.py` |
| Option combination behavior | `tests/test_option_combinations.py` |
| New template option values | `tests/test_template_options.py` or `tests/test_option_values.py` |
| Docs content | `tests/test_docs_content.py` |
| GitHub workflow changes | `tests/test_github_workflows.py` |
| Hook script changes | `tests/test_hooks.py` |
| Feature propagation (variable in multiple files) | `tests/test_propagated_features.py` |

## Running Tests

```bash
just test-fast    # Fast feedback (excludes slow/integration)
just fix          # Auto-format and lint
```
