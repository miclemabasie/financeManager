import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User.objects.create_user(
        email="user@example.com",
        username="user1",
        first_name="Test",
        last_name="User",
        password="testpass123",
    )
    return user


@pytest.fixture
def test_staff_user(db):
    """Create a test staff user."""
    user = User.objects.create_user(
        email="admin@example.com",
        username="admin",
        first_name="Admin",
        last_name="User",
        password="testpass123",
        is_staff=True,
    )
    return user


@pytest.fixture
def test_institution(db):
    """Create a test financial institution."""
    from apps.finance.models import FinancialInstitution

    return FinancialInstitution.objects.create(
        name="Test Bank",
        momo_number="+237650123456",
        contact_email="contact@testbank.com",
    )


@pytest.fixture
def authenticated_user(test_user):
    """Return an authenticated user."""
    return test_user
