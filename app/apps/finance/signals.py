from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from apps.notifications.utils import send_notification
from apps.notifications.choices import NotificationChannel
from .models import DepositTransaction, WithdrawalRequest


@receiver(post_save, sender=DepositTransaction)
def deposit_confirmed_notification(sender, instance, created, **kwargs):
    """Send SMS/email when a deposit is confirmed."""
    if not created and instance.status == DepositTransaction.Status.CONFIRMED:
        # Check if status changed from pending to confirmed
        # For simplicity, send notification on every confirmed save
        user = instance.user
        context = {
            "amount": str(instance.amount),
            "institution": instance.institution.name,
            "transaction_id": str(instance.id)[:8],
        }
        send_notification(
            user=user,
            channel=NotificationChannel.SMS,
            template_name="deposit_confirmed",  # you need to create this template
            context=context,
        )
        # Also send email if user has email
        if user.email:
            send_notification(
                user=user,
                channel=NotificationChannel.EMAIL,
                template_name="deposit_confirmed_email",
                context=context,
            )


@receiver(post_save, sender=WithdrawalRequest)
def withdrawal_completed_notification(sender, instance, created, **kwargs):
    """Send SMS when a withdrawal is completed."""
    if not created and instance.status == WithdrawalRequest.Status.COMPLETED:
        user = instance.user
        context = {
            "amount": str(instance.amount),
            "institution": instance.institution.name,
        }
        send_notification(
            user=user,
            channel=NotificationChannel.SMS,
            template_name="withdrawal_completed",
            context=context,
        )
