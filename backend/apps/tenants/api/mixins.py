from apps.tenants.context import TenantContext


class TenantContextMixin:
    """
    Resolves tenant context after DRF authentication
    and before permission checks.
    """

    TENANT_HEADER = "HTTP_X_TENANT_ID"

    def perform_authentication(self, request):
        super().perform_authentication(request)

        tenant_id = request.META.get(self.TENANT_HEADER)

        if tenant_id:
            request.tenant_id = tenant_id

        TenantContext.resolve(request)
