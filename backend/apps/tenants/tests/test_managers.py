from django.test import TestCase

from apps.tenants.models import Company, Tenant


class TenantAwareManagerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tenant_a = Tenant.objects.create(
            name="Tenant A",
            slug="tenant-a",
        )

        cls.tenant_b = Tenant.objects.create(
            name="Tenant B",
            slug="tenant-b",
        )

        Company.objects.create(
            tenant=cls.tenant_a,
            name="Company A1",
            code="A1",
        )

        Company.objects.create(
            tenant=cls.tenant_a,
            name="Company A2",
            code="A2",
        )

        Company.objects.create(
            tenant=cls.tenant_b,
            name="Company B1",
            code="B1",
        )

    def test_for_tenant_returns_only_matching_records(self):
        companies = Company.objects.for_tenant(self.tenant_a)

        self.assertEqual(companies.count(), 2)

        self.assertQuerySetEqual(
            companies.order_by("code"),
            ["A1", "A2"],
            transform=lambda company: company.code,
        )

    def test_for_tenant_does_not_return_other_tenant_records(self):
        companies = Company.objects.for_tenant(self.tenant_a)

        codes = list(
            companies.values_list("code", flat=True)
        )

        self.assertNotIn("B1", codes)

    def test_for_tenant_with_none_fails_closed(self):
        companies = Company.objects.for_tenant(None)

        self.assertEqual(companies.count(), 0)

    def test_for_tenant_supports_queryset_chaining(self):
        Company.objects.create(
            tenant=self.tenant_a,
            name="Inactive Company",
            code="A3",
            is_active=False,
        )

        companies = (
            Company.objects
            .for_tenant(self.tenant_a)
            .filter(is_active=True)
            .order_by("name")
        )

        self.assertEqual(companies.count(), 2)

        self.assertQuerySetEqual(
            companies,
            ["Company A1", "Company A2"],
            transform=lambda company: company.name,
        )

    def test_for_tenant_with_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            Company.objects.for_tenant("invalid-tenant")