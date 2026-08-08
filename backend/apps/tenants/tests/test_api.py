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

        access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
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