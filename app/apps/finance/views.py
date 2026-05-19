from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum

from .models import (
    FinancialInstitution,
    UserInstitutionAccount,
    DepositTransaction,
    WithdrawalRequest,
    Expense,
)
from .serializers import (
    FinancialInstitutionSerializer,
    UserInstitutionAccountSerializer,
    DepositTransactionSerializer,
    WithdrawalRequestSerializer,
    ExpenseSerializer,
)
from .permissions import IsBankAdminForInstitution, IsOwner


class FinancialInstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    """List available financial institutions."""

    queryset = FinancialInstitution.objects.filter(is_active=True)
    serializer_class = FinancialInstitutionSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserInstitutionAccountViewSet(viewsets.ModelViewSet):
    """Manage user's linked institutions."""

    serializer_class = UserInstitutionAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserInstitutionAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DepositTransactionViewSet(viewsets.ModelViewSet):
    """Deposit requests (create, list, confirm)."""

    serializer_class = DepositTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return DepositTransaction.objects.all()
        return DepositTransaction.objects.filter(user=user)

    @action(
        detail=True, methods=["patch"], permission_classes=[IsBankAdminForInstitution]
    )
    def confirm(self, request, pk=None):
        deposit = self.get_object()
        if deposit.status != DepositTransaction.Status.PENDING:
            return Response(
                {"error": "Deposit already confirmed or failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deposit.status = DepositTransaction.Status.CONFIRMED
        deposit.confirmed_at = timezone.now()
        deposit.confirmed_by = request.user
        deposit.save()
        # TODO: Trigger notification via signals or Celery
        return Response({"status": "confirmed"})


class WithdrawalRequestViewSet(viewsets.ModelViewSet):
    """Withdrawal requests (create, list, schedule, complete)."""

    serializer_class = WithdrawalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return WithdrawalRequest.objects.all()
        return WithdrawalRequest.objects.filter(user=user)

    @action(
        detail=True, methods=["patch"], permission_classes=[IsBankAdminForInstitution]
    )
    def schedule(self, request, pk=None):
        withdrawal = self.get_object()
        if withdrawal.status != WithdrawalRequest.Status.PENDING:
            return Response(
                {"error": "Withdrawal already scheduled or completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        withdrawal.status = WithdrawalRequest.Status.SCHEDULED
        # Optionally accept a date from request body
        withdrawal.scheduled_payout_date = request.data.get(
            "scheduled_payout_date", timezone.now() + timezone.timedelta(days=1)
        )
        withdrawal.save()
        return Response(
            {
                "status": "scheduled",
                "scheduled_payout_date": withdrawal.scheduled_payout_date,
            }
        )

    @action(
        detail=True, methods=["patch"], permission_classes=[IsBankAdminForInstitution]
    )
    def complete(self, request, pk=None):
        withdrawal = self.get_object()
        if withdrawal.status != WithdrawalRequest.Status.SCHEDULED:
            return Response(
                {"error": "Withdrawal must be scheduled before completion."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        withdrawal.status = WithdrawalRequest.Status.COMPLETED
        withdrawal.completed_at = timezone.now()
        withdrawal.processed_by = request.user
        withdrawal.save()
        return Response({"status": "completed"})


class ExpenseViewSet(viewsets.ModelViewSet):
    """Expense tracking (CRUD)."""

    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Spending summary grouped by category for a period."""
        period = request.query_params.get("period", "week")  # week, month, year
        now = timezone.now()
        if period == "week":
            start_date = now - timezone.timedelta(days=7)
        elif period == "month":
            start_date = now - timezone.timedelta(days=30)
        elif period == "year":
            start_date = now - timezone.timedelta(days=365)
        else:
            start_date = None

        queryset = self.get_queryset()
        if start_date:
            queryset = queryset.filter(expense_date__gte=start_date)

        summary = (
            queryset.values("category").annotate(total=Sum("amount")).order_by("-total")
        )
        return Response(summary)


class FinancialInstitutionAdminViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for financial institutions – admin only.
    """

    queryset = FinancialInstitution.objects.all()
    serializer_class = FinancialInstitutionSerializer
    permission_classes = [permissions.IsAdminUser]  # only superuser/staff
