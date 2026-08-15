from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import success_response
from apps.tenants.models import Company
from apps.tenants.utils import (
    get_current_membership,
    get_current_tenant,
)

from .mixins import TenantContextMixin
from .permissions import IsTenantMember
from .serializers import CompanySerializer


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


class CompanyListView(TenantContextMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsTenantMember,
    ]

    def get(self, request):
        companies = Company.objects.for_tenant(
            request.tenant
        )

        serializer = CompanySerializer(
            companies,
            many=True,
        )

        return success_response(
            message="Companies retrieved successfully.",
            data=serializer.data,
        )

    def post(self, request):
        serializer = CompanySerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        company = serializer.save(
            tenant=request.tenant
        )

        return success_response(
            message="Company created successfully.",
            data=CompanySerializer(company).data,
            status_code=status.HTTP_201_CREATED,
        )


class CompanyDetailView(TenantContextMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsTenantMember,
    ]

    def get(self, request, pk):
        company = get_object_or_404(
            Company.objects.for_tenant(request.tenant),
            pk=pk,
        )

        serializer = CompanySerializer(company)

        return success_response(
            message="Company retrieved successfully.",
            data=serializer.data,
        )

    def patch(self, request, pk):
        company = get_object_or_404(
            Company.objects.for_tenant(request.tenant),
            pk=pk,
        )

        serializer = CompanySerializer(
            company,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        company = serializer.save()

        return success_response(
            message="Company updated successfully.",
            data=CompanySerializer(company).data,
        )

    def delete(self, request, pk):
        company = get_object_or_404(
            Company.objects.for_tenant(request.tenant),
            pk=pk,
        )

        company.delete()

        return success_response(
            message="Company deleted successfully.",
            data=None,
        )
