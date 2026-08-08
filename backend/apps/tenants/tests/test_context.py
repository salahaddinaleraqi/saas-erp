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