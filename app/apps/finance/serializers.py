from rest_framework import serializers
from django.utils import timezone

from .models import (
    FinancialInstitution,
    UserInstitutionAccount,
    DepositTransaction,
    WithdrawalRequest,
    Expense,
)


class FinancialInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialInstitution
        fields = [
            "pkid",
            "id",
            "name",
            "momo_number",
            "contact_phone",
            "contact_email",
            "is_active",
        ]
        read_only_fields = ["id"]


class UserInstitutionAccountSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = UserInstitutionAccount
        fields = [
            "pkid",
            "id",
            "user",
            "institution",
            "institution_name",
            "account_number",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class DepositTransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = DepositTransaction
        fields = [
            "pkid",
            "id",
            "user",
            "user_email",
            "institution",
            "institution_name",
            "amount",
            "momo_transaction_id",
            "status",
            "notes",
            "requested_at",
            "confirmed_at",
            "confirmed_by",
        ]
        read_only_fields = [
            "id",
            "status",
            "requested_at",
            "confirmed_at",
            "confirmed_by",
            "user",
        ]

    def create(self, validated_data):
        # Automatically set user from request context
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = WithdrawalRequest
        fields = [
            "pkid",
            "id",
            "user",
            "user_email",
            "institution",
            "institution_name",
            "amount",
            "status",
            "scheduled_payout_date",
            "completed_at",
            "notes",
            "processed_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "completed_at",
            "processed_by",
            "created_at",
            "user",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "pkid",
            "id",
            "user",
            "category",
            "amount",
            "expense_date",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
