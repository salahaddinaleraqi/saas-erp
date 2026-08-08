from apps.tenants.context import TenantContext


class TenantContextMixin:
    """
    Resolves tenant context after DRF authentication
    and before permission checks.
    """

    def perform_authentication(self, request):
        super().perform_authentication(request)
        TenantContext.resolve(request)