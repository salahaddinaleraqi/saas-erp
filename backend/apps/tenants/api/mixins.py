from apps.tenants.context import TenantContext


class TenantContextMixin:
    """
    Resolves tenant context after DRF authentication.
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        TenantContext.resolve(request)