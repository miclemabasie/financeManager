from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    FinancialInstitutionViewSet,
    UserInstitutionAccountViewSet,
    DepositTransactionViewSet,
    WithdrawalRequestViewSet,
    ExpenseViewSet,
    FinancialInstitutionAdminViewSet,
)

app_name = "finance"

router = DefaultRouter()
router.register(r"institutions", FinancialInstitutionViewSet, basename="institution")
router.register(
    r"my-institutions", UserInstitutionAccountViewSet, basename="user-institution"
)
router.register(r"deposits", DepositTransactionViewSet, basename="deposit")
router.register(r"withdrawals", WithdrawalRequestViewSet, basename="withdrawal")
router.register(r"expenses", ExpenseViewSet, basename="expense")

admin_router = DefaultRouter()
admin_router.register(
    r"admin/institutions",
    FinancialInstitutionAdminViewSet,
    basename="admin-institution",
)


urlpatterns = [
    path("", include(router.urls)),
    path("", include(admin_router.urls)),
]
