import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.notifications.models import (
    NotificationTemplate,
    Broadcast,
    Notification,
    UserNotificationSetting,
    EmailConfiguration,
)
from apps.notifications.choices import NotificationChannel, NotificationStatus, BroadcastStatus, TemplateType

User = get_user_model()


@pytest.mark.django_db
class TestNotificationTemplate:
    """Test NotificationTemplate model."""

    def test_create_email_template(self):
        """Test creating an email template."""
        user = User.objects.create_user(
            email="admin@example.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            password="pass123",
            is_staff=True,
        )
        template = NotificationTemplate.objects.create(
            name="Welcome Email",
            type=TemplateType.EMAIL,
            subject="Welcome to SmartSave",
            template="Hello {name}, welcome!",
            created_by=user,
        )
        assert template.name == "Welcome Email"
        assert template.type == TemplateType.EMAIL
        assert template.subject == "Welcome to SmartSave"
        assert template.is_active is True

    def test_create_sms_template(self):
        """Test creating an SMS template."""
        template = NotificationTemplate.objects.create(
            name="SMS Deposit",
            type=TemplateType.SMS,
            template="Your deposit of {amount} is pending confirmation.",
        )
        assert template.type == TemplateType.SMS
        assert template.subject == ""

    def test_template_unique_name(self):
        """Test that template names must be unique."""
        NotificationTemplate.objects.create(
            name="Unique Template",
            template="Test",
        )
        with pytest.raises(Exception):
            NotificationTemplate.objects.create(
                name="Unique Template",
                template="Another test",
            )

    def test_template_str_representation(self):
        """Test template string representation."""
        template = NotificationTemplate.objects.create(
            name="Test Template",
            template="Test body",
        )
        assert str(template) == "Test Template"


@pytest.mark.django_db
class TestBroadcast:
    """Test Broadcast model."""

    def setup_method(self):
        """Setup test data."""
        self.admin = User.objects.create_user(
            email="admin@example.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            password="pass123",
            is_staff=True,
        )
        self.template = NotificationTemplate.objects.create(
            name="Test Template",
            template="Test message",
            created_by=self.admin,
        )

    def test_create_broadcast(self):
        """Test creating a broadcast."""
        broadcast = Broadcast.objects.create(
            name="Test Broadcast",
            template=self.template,
            channel=NotificationChannel.EMAIL,
            created_by=self.admin,
        )
        assert broadcast.name == "Test Broadcast"
        assert broadcast.template == self.template
        assert broadcast.status == BroadcastStatus.DRAFT
        assert broadcast.total_recipients == 0

    def test_broadcast_statuses(self):
        """Test all broadcast statuses."""
        statuses = ["draft", "scheduled", "sent", "failed"]
        for status in statuses:
            broadcast = Broadcast.objects.create(
                name=f"Broadcast {status}",
                template=self.template,
                status=status,
            )
            assert broadcast.status == status

    def test_broadcast_channels(self):
        """Test broadcast channels."""
        email_broadcast = Broadcast.objects.create(
            name="Email Broadcast",
            template=self.template,
            channel=NotificationChannel.EMAIL,
        )
        sms_broadcast = Broadcast.objects.create(
            name="SMS Broadcast",
            template=self.template,
            channel=NotificationChannel.SMS,
        )
        assert email_broadcast.channel == NotificationChannel.EMAIL
        assert sms_broadcast.channel == NotificationChannel.SMS

    def test_broadcast_str_representation(self):
        """Test broadcast string representation."""
        broadcast = Broadcast.objects.create(
            name="Test Broadcast",
            template=self.template,
            status=BroadcastStatus.DRAFT,
        )
        assert "Test Broadcast" in str(broadcast)
        assert "Draft" in str(broadcast)


