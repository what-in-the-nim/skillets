# pytest — Advanced Implementation Playbook

## §1 — Production Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short -q
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks integration tests
    smoke: marks smoke tests
    api: marks API tests
filterwarnings =
    error
    ignore::DeprecationWarning
```

```toml
# pyproject.toml (alternative)
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --strict-markers --tb=short"
markers = [
    "slow: marks tests as slow",
    "integration: integration tests",
    "smoke: smoke tests",
]

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## §2 — Fixtures (Scoping, Factories, Teardown)

```python
# conftest.py — shared fixtures
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Session-scoped: created once per test session
@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

# Function-scoped: created per test (default), auto-cleanup
@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# Factory fixture — create multiple instances
@pytest.fixture
def user_factory(db_session):
    created = []
    def _create_user(name="Test User", email=None, role="viewer"):
        email = email or f"{name.lower().replace(' ', '.')}@test.com"
        user = User(name=name, email=email, role=role)
        db_session.add(user)
        db_session.commit()
        created.append(user)
        return user
    yield _create_user
    for user in created:
        db_session.delete(user)
    db_session.commit()

# Autouse fixture — runs for every test in module
@pytest.fixture(autouse=True)
def reset_cache():
    cache.clear()
    yield
    cache.clear()

# tmp_path for file operations (built-in)
def test_writes_output(tmp_path):
    output_file = tmp_path / "result.json"
    generate_report(output_file)
    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert data["status"] == "complete"
```

## §3 — Parameterized Tests

```python
import pytest

# Basic parametrize
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected

# Multiple parameters with IDs
@pytest.mark.parametrize("email,valid", [
    ("user@test.com", True),
    ("invalid", False),
    ("", False),
    ("user@.com", False),
], ids=["valid_email", "no_at_sign", "empty", "missing_domain"])
def test_validate_email(email, valid):
    assert validate_email(email) == valid

# Combine parametrize (cartesian product)
@pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
@pytest.mark.parametrize("resolution", ["1920x1080", "1366x768", "375x667"])
def test_responsive_layout(browser, resolution):
    assert render_page(browser, resolution).is_valid()

# Indirect parametrize (pass to fixture)
@pytest.fixture
def user(request):
    return create_user(role=request.param)

@pytest.mark.parametrize("user", ["admin", "editor", "viewer"], indirect=True)
def test_permissions(user):
    assert user.can_view()
```

## §4 — Mocking with pytest-mock

```python
# pip install pytest-mock

def test_send_email(mocker):
    mock_smtp = mocker.patch("myapp.email.smtplib.SMTP")
    send_email("test@example.com", "Hello", "Body")
    mock_smtp.return_value.sendmail.assert_called_once()

def test_api_call(mocker):
    mock_get = mocker.patch("myapp.api.requests.get")
    mock_get.return_value.json.return_value = {"id": 1, "name": "Alice"}
    mock_get.return_value.status_code = 200
    user = get_user(1)
    assert user["name"] == "Alice"
    mock_get.assert_called_once_with("https://api.example.com/users/1")

def test_database_error(mocker):
    mocker.patch("myapp.db.session.commit", side_effect=IntegrityError("duplicate"))
    with pytest.raises(DuplicateError):
        create_user("Alice", "alice@test.com")

# Spy — track calls without replacing
def test_logging(mocker):
    spy = mocker.spy(logger, "info")
    process_order(order)
    spy.assert_called_with("Order processed: %s", order.id)

# Mock environment variables
def test_config(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key-123")
    monkeypatch.setenv("DEBUG", "true")
    config = load_config()
    assert config.api_key == "test-key-123"
    assert config.debug is True
```

## §5 — Async Testing

```python
# pip install pytest-asyncio

import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data("https://api.example.com/data")
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_async_exception():
    with pytest.raises(ConnectionError):
        await fetch_data("https://invalid.example.com")

# Async fixtures
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_api_endpoint(async_client):
    response = await async_client.get("/api/users")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

## §6 — Testing Exceptions & Warnings

```python
# Exception testing
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_error_message():
    with pytest.raises(ValueError, match=r".*invalid email.*"):
        validate_email("not-an-email")

