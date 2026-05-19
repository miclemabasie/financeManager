import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.users.models import Profile, DataDeletionRequest, Role

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test User model creation and methods."""

    def test_create_user(self):
        """Test basic user creation."""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="securepass123",
        )
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is False
        assert user.role == Role.USER

    def test_user_email_unique(self):
        """Test that user emails must be unique."""
        User.objects.create_user(
            email="unique@example.com",
            username="user1",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                email="unique@example.com",
                username="user2",
                first_name="Test",
                last_name="User",
                password="pass123",
            )

    def test_user_get_full_name(self):
        """Test get_full_name method."""
        user = User.objects.create_user(
            email="fullname@example.com",
            username="testuser",
            first_name="john",
            last_name="doe",
            password="pass123",
        )
        assert user.get_full_name() == "John Doe"

    def test_user_get_short_name(self):
        """Test get_short_name method."""
        user = User.objects.create_user(
            email="shortname@example.com",
            username="johnny",
            first_name="John",
            last_name="Doe",
            password="pass123",
        )
        assert user.get_short_name() == "johnny"

    def test_user_membership_duration(self):
        """Test membership duration calculation."""
        user = User.objects.create_user(
            email="member@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        duration = user.membership_duration()
        assert isinstance(duration, str)
        assert "ago" in duration or "0" in duration

    def test_user_last_active_never(self):
        """Test last_active when user has never logged in."""
        user = User.objects.create_user(
            email="never@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        assert user.last_active() == "Never"

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email="str@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        assert str(user) == "testuser - str@example.com"

    def test_user_set_role(self):
        """Test setting user role."""
        user = User.objects.create_user(
            email="role@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        user.role = Role.BANK_ADMIN
        user.save()
        user.refresh_from_db()
        assert user.role == Role.BANK_ADMIN


@pytest.mark.django_db
class TestProfileModel:
    """Test Profile model."""

    def setup_method(self):
        """Setup test users to avoid profile conflicts."""
        pass

    def test_create_profile_via_signal(self):
        """Test profile is automatically created via signal."""
        user = User.objects.create_user(
            email="profile1@example.com",
            username="testuser1",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        profile = Profile.objects.get(user=user)
        assert profile.user == user
        assert str(profile.country) == "CM"
        assert profile.city == "Bamenda"

    def test_profile_can_be_updated(self):
        """Test profile can be updated after creation."""
        user = User.objects.create_user(
            email="profile2@example.com",
            username="testuser2",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        profile = Profile.objects.get(user=user)
        profile.bio = "Test bio"
        profile.phone_number = "+237699123456"
        profile.save()
        profile.refresh_from_db()
        assert profile.bio == "Test bio"
        assert str(profile.phone_number) == "+237699123456"

    def test_profile_phone_number(self):
        """Test profile phone number."""
        user = User.objects.create_user(
            email="phone1@example.com",
            username="testuser3",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        profile = Profile.objects.get(user=user)
        profile.phone_number = "+237699987654"
        profile.save()
        profile.refresh_from_db()
        assert str(profile.phone_number) == "+237699987654"

    def test_profile_one_to_one_relationship(self):
        """Test that profile is one-to-one with user."""
        user = User.objects.create_user(
            email="onetoone1@example.com",
            username="testuser4",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        profile1 = Profile.objects.get(user=user)
        with pytest.raises(Exception):
            Profile.objects.create(user=user)

    def test_profile_str_representation(self):
        """Test profile string representation."""
        user = User.objects.create_user(
            email="profstr1@example.com",
            username="testuser5",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        profile = Profile.objects.get(user=user)
        assert str(profile) == "testuser5's Profile"


@pytest.mark.django_db
class TestDataDeletionRequest:
    """Test DataDeletionRequest model."""

    def test_create_deletion_request(self):
        """Test creating a data deletion request."""
        user = User.objects.create_user(
            email="delete@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        deletion = DataDeletionRequest.objects.create(
            user=user,
            email=user.email,
            request_type="account",
        )
        assert deletion.user == user
        assert deletion.status == "pending"
        assert deletion.request_type == "account"

    def test_deletion_request_statuses(self):
        """Test all deletion request statuses."""
        statuses = ["pending", "processing", "completed", "rejected"]
        for i, status in enumerate(statuses):
            deletion = DataDeletionRequest.objects.create(
                email=f"delete{i}@example.com",
                request_type="data",
                status=status,
            )
            assert deletion.status == status

    def test_deletion_request_types(self):
        """Test deletion request types."""
        account_del = DataDeletionRequest.objects.create(
            email="acc@example.com",
            request_type="account",
        )
        data_del = DataDeletionRequest.objects.create(
            email="data@example.com",
            request_type="data",
        )
        assert account_del.request_type == "account"
        assert data_del.request_type == "data"

    def test_deletion_request_timestamps(self):
        """Test deletion request timestamps."""
        deletion = DataDeletionRequest.objects.create(
            email="time@example.com",
            request_type="account",
        )
        assert deletion.created_at is not None
        assert deletion.verified_at is None
        assert deletion.processed_at is None

    def test_deletion_request_str_representation(self):
        """Test deletion request string representation."""
        deletion = DataDeletionRequest.objects.create(
            email="strtest@example.com",
            request_type="account",
            status="pending",
        )
        assert "strtest@example.com" in str(deletion)
        assert "Account Deletion" in str(deletion)
