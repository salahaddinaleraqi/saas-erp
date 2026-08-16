from apps.tenants.models import Membership


def get_current_membership(user):
    """
    Returns the current active membership for the authenticated user.

    If the user has exactly one active membership, it is selected
    automatically.

    If the user belongs to multiple active tenants, no tenant is
    selected implicitly.
    """

    if not user or not user.is_authenticated:
        return None

    memberships = (
        Membership.objects
        .select_related("tenant")
        .filter(
            user=user,
            is_active=True,
            tenant__is_active=True,
        )
    )

    if memberships.count() != 1:
        return None

    return memberships.first()


def get_membership_for_tenant(user, tenant_id):
    """
    Returns the user's active membership for the explicitly selected
    tenant.

    Returns None if the user is not an active member of the tenant
    or if the tenant is inactive.
    """

    if not user or not user.is_authenticated:
        return None

    if not tenant_id:
        return None

    return (
        Membership.objects
        .select_related("tenant")
        .filter(
            user=user,
            tenant_id=tenant_id,
            is_active=True,
            tenant__is_active=True,
        )
        .first()
    )
