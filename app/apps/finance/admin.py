from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    FinancialInstitution,
    UserInstitutionAccount,
    DepositTransaction,
    WithdrawalRequest,
    Expense,
)


class InstitutionFilter(SimpleListFilter):
    title = "Institution"
    parameter_name = "institution"

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            institutions = FinancialInstitution.objects.all()
        else:
            # Non-superuser staff: only show their managed institution (requires profile extension)
            # For simplicity, we assume staff can see all; override later if needed
            institutions = FinancialInstitution.objects.all()
        return [(i.id, i.name) for i in institutions]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(institution_id=self.value())
        return queryset


@admin.register(FinancialInstitution)
class FinancialInstitutionAdmin(admin.ModelAdmin):
    list_display = ["name", "momo_number", "contact_phone", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "momo_number"]


@admin.register(UserInstitutionAccount)
class UserInstitutionAccountAdmin(admin.ModelAdmin):
    list_display = ["user", "institution", "account_number", "created_at"]
    list_filter = [InstitutionFilter]
    search_fields = ["user__email", "user__username", "account_number"]
    raw_id_fields = ["user", "institution"]


@admin.register(DepositTransaction)
class DepositTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "institution",
        "amount",
        "status",
        "requested_at",
        "confirmed_at",
    ]
    list_filter = ["status", InstitutionFilter]
    search_fields = ["user__email", "momo_transaction_id"]
    readonly_fields = ["requested_at", "confirmed_at", "confirmed_by"]
    actions = ["confirm_deposits"]

    def confirm_deposits(self, request, queryset):
        updated = 0
        for deposit in queryset.filter(status=DepositTransaction.Status.PENDING):
            deposit.status = DepositTransaction.Status.CONFIRMED
            deposit.confirmed_at = timezone.now()
            deposit.confirmed_by = request.user
            deposit.save()
            updated += 1
        self.message_user(request, f"{updated} deposit(s) confirmed.")

    confirm_deposits.short_description = "Confirm selected deposits (mark as confirmed)"


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "institution",
        "amount",
        "status",
        "scheduled_payout_date",
        "completed_at",
    ]
    list_filter = ["status", InstitutionFilter]
    search_fields = ["user__email"]
    readonly_fields = ["created_at", "completed_at", "processed_by"]
    actions = ["schedule_withdrawals", "complete_withdrawals"]

    def schedule_withdrawals(self, request, queryset):
        # This action expects a date to be entered; for simplicity, we'll just mark as scheduled with current date+1 day
        for w in queryset.filter(status=WithdrawalRequest.Status.PENDING):
            w.status = WithdrawalRequest.Status.SCHEDULED
            w.scheduled_payout_date = timezone.now() + timezone.timedelta(days=1)
            w.save()
        self.message_user(request, "Selected withdrawals scheduled for tomorrow.")

    schedule_withdrawals.short_description = (
        "Schedule selected withdrawals (set date to tomorrow)"
    )

    def complete_withdrawals(self, request, queryset):
        updated = 0
        for w in queryset.filter(status=WithdrawalRequest.Status.SCHEDULED):
            w.status = WithdrawalRequest.Status.COMPLETED
            w.completed_at = timezone.now()
            w.processed_by = request.user
            w.save()
            updated += 1
        self.message_user(request, f"{updated} withdrawal(s) marked as completed.")

    complete_withdrawals.short_description = (
        "Complete selected withdrawals (mark as done)"
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["user", "category", "amount", "expense_date"]
    list_filter = ["category", "expense_date"]
    search_fields = ["user__email", "description"]
