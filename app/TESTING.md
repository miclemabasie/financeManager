# SmartSave - Testing Guide

This guide explains how to run the test suite for the SmartSave project.

## Overview

The project uses **pytest** with **pytest-django** for unit testing. All tests are located in the `tests/` directories within each app:

- `apps/users/tests/test_models.py` - User and Profile model tests
- `apps/finance/tests/test_models.py` - Finance-related model tests
- `apps/notifications/tests/test_models.py` - Notification model tests

**Test Coverage:** 62 tests covering all core models with ~61% overall code coverage.

---

## Prerequisites

Ensure you have the project dependencies installed:

```bash
pip install -r requirements.txt
```

Required packages (already in requirements.txt):

- `pytest` - Test framework
- `pytest-django` - Django integration for pytest
- `pytest-cov` - Coverage reporting

---

## Configuration

### pytest.ini

Located in `/app/pytest.ini`, it configures:

- **DJANGO_SETTINGS_MODULE**: Points to `finance_manager.settings.test`
- **Test discovery**: Looks for test files matching `test_*.py` in the `apps` directory
- **Coverage**: Generates HTML and terminal reports

### finance_manager/settings/test.py

Special test settings file that:

- Uses SQLite in-memory database (fast tests, no DB setup required)
- Disables migrations for faster execution
- Simplifies password validation
- Mutes logging during tests

### conftest.py

Provides pytest fixtures:

- `test_user(db)` - Creates a regular test user
- `test_staff_user(db)` - Creates a staff/admin user
- `test_institution(db)` - Creates a test financial institution
- `authenticated_user` - Returns a pre-authenticated user

---

## Running Tests

### Run All Tests

```bash
cd app
pytest
```

Or with verbose output:

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest apps/users/tests/test_models.py -v
pytest apps/finance/tests/test_models.py -v
pytest apps/notifications/tests/test_models.py -v
```

### Run Specific Test Class

```bash
pytest apps/users/tests/test_models.py::TestUserModel -v
pytest apps/finance/tests/test_models.py::TestDepositTransaction -v
```

### Run Specific Test

```bash
pytest apps/users/tests/test_models.py::TestUserModel::test_create_user -v
```

### Run Tests with Coverage Report

```bash
pytest --cov=apps --cov-report=html --cov-report=term-missing
```

This generates:

- **htmlcov/index.html** - Interactive HTML coverage report
- **Terminal output** - Shows missing lines for each module

### Run Tests with Short Output

```bash
pytest --tb=short
```

### Run Tests with Extra Verbosity

```bash
pytest -vv
```

---

## Test Structure

Each test file is organized into test classes grouped by model:

```python
@pytest.mark.django_db
class TestUserModel:
    """Test User model creation and methods."""

    def test_create_user(self):
        """Test basic user creation."""
        # Test code here
```

### Test Database

Tests use an in-memory SQLite database (`finance_manager/settings/test.py`) that:

- ✅ Fast - no network I/O
- ✅ Clean - fresh DB for each test
- ✅ Isolated - tests don't interfere with each other
- ✅ No setup needed - just run pytest

### Database Fixtures

Tests that need the database use the `@pytest.mark.django_db` decorator:

```python
@pytest.mark.django_db
def test_something():
    user = User.objects.create_user(...)  # Works!
```

---

## What's Tested

### Users App

- ✅ User creation and validation
- ✅ User roles (Admin, Bank Admin, User)
- ✅ User name methods (get_full_name, get_short_name)
- ✅ Profile auto-creation via signals
- ✅ Profile relationships and phone numbers
- ✅ Data deletion requests

### Finance App

- ✅ Financial institutions
- ✅ User-institution account linking
- ✅ Deposit transactions (create, confirm, list)
- ✅ Withdrawal requests (create, schedule, complete)
- ✅ Expense tracking and categorization
- ✅ Status transitions

### Notifications App

- ✅ Email/SMS notification templates
- ✅ Broadcast campaigns
- ✅ Individual notifications
- ✅ User notification preferences
- ✅ Email configuration management

---

## Example Test Run

```bash
$ cd app
$ pytest apps/users/tests/test_models.py -v

======= test session starts ========
platform linux -- Python 3.10.12, pytest-8.3.2, py-1.13.2, pluggy-1.5.0
django: version 5.2, pluginbase: 1.5.0
cachedir: .pytest_cache
rootdir: /app, configfile: pytest.ini
collected 13 items

apps/users/tests/test_models.py::TestUserModel::test_create_user PASSED         [  7%]
apps/users/tests/test_models.py::TestUserModel::test_user_email_unique PASSED   [ 15%]
...
======= 13 passed in 1.23s =======
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'apps'"

**Solution:** Ensure you're running pytest from the `app/` directory:

```bash
cd app
pytest
```

### "django.core.exceptions.ImproperlyConfigured"

**Solution:** Check that `.env` file exists in the `app/` directory:

```bash
cd app
cp .env.example .env
```

### Tests are slow

By default, coverage is enabled. Run without coverage for faster execution:

```bash
pytest --no-cov
```

### Database integrity errors in one test affect others

This shouldn't happen with in-memory SQLite. If it does, ensure you're using fresh database per test:

```bash
pytest --forked  # Run each test in isolated process (requires pytest-forked)
```

---

## Continuous Integration

To run tests in CI/CD pipelines:

```bash
# With coverage report
pytest --cov=apps --cov-report=xml --cov-report=term-missing

# Exit with error if coverage below threshold
pytest --cov=apps --cov-fail-under=60
```

---

## Adding New Tests

When adding features, add corresponding tests:

1. Create test in appropriate `tests/test_models.py` file
2. Use `@pytest.mark.django_db` for database access
3. Follow the naming convention: `test_<what_is_being_tested>`
4. Run tests locally before committing

Example:

```python
@pytest.mark.django_db
def test_new_feature():
    """Test new feature."""
    user = User.objects.create_user(...)
    # Test new code
    assert something
```

---

## Performance Notes

- **Full test suite:** ~40 seconds
- **Single test file:** ~5-10 seconds
- **Single test:** <1 second

To speed up test runs:

```bash
pytest --no-cov -x  # Stop on first failure, no coverage
pytest --tb=short   # Shorter tracebacks
```

---

For questions or issues, refer to:

- [pytest documentation](https://docs.pytest.org/)
- [pytest-django documentation](https://pytest-django.readthedocs.io/)
- Django models and testing best practices