def test_raises_with_info():
    with pytest.raises(PermissionError) as exc_info:
        delete_file("/protected/file.txt")
    assert "permission denied" in str(exc_info.value).lower()
    assert exc_info.value.errno == 13

# Warning testing
def test_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="use new_func"):
        old_func()
```

## §7 — Markers & Custom Plugins

```python
# Custom marker usage
@pytest.mark.slow
def test_full_data_processing():
    result = process_large_dataset()
    assert result.row_count > 1_000_000

@pytest.mark.integration
def test_database_connection():
    assert db.is_connected()

# Run by marker: pytest -m "not slow"
# Run by marker: pytest -m "smoke and not integration"

# Custom plugin — conftest.py
def pytest_collection_modifyitems(config, items):
    """Auto-mark tests in integration/ directory"""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

# Custom report header
def pytest_report_header(config):
    return f"Environment: {os.getenv('ENV', 'local')}"
```

## §8 — Class-Based Test Organization

Use stateless, behavior-named classes for grouping. Pass dependencies through fixtures instead of storing setup state on the class.

```python
class TestUserCreate:
    def test_create_user_returns_saved_user(self, user_service):
        user = user_service.create("Alice", "alice@test.com")
        assert user.id is not None
        assert user.name == "Alice"

class TestUserFindByEmail:
    def test_returns_matching_user(self, user_service, user_factory):
        user_factory(name="Bob", email="bob@test.com")
        user = user_service.find_by_email("bob@test.com")
        assert user.name == "Bob"

class TestUserDelete:
    def test_delete_nonexistent_raises_not_found(self, user_service):
        with pytest.raises(NotFoundError):
            user_service.delete(999)
```

## §9 — CI/CD Integration

```yaml
# GitHub Actions
name: Python Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '${{ matrix.python-version }}' }
      - name: Install deps
        run: pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov=src --cov-report=xml --junitxml=results.xml -v
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with: { files: coverage.xml }
      - name: Upload results
        uses: actions/upload-artifact@v4
        if: always()
        with: { name: test-results-${{ matrix.python-version }}, path: results.xml }
```

## §10 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Fixture not found | Wrong scope or missing conftest.py | Check conftest.py location, fixture name |
| `ScopeMismatch` | Function fixture depends on session fixture | Match scope: session → module → function |
| Tests interfere | Shared mutable state | Use function-scoped fixtures, `autouse` cleanup |
| Parametrize fails | Wrong number of params | Ensure tuple count matches parameter names |
| Slow collection | Too many test paths | Set `testpaths` in pytest.ini |
| Async test hangs | Missing `@pytest.mark.asyncio` | Add marker or set `asyncio_mode = "auto"` |
| Coverage wrong | Source path mismatch | Set `source` in `[tool.coverage.run]` |
| Import errors | Missing `__init__.py` or bad path | Add `__init__.py` or use `src` layout with `--import-mode=importlib` |
| Monkeypatch not reverting | Using at module scope | Only use in function-scoped fixtures |
| Marker warnings | Marker not registered | Add to `markers` in pytest.ini |

## §11 — Best Practices Checklist

- ✅ Use fixtures over setup/teardown methods
- ✅ Use `conftest.py` for shared fixtures (auto-discovered)
- ✅ Use `tmp_path` for file operations (built-in, auto-cleanup)
- ✅ Use `monkeypatch` for env vars and attribute patching
- ✅ Use `pytest-mock` (mocker fixture) over `unittest.mock`
- ✅ Use `@pytest.mark.parametrize` for data-driven tests
- ✅ Register all custom markers in `pytest.ini`
- ✅ Use `--strict-markers` to catch typos in marker names
- ✅ Use `pytest-cov` for coverage with `--cov-fail-under=80`
- ✅ Use `pytest-xdist` for parallel execution: `pytest -n auto`
- ✅ Use `--tb=short` for concise tracebacks in CI
- ✅ Structure: `tests/unit/`, `tests/integration/`, `conftest.py`
- ✅ Name files `test_*.py` and functions `test_*`
- ✅ Use factory fixtures for creating test objects
- ✅ Use `pytest.raises(match=...)` for precise error checking

## Basic patterns

### Basic Test

```python
import pytest

