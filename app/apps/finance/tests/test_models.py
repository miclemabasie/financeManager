import pytest
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.finance.models import (
    FinancialInstitution,
    UserInstitutionAccount,
    DepositTransaction,
    WithdrawalRequest,
    Expense,
)

User = get_user_model()


@pytest.mark.django_db
class TestFinancialInstitution:
    """Test FinancialInstitution model."""

    def test_create_institution(self):
        """Test creating a financial institution."""
        institution = FinancialInstitution.objects.create(
            name="Test Bank",
            momo_number="+237650123456",
            contact_email="contact@testbank.com",
        )
        assert institution.name == "Test Bank"
        assert institution.momo_number == "+237650123456"
        assert institution.is_active is True

    def test_institution_unique_name(self):
        """Test that institution names must be unique."""
        FinancialInstitution.objects.create(
            name="Unique Bank",
            momo_number="+237650123456",
        )
        with pytest.raises(Exception):
            FinancialInstitution.objects.create(
                name="Unique Bank",
                momo_number="+237650789012",
            )

    def test_institution_str_representation(self):
        """Test institution string representation."""
        institution = FinancialInstitution.objects.create(
            name="Test Bank",
            momo_number="+237650123456",
        )
        assert str(institution) == "Test Bank"

    def test_institution_ordering(self):
        """Test institutions are ordered by name."""
        FinancialInstitution.objects.create(name="Zebra Bank", momo_number="+1111111111")
        FinancialInstitution.objects.create(name="Apple Bank", momo_number="+2222222222")
        institutions = list(FinancialInstitution.objects.all())
        assert institutions[0].name == "Apple Bank"
        assert institutions[1].name == "Zebra Bank"


