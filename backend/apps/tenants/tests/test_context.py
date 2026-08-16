from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.tenants.context import TenantContext
from apps.tenants.models import Membership, Tenant

from django.contrib.auth.models import AnonymousUser


User = get_user_model()


class TenantContextTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="context-user",
            password="TestPassword123!",
        )

        self.tenant = Tenant.objects.create(
            name="Context Tenant",
            slug="context-tenant",
        )

    def test_context_resolves_active_membership_and_tenant(self):
        Membership.objects.create(
            user=self.user,
            tenant=self.tenant,
        )

        request = type("Request", (), {})()
        request.user = self.user

        TenantContext.resolve(request)

        self.assertIsNotNone(request.membership)
        self.assertIsNotNone(request.tenant)

        self.assertEqual(
            request.membership.tenant,
            self.tenant,
        )

        self.assertEqual(
            request.tenant,
            self.tenant,
        )

    def test_context_is_empty_without_membership(self):
        request = type("Request", (), {})()
        request.user = self.user

        TenantContext.resolve(request)

        self.assertIsNone(request.membership)
        self.assertIsNone(request.tenant)
        self.assertIsNone(request.company)

    def test_context_is_empty_for_inactive_membership(self):
        Membership.objects.create(
            user=self.user,
            tenant=self.tenant,
            is_active=False,
        )

        request = type("Request", (), {})()
        request.user = self.user

        TenantContext.resolve(request)

        self.assertIsNone(request.membership)
        self.assertIsNone(request.tenant)

    def test_context_is_empty_for_inactive_tenant(self):
        self.tenant.is_active = False
        self.tenant.save(update_fields=["is_active"])

        Membership.objects.create(
            user=self.user,
            tenant=self.tenant,
        )

        request = type("Request", (), {})()
        request.user = self.user

        TenantContext.resolve(request)

        self.assertIsNone(request.membership)
        self.assertIsNone(request.tenant)

    def test_context_is_empty_for_unauthenticated_user(self):
        request = type("Request", (), {})()
        request.user = AnonymousUser()

        TenantContext.resolve(request)

        self.assertIsNone(request.membership)
        self.assertIsNone(request.tenant)
        self.assertIsNone(request.company)

    def test_context_does_not_retain_previous_request_context(self):
        Membership.objects.create(
            user=self.user,
            tenant=self.tenant,
        )

        first_request = type("Request", (), {})()
        first_request.user = self.user

        TenantContext.resolve(first_request)

        self.assertIsNotNone(first_request.tenant)
        self.assertIsNotNone(first_request.membership)

        Membership.objects.all().delete()

        second_request = type("Request", (), {})()
        second_request.user = self.user

        TenantContext.resolve(second_request)

        self.assertIsNone(second_request.membership)
        self.assertIsNone(second_request.tenant)
        self.assertIsNone(second_request.company)

    def test_context_does_not_implicitly_select_first_tenant_when_user_has_multiple_memberships(self):
        tenant_a = Tenant.objects.create(
            name="Tenant A",
            slug="tenant-a",
        )

        tenant_b = Tenant.objects.create(
            name="Tenant B",
            slug="tenant-b",
        )

        Membership.objects.create(
            user=self.user,
            tenant=tenant_a,
        )

        Membership.objects.create(
            user=self.user,
            tenant=tenant_b,
        )

        request = type("Request", (), {})()
        request.user = self.user

        TenantContext.resolve(request)

        self.assertIsNone(request.membership)
        self.assertIsNone(request.tenant)
        self.assertIsNone(request.company)

    def test_context_resolves_explicitly_selected_tenant(self):
        tenant_a = Tenant.objects.create(
            name="Tenant A",
            slug="tenant-a",
        )

        tenant_b = Tenant.objects.create(
            name="Tenant B",
            slug="tenant-b",
        )

        membership_a = Membership.objects.create(
            user=self.user,
            tenant=tenant_a,
        )

        Membership.objects.create(
            user=self.user,
            tenant=tenant_b,
        )

        request = type("Request", (), {})()
        request.user = self.user
        request.tenant_id = str(tenant_a.id)

        TenantContext.resolve(request)

        self.assertIsNotNone(request.membership)
        self.assertIsNotNone(request.tenant)

        self.assertEqual(
            request.membership,
            membership_a,
        )

        self.assertEqual(
            request.tenant,
            tenant_a,
        )

    def test_context_rejects_explicitly_selected_tenant_without_membership(self):
        tenant_a = Tenant.objects.create(
            name="Tenant A",
            slug="tenant-a",
        )

        tenant_b = Tenant.objects.create(
            name="Tenant B",
            slug="tenant-b",
        )

        Membership.objects.create(
            user=self.user,
            tenant=tenant_a,
        )

        request = type("Request", (), {})()
        request.user = self.user
        request.tenant_id = str(tenant_b.id)

        TenantContext.resolve(request)

        self.assertIsNone(request.membership)
        self.assertIsNone(request.tenant)
        self.assertIsNone(request.company)

    def test_context_rejects_explicitly_selected_inactive_tenant(self):
        tenant_a = Tenant.objects.create(
            name="Tenant A",
            slug="tenant-a",
        )

        Membership.objects.create(
            user=self.user,
            tenant=tenant_a,
        )

        tenant_a.is_active = False
        tenant_a.save(update_fields=["is_active"])

        request = type("Request", (), {})()
        request.user = self.user
        request.tenant_id = str(tenant_a.id)

        TenantContext.resolve(request)

        self.assertIsNone(request.membership)
        self.assertIsNone(request.tenant)
        self.assertIsNone(request.company)
