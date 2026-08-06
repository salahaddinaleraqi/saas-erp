from apps.tenants.services import get_current_membership


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

        membership = get_current_membership(request.user)

        if membership:
            request.membership = membership
            request.tenant = membership.tenant

        # Current company selection will be implemented later.