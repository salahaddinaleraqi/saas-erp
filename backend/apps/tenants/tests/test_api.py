from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.tenants.models import Membership, Tenant
from apps.users.models import User


class TenantContextAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tenant-user",
            password="TestPassword123!",
        )

        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test-tenant",
        )

        self.membership = Membership.objects.create(
            user=self.user,
            tenant=self.tenant,
        )

        self.url = reverse("tenant-context")

    def authenticate(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "tenant-user",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    def test_authenticated_user_with_active_membership_can_access_context(self):
        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        self.assertEqual(
            response.data["data"]["membership"],
            str(self.membership.id),
        )

        self.assertEqual(
            response.data["data"]["tenant"]["id"],
            str(self.tenant.id),
        )

    def test_authenticated_user_without_membership_is_denied(self):
        self.membership.delete()

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_membership_is_denied(self):
        self.membership.is_active = False
        self.membership.save(update_fields=["is_active"])

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_tenant_is_denied(self):
        self.tenant.is_active = False
        self.tenant.save(update_fields=["is_active"])

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_is_denied(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_with_multiple_tenants_requires_tenant_header(self):
        tenant_b = Tenant.objects.create(
            name="Second Tenant",
            slug="second-tenant",
        )

        Membership.objects.create(
            user=self.user,
            tenant=tenant_b,
        )

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_authenticated_user_can_select_tenant_with_header(self):
        tenant_b = Tenant.objects.create(
            name="Second Tenant",
            slug="second-tenant",
        )

        membership_b = Membership.objects.create(
            user=self.user,
            tenant=tenant_b,
        )

        self.authenticate()

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            HTTP_X_TENANT_ID=str(tenant_b.id),
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["data"]["membership"],
            str(membership_b.id),
        )

        self.assertEqual(
            response.data["data"]["tenant"]["id"],
            str(tenant_b.id),
        )

    def test_authenticated_user_cannot_select_tenant_without_membership(self):
        tenant_b = Tenant.objects.create(
            name="Second Tenant",
            slug="second-tenant",
        )

        self.authenticate()

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            HTTP_X_TENANT_ID=str(tenant_b.id),
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_authenticated_user_cannot_select_inactive_tenant(self):
        tenant_b = Tenant.objects.create(
            name="Inactive Tenant",
            slug="inactive-tenant",
            is_active=False,
        )

        Membership.objects.create(
            user=self.user,
            tenant=tenant_b,
        )

        self.authenticate()

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            HTTP_X_TENANT_ID=str(tenant_b.id),
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_authenticated_user_cannot_select_nonexistent_tenant(self):
        self.authenticate()

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            HTTP_X_TENANT_ID="00000000-0000-0000-0000-000000000000",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
