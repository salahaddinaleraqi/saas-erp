from apps.tenants.models import Membership


def get_current_membership(user):
    """
    Returns the current active membership for the authenticated user.

    Current implementation:
    - Assumes the user belongs to a single active tenant.

    Future implementation:
    - Will support multiple memberships.
    - Will support switching between tenants.
    """

    if not user or not user.is_authenticated:
        return None

    return (
        Membership.objects
        .select_related("tenant")
        .filter(
            user=user,
            is_active=True,
            tenant__is_active=True,
        )
        .first()
    )