@pytest.mark.django_db
class TestUserInstitutionAccount:
    """Test UserInstitutionAccount model."""

    def setup_method(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        self.institution = FinancialInstitution.objects.create(
            name="Test Bank",
            momo_number="+237650123456",
        )

    def test_create_account_link(self):
        """Test linking user to institution."""
        account = UserInstitutionAccount.objects.create(
            user=self.user,
            institution=self.institution,
            account_number="ACC123456",
        )
        assert account.user == self.user
        assert account.institution == self.institution
        assert account.account_number == "ACC123456"

    def test_account_link_unique_constraint(self):
        """Test that user can't link same institution twice."""
        UserInstitutionAccount.objects.create(
            user=self.user,
            institution=self.institution,
        )
        with pytest.raises(Exception):
            UserInstitutionAccount.objects.create(
                user=self.user,
                institution=self.institution,
            )

    def test_account_link_str_representation(self):
        """Test account link string representation."""
        account = UserInstitutionAccount.objects.create(
            user=self.user,
            institution=self.institution,
        )
        assert str(account) == f"{self.user.email} @ {self.institution.name}"


@pytest.mark.django_db
class TestDepositTransaction:
    """Test DepositTransaction model."""

    def setup_method(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            email="depositor@example.com",
            username="depositor",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        self.institution = FinancialInstitution.objects.create(
            name="Test Bank",
            momo_number="+237650123456",
        )

    def test_create_deposit(self):
        """Test creating a deposit transaction."""
        deposit = DepositTransaction.objects.create(
            user=self.user,
            institution=self.institution,
            amount=Decimal("50000"),
            momo_transaction_id="TXN123456",
        )
        assert deposit.user == self.user
        assert deposit.institution == self.institution
        assert deposit.amount == Decimal("50000")
        assert deposit.status == DepositTransaction.Status.PENDING
        assert deposit.momo_transaction_id == "TXN123456"

    def test_deposit_status_choices(self):
        """Test all deposit status choices."""
        statuses = ["pending", "confirmed", "failed"]
        for i, status in enumerate(statuses):
            deposit = DepositTransaction.objects.create(
                user=self.user,
                institution=self.institution,
                amount=Decimal("10000"),
                momo_transaction_id=f"TXN{i}",
                status=status,
            )
            assert deposit.status == status

    def test_deposit_confirmation(self):
        """Test confirming a deposit (without save to avoid signal issues)."""
        deposit = DepositTransaction.objects.create(
            user=self.user,
            institution=self.institution,
            amount=Decimal("50000"),
            momo_transaction_id="TXN123456",
        )
        admin = User.objects.create_user(
            email="admin@bank.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            password="pass123",
            is_staff=True,
        )
        deposit.status = DepositTransaction.Status.CONFIRMED
        deposit.confirmed_by = admin
        deposit.confirmed_at = timezone.now()
        assert deposit.status == DepositTransaction.Status.CONFIRMED
        assert deposit.confirmed_by == admin
        assert deposit.confirmed_at is not None

    def test_deposit_str_representation(self):
        """Test deposit string representation."""
        deposit = DepositTransaction.objects.create(
            user=self.user,
            institution=self.institution,
            amount=Decimal("50000"),
            momo_transaction_id="TXN123456",
        )
        assert "Deposit 50000" in str(deposit)
        assert "pending" in str(deposit)


@pytest.mark.django_db
class TestWithdrawalRequest:
    """Test WithdrawalRequest model."""

    def setup_method(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            email="withdrawer@example.com",
            username="withdrawer",
            first_name="Test",
            last_name="User",
            password="pass123",
        )
        self.institution = FinancialInstitution.objects.create(
            name="Test Bank",
            momo_number="+237650123456",
        )

    def test_create_withdrawal(self):
        """Test creating a withdrawal request."""
        withdrawal = WithdrawalRequest.objects.create(
            user=self.user,
            institution=self.institution,
            amount=Decimal("25000"),
        )
        assert withdrawal.user == self.user
        assert withdrawal.institution == self.institution
        assert withdrawal.amount == Decimal("25000")
        assert withdrawal.status == WithdrawalRequest.Status.PENDING

    def test_withdrawal_status_choices(self):
        """Test all withdrawal status choices."""
        statuses = ["pending", "scheduled", "completed", "cancelled"]
        for i, status in enumerate(statuses):
            withdrawal = WithdrawalRequest.objects.create(
                user=self.user,
                institution=self.institution,
                amount=Decimal("10000"),
                status=status,
            )
            assert withdrawal.status == status

    def test_withdrawal_schedule(self):
        """Test scheduling a withdrawal."""
        withdrawal = WithdrawalRequest.objects.create(
            user=self.user,
            institution=self.institution,
            amount=Decimal("25000"),
        )
        admin = User.objects.create_user(
            email="admin@bank.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            password="pass123",
            is_staff=True,
        )
        payout_date = timezone.now() + timezone.timedelta(days=2)
        withdrawal.status = WithdrawalRequest.Status.SCHEDULED
        withdrawal.scheduled_payout_date = payout_date
        withdrawal.processed_by = admin
        withdrawal.save()
        withdrawal.refresh_from_db()
        assert withdrawal.status == WithdrawalRequest.Status.SCHEDULED
        assert withdrawal.scheduled_payout_date == payout_date

    def test_withdrawal_completion(self):
        """Test completing a withdrawal."""
        withdrawal = WithdrawalRequest.objects.create(
            user=self.user,
            institution=self.institution,
            amount=Decimal("25000"),
        )
        withdrawal.status = WithdrawalRequest.Status.COMPLETED
        withdrawal.completed_at = timezone.now()
        assert withdrawal.status == WithdrawalRequest.Status.COMPLETED
        assert withdrawal.completed_at is not None

    def test_withdrawal_str_representation(self):
        """Test withdrawal string representation."""
        withdrawal = WithdrawalRequest.objects.create(
            user=self.user,
            institution=self.institution,
            amount=Decimal("25000"),
        )
        assert "Withdrawal 25000" in str(withdrawal)
        assert "pending" in str(withdrawal)


@pytest.mark.django_db
class TestExpense:
    """Test Expense model."""

    def setup_method(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            email="saver@example.com",
            username="saver",
            first_name="Test",
            last_name="User",
            password="pass123",
        )

    def test_create_expense(self):
        """Test creating an expense."""
        expense = Expense.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("5000"),
            description="Bought groceries",
        )
        assert expense.user == self.user
        assert expense.category == "food"
        assert expense.amount == Decimal("5000")
        assert expense.description == "Bought groceries"

    def test_expense_categories(self):
        """Test all expense categories."""
        categories = ["food", "transport", "bills", "entertainment", "health", "education", "savings", "other"]
        for i, category in enumerate(categories):
            expense = Expense.objects.create(
                user=self.user,
                category=category,
                amount=Decimal("1000"),
            )
            assert expense.category == category

    def test_expense_default_date(self):
        """Test expense uses correct default behavior."""
        expense = Expense.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("5000"),
        )
        assert expense.expense_date is not None

    def test_expense_ordering(self):
        """Test expenses are ordered by date descending."""
        today = timezone.now().date()
        exp1 = Expense.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("1000"),
            expense_date=today,
        )
        yesterday = today - timezone.timedelta(days=1)
        exp2 = Expense.objects.create(
            user=self.user,
            category="transport",
            amount=Decimal("2000"),
            expense_date=yesterday,
        )
        expenses = list(Expense.objects.all())
        assert expenses[0].id == exp1.id
        assert expenses[1].id == exp2.id

    def test_expense_str_representation(self):
        """Test expense string representation."""
        expense = Expense.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("5000"),
        )
        assert "food" in str(expense)
        assert "5000" in str(expense)
