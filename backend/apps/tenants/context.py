from apps.tenants.services import (
    get_current_membership,
    get_membership_for_tenant,
)


class TenantContext:
    """
    Builds the tenant context for an authenticated request.
    """

    @staticmethod
    def resolve(request):
        request.membership = None
        request.tenant = None
        request.company = None

        if not request.user or not request.user.is_authenticated:
            return

        tenant_id = getattr(request, "tenant_id", None)

        if tenant_id:
            membership = get_membership_for_tenant(
                request.user,
                tenant_id,
            )
        else:
            membership = get_current_membership(request.user)

        if membership:
            request.membership = membership
            request.tenant = membership.tenant

        # Current company selection will be implemented later.