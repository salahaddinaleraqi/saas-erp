from django.test import SimpleTestCase
from django.test import RequestFactory

from apps.tenants.utils import (
    get_current_membership,
    get_current_tenant,
)


class TenantUtilsTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_current_tenant_returns_request_tenant(self):
        request = self.factory.get("/")

        tenant = object()
        request.tenant = tenant

        result = get_current_tenant(request)

        self.assertIs(result, tenant)

    def test_get_current_tenant_returns_none_when_not_resolved(self):
        request = self.factory.get("/")

        result = get_current_tenant(request)

        self.assertIsNone(result)

    def test_get_current_membership_returns_request_membership(self):
        request = self.factory.get("/")

        membership = object()
        request.membership = membership

        result = get_current_membership(request)

        self.assertIs(result, membership)

    def test_get_current_membership_returns_none_when_not_resolved(self):
        request = self.factory.get("/")

        result = get_current_membership(request)

        self.assertIsNone(result)