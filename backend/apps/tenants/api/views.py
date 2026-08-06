from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import success_response
from .mixins import TenantContextMixin


class TenantContextView(TenantContextMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = request.membership
        tenant = request.tenant

        data = {
            "user": str(request.user),
            "membership": None,
            "tenant": None,
        }

        if membership:
            data["membership"] = str(membership.id)

        if tenant:
            data["tenant"] = {
                "id": str(tenant.id),
                "name": tenant.name,
                "slug": tenant.slug,
            }

        return success_response(
            message="Tenant context retrieved successfully.",
            data=data,
        )