def test_addition():
    assert 2 + 3 == 5

def test_exception():
    with pytest.raises(ValueError, match="invalid"):
        int("not_a_number")

class TestCalculator:
    def test_add(self):
        calc = Calculator()
        assert calc.add(2, 3) == 5

    def test_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            Calculator().divide(10, 0)
```

### Fixtures

```python
@pytest.fixture
def calculator():
    return Calculator()

@pytest.fixture
def db_connection():
    conn = Database.connect("test_db")
    yield conn  # teardown after yield
    conn.rollback()
    conn.close()

@pytest.fixture(scope="module")
def api_client():
    client = APIClient(base_url="http://localhost:8000")
    yield client
    client.logout()

# conftest.py - shared fixtures
@pytest.fixture(autouse=True)
def reset_state():
    State.reset()
    yield
    State.cleanup()

# Usage
def test_add(calculator):
    assert calculator.add(2, 3) == 5
```

### Parametrize

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", 5), ("", 0), ("pytest", 6),
])
def test_string_length(input, expected):
    assert len(input) == expected

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5), (-1, 1, 0), (0, 0, 0),
])
def test_add(calculator, a, b, expected):
    assert calculator.add(a, b) == expected
```

### Markers

```python
@pytest.mark.slow
def test_large_dataset(): ...

@pytest.mark.skip(reason="Not implemented")
def test_future_feature(): ...

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_permissions(): ...

@pytest.mark.xfail(reason="Known bug #123")
def test_known_bug(): ...
```

### Mocking

Use mocks only for a justified external boundary. Interaction assertions are appropriate when the outgoing interaction is itself the observable contract, such as sending an email. Prefer assertions on the destination, payload, or result over incidental call counts. The database example below illustrates mocking syntax; prefer a real in-process implementation or small fake when practical.

```python
from unittest.mock import patch, MagicMock

def test_send_email(mocker):
    mock_smtp = mocker.patch("myapp.email.smtplib.SMTP")
    send_welcome_email("user@test.com")
    mock_smtp.return_value.sendmail.assert_called_once()

def test_api_call(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"users": [{"name": "Alice"}]}
    mocker.patch("myapp.service.requests.get", return_value=mock_response)
    users = get_users()
    assert len(users) == 1

@patch("myapp.service.database")
def test_save_user(mock_db):
    mock_db.save.return_value = True
    assert save_user({"name": "Alice"}) is True
    mock_db.save.assert_called_once()
```

### Assertions

```python
assert x == y
assert x != y
assert x in collection
assert isinstance(obj, MyClass)
assert 0.1 + 0.2 == pytest.approx(0.3)

with pytest.raises(ValueError) as exc_info:
    raise ValueError("bad")
assert "bad" in str(exc_info.value)
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| `self.assertEqual()` | `assert x == y` | pytest rewrites give better output |
| Setup in `__init__` | `@pytest.fixture` | Lifecycle management |
| Global state | Fixture with `yield` | Proper cleanup |
| Huge test functions | Small focused tests | Easier debugging |

## Quick Reference

| Task | Command |
|------|---------|
| Run all | `pytest` |
| Run file | `pytest tests/test_login.py` |
| Run specific | `pytest tests/test_login.py::test_login_success` |
| By marker | `pytest -m slow` |
| By keyword | `pytest -k "login and not invalid"` |
| Verbose | `pytest -v` |
| Stop first fail | `pytest -x` |
| Last failed | `pytest --lf` |
| Coverage | `pytest --cov=myapp --cov-report=html` |
| Parallel | `pytest -n auto` (pytest-xdist) |

## pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = ["slow: slow tests", "integration: integration tests"]
addopts = "-v --tb=short"
```
