# app/apps/finance/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedUUIDModel


class FinancialInstitution(TimeStampedUUIDModel):
    """Bank or microfinance institution that users can link to."""

    name = models.CharField(_("Name"), max_length=255, unique=True)
    momo_number = models.CharField(
        _("Mobile Money Number"),
        max_length=30,
        help_text=_("Phone number where users send savings (MTN/Orange MoMo)"),
    )
    contact_phone = models.CharField(_("Contact Phone"), max_length=30, blank=True)
    contact_email = models.EmailField(_("Contact Email"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Financial Institution")
        verbose_name_plural = _("Financial Institutions")
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserInstitutionAccount(TimeStampedUUIDModel):
    """Links a user to a financial institution (e.g., user has an account at a specific MF)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="institution_accounts",
    )
    institution = models.ForeignKey(
        FinancialInstitution,
        on_delete=models.CASCADE,
        related_name="user_accounts",
    )
    account_number = models.CharField(
        _("Account Number"),
        max_length=100,
        blank=True,
        help_text=_("Optional account number assigned by the institution"),
    )

    class Meta:
        verbose_name = _("User Institution Account")
        verbose_name_plural = _("User Institution Accounts")
        unique_together = [["user", "institution"]]

    def __str__(self):
        return f"{self.user.email} @ {self.institution.name}"


class DepositTransaction(TimeStampedUUIDModel):
    """Deposit request made by a user via Mobile Money."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        FAILED = "failed", _("Failed")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deposits",
    )
    institution = models.ForeignKey(
        FinancialInstitution,
        on_delete=models.CASCADE,
        related_name="deposits",
    )
    amount = models.DecimalField(_("Amount"), max_digits=12, decimal_places=0)
    momo_transaction_id = models.CharField(
        _("MoMo Transaction ID"),
        max_length=100,
        help_text=_("Transaction ID from user's Mobile Money app"),
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    notes = models.TextField(_("Notes"), blank=True)
    requested_at = models.DateTimeField(_("Requested At"), default=timezone.now)
    confirmed_at = models.DateTimeField(_("Confirmed At"), null=True, blank=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_deposits",
        verbose_name=_("Confirmed By"),
    )

    class Meta:
        verbose_name = _("Deposit Transaction")
        verbose_name_plural = _("Deposit Transactions")
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["status", "institution"]),
            models.Index(fields=["user", "-requested_at"]),
        ]

    def __str__(self):
        return f"Deposit {self.amount} by {self.user.email} - {self.status}"


class WithdrawalRequest(TimeStampedUUIDModel):
    """Withdrawal request made by a user."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SCHEDULED = "scheduled", _("Scheduled")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="withdrawals",
    )
    institution = models.ForeignKey(
        FinancialInstitution,
        on_delete=models.CASCADE,
        related_name="withdrawals",
    )
    amount = models.DecimalField(_("Amount"), max_digits=12, decimal_places=0)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    scheduled_payout_date = models.DateTimeField(
        _("Scheduled Payout Date"),
        null=True,
        blank=True,
        help_text=_("Date when institution will send MoMo"),
    )
    completed_at = models.DateTimeField(_("Completed At"), null=True, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_withdrawals",
        verbose_name=_("Processed By"),
    )

    class Meta:
        verbose_name = _("Withdrawal Request")
        verbose_name_plural = _("Withdrawal Requests")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "institution"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"Withdrawal {self.amount} by {self.user.email} - {self.status}"


class Expense(TimeStampedUUIDModel):
    """Simple expense log for personal budgeting."""

    CATEGORY_CHOICES = [
        ("food", _("Food & Groceries")),
        ("transport", _("Transport")),
        ("bills", _("Utilities & Bills")),
        ("entertainment", _("Entertainment")),
        ("health", _("Health")),
        ("education", _("Education")),
        ("savings", _("Savings")),
        ("other", _("Other")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    category = models.CharField(_("Category"), max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=0)
    expense_date = models.DateField(_("Expense Date"), default=timezone.now)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Expense")
        verbose_name_plural = _("Expenses")
        ordering = ["-expense_date"]
        indexes = [
            models.Index(fields=["user", "expense_date"]),
            models.Index(fields=["user", "category"]),
        ]

    def __str__(self):
        return f"{self.category}: {self.amount} on {self.expense_date}"
