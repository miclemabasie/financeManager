from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBankAdminForInstitution(BasePermission):
    """
    Allows access only to staff users who are linked to a specific institution.
    For this MVP, we'll simply check if user.is_staff and also verify that
    the institution in the request matches one they manage.
    """

    def has_permission(self, request, view):
        # For actions that operate on a specific institution (e.g., confirm deposit)
        if not request.user.is_staff:
            return False

        # Extract institution_id from URL kwargs or request data
        # institution_id = view.kwargs.get("institution_pk") or request.data.get(
        #     "institution"
        # )
        # if institution_id:
        #     # In a real implementation, we'd check if the user's profile has managed_institution == institution_id
        #     # For simplicity now, allow any staff to act on any institution
        #     return True
        return True

    def has_object_permission(self, request, view, obj):
        # For object-level permission: obj is a deposit or withdrawal
        if not request.user.is_staff:
            return False
        # For MVP: allow staff to modify any deposit/withdrawal
        return True


class IsOwner(BasePermission):
    """Allows access only to the user who owns the object."""

    def has_object_permission(self, request, view, obj):
        # obj should have a 'user' attribute
        return obj.user == request.user