@pytest.mark.django_db
class TestNotification:
    """Test Notification model."""

    def setup_method(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        self.template = NotificationTemplate.objects.create(
            name="Test Template",
            template="Test message",
        )

    def test_create_notification(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            user=self.user,
            recipient=self.user.email,
            channel=NotificationChannel.EMAIL,
            subject="Test",
            body="Test message",
            template=self.template,
        )
        assert notification.user == self.user
        assert notification.channel == NotificationChannel.EMAIL
        assert notification.status == NotificationStatus.PENDING

    def test_notification_statuses(self):
        """Test all notification statuses."""
        statuses = ["pending", "sent", "failed", "bounced"]
        for i, status in enumerate(statuses):
            notification = Notification.objects.create(
                recipient=f"user{i}@example.com",
                channel=NotificationChannel.EMAIL,
                body="Test",
                status=status,
            )
            assert notification.status == status

    def test_notification_channels(self):
        """Test notification channels."""
        email_notif = Notification.objects.create(
            recipient="test@example.com",
            channel=NotificationChannel.EMAIL,
            body="Test",
        )
        sms_notif = Notification.objects.create(
            phone_number="+237699123456",
            channel=NotificationChannel.SMS,
            body="Test",
        )
        assert email_notif.channel == NotificationChannel.EMAIL
        assert sms_notif.channel == NotificationChannel.SMS

    def test_notification_sent(self):
        """Test marking notification as sent."""
        notification = Notification.objects.create(
            user=self.user,
            recipient=self.user.email,
            channel=NotificationChannel.EMAIL,
            body="Test",
        )
        notification.status = NotificationStatus.SENT
        notification.sent_at = timezone.now()
        notification.save()
        notification.refresh_from_db()
        assert notification.status == NotificationStatus.SENT
        assert notification.sent_at is not None

    def test_notification_with_context(self):
        """Test notification with context data."""
        context = {"name": "John", "amount": "50000"}
        notification = Notification.objects.create(
            recipient="test@example.com",
            channel=NotificationChannel.EMAIL,
            body="Test",
            context=context,
        )
        assert notification.context == context

    def test_notification_str_representation(self):
        """Test notification string representation."""
        notification = Notification.objects.create(
            user=self.user,
            channel=NotificationChannel.EMAIL,
            body="Test",
            status=NotificationStatus.PENDING,
        )
        assert "email" in str(notification).lower()
        assert "pending" in str(notification).lower()


@pytest.mark.django_db
class TestUserNotificationSetting:
    """Test UserNotificationSetting model."""

    def test_create_notification_setting(self):
        """Test creating notification settings."""
        user = User.objects.create_user(
            email="setting@example.com",
            username="setting",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        setting = UserNotificationSetting.objects.create(
            user=user,
            email_enabled=True,
            sms_enabled=False,
        )
        assert setting.user == user
        assert setting.email_enabled is True
        assert setting.sms_enabled is False

    def test_notification_setting_defaults(self):
        """Test default notification settings."""
        user = User.objects.create_user(
            email="default@example.com",
            username="default",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        setting = UserNotificationSetting.objects.create(user=user)
        assert setting.email_enabled is True
        assert setting.sms_enabled is False
        assert setting.receive_security_emails is True
        assert setting.receive_marketing_emails is False

    def test_notification_setting_one_to_one(self):
        """Test that user can have only one setting."""
        user = User.objects.create_user(
            email="onetoone@example.com",
            username="onetoone",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        UserNotificationSetting.objects.create(user=user)
        with pytest.raises(Exception):
            UserNotificationSetting.objects.create(user=user)

    def test_notification_setting_str_representation(self):
        """Test setting string representation."""
        user = User.objects.create_user(
            email="str@example.com",
            username="str",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        setting = UserNotificationSetting.objects.create(user=user)
        assert "str@example.com" in str(setting)


@pytest.mark.django_db
class TestEmailConfiguration:
    """Test EmailConfiguration model."""

    def test_create_email_config(self):
        """Test creating email configuration."""
        config = EmailConfiguration.objects.create(
            name="Gmail",
            host="smtp.gmail.com",
            port=587,
            username="test@gmail.com",
            password="secret",
            from_email="test@gmail.com",
        )
        assert config.name == "Gmail"
        assert config.host == "smtp.gmail.com"
        assert config.port == 587
        assert config.is_active is False

    def test_only_one_active_config(self):
        """Test that only one config can be active."""
        config1 = EmailConfiguration.objects.create(
            name="Gmail",
            host="smtp.gmail.com",
            from_email="test@gmail.com",
            is_active=True,
        )
        config2 = EmailConfiguration.objects.create(
            name="SendGrid",
            host="smtp.sendgrid.net",
            from_email="sendgrid@example.com",
            is_active=True,
        )
        config1.refresh_from_db()
        assert config1.is_active is False
        assert config2.is_active is True

    def test_email_config_get_active(self):
        """Test getting active email config."""
        EmailConfiguration.objects.create(
            name="Gmail",
            host="smtp.gmail.com",
            from_email="test@gmail.com",
            is_active=False,
        )
        active_config = EmailConfiguration.objects.create(
            name="SendGrid",
            host="smtp.sendgrid.net",
            from_email="sendgrid@example.com",
            is_active=True,
        )
        assert EmailConfiguration.get_active() == active_config

    def test_email_config_defaults(self):
        """Test email config defaults."""
        config = EmailConfiguration.objects.create(
            name="Test",
            host="smtp.test.com",
            from_email="test@example.com",
        )
        assert config.use_tls is True
        assert config.use_ssl is False
        assert config.timeout == 30

    def test_email_config_str_representation(self):
        """Test email config string representation."""
        config = EmailConfiguration.objects.create(
            name="Gmail",
            host="smtp.gmail.com",
            from_email="test@gmail.com",
            is_active=True,
        )
        assert "Gmail" in str(config)
        assert "active" in str(config)
