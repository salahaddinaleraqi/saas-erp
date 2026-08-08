from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import success_response
from apps.tenants.utils import (
    get_current_membership,
    get_current_tenant,
)

from .mixins import TenantContextMixin
from .permissions import IsTenantMember


class TenantContextView(TenantContextMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsTenantMember,
    ]

    def get(self, request):
        membership = get_current_membership(request)
        tenant = get_current_tenant(request)

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