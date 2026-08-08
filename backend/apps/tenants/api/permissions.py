from rest_framework.permissions import BasePermission


class IsTenantMember(BasePermission):
    """
    Allows access only to authenticated users
    with a valid tenant membership context.
    """

    message = "You do not have an active tenant membership."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.membership is not None
            and request.tenant is not None
        )