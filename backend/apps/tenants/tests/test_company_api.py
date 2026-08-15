from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.tenants.models import Company, Membership, Tenant
from apps.users.models import User


class CompanyListAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="company-user",
            password="TestPassword123!",
        )

        self.tenant_a = Tenant.objects.create(
            name="Tenant A",
            slug="tenant-a",
        )

        self.tenant_b = Tenant.objects.create(
            name="Tenant B",
            slug="tenant-b",
        )

        Membership.objects.create(
            user=self.user,
            tenant=self.tenant_a,
        )

        self.company_a1 = Company.objects.create(
            tenant=self.tenant_a,
            name="Company A1",
            code="A001",
        )

        self.company_a2 = Company.objects.create(
            tenant=self.tenant_a,
            name="Company A2",
            code="A002",
        )

        self.company_b1 = Company.objects.create(
            tenant=self.tenant_b,
            name="Company B1",
            code="B001",
        )

        self.url = reverse("company-list")

    def authenticate(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "company-user",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

    def test_authenticated_user_only_sees_companies_of_current_tenant(self):
        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(response.data["success"])

        companies = response.data["data"]

        company_ids = {
            item["id"]
            for item in companies
        }

        self.assertEqual(
            company_ids,
            {
                str(self.company_a1.id),
                str(self.company_a2.id),
            },
        )

        self.assertNotIn(
            str(self.company_b1.id),
            company_ids,
        )

    def test_authenticated_user_cannot_access_company_from_another_tenant(self):
        self.authenticate()

        url = reverse(
            "company-detail",
            kwargs={"pk": self.company_b1.id},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_authenticated_user_creates_company_in_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "name": "Company A3",
                "code": "A003",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        company = Company.objects.get(
            code="A003",
        )

        self.assertEqual(
            company.tenant,
            self.tenant_a,
        )

        self.assertEqual(
            response.data["data"]["id"],
            str(company.id),
        )

    def test_client_cannot_override_company_tenant(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "name": "Malicious Company",
                "code": "EVIL",
                "tenant": str(self.tenant_b.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        company = Company.objects.get(
            code="EVIL",
        )

        self.assertEqual(
            company.tenant,
            self.tenant_a,
        )

        self.assertNotEqual(
            company.tenant,
            self.tenant_b,
        )

    def test_authenticated_user_can_update_company_in_current_tenant(self):
        self.authenticate()

        url = reverse(
            "company-detail",
            kwargs={"pk": self.company_a1.id},
        )

        response = self.client.patch(
            url,
            {
                "name": "Updated Company A1",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.company_a1.refresh_from_db()

        self.assertEqual(
            self.company_a1.name,
            "Updated Company A1",
        )

        self.assertEqual(
            self.company_a1.tenant,
            self.tenant_a,
        )

    def test_authenticated_user_cannot_update_company_from_another_tenant(self):
        self.authenticate()

        url = reverse(
            "company-detail",
            kwargs={"pk": self.company_b1.id},
        )

        response = self.client.patch(
            url,
            {
                "name": "Hacked Company",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.company_b1.refresh_from_db()

        self.assertEqual(
            self.company_b1.name,
            "Company B1",
        )

        self.assertEqual(
            self.company_b1.tenant,
            self.tenant_b,
        )

    def test_authenticated_user_cannot_delete_company_from_another_tenant(self):
        self.authenticate()

        url = reverse(
            "company-detail",
            kwargs={"pk": self.company_b1.id},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Company.objects.filter(
                pk=self.company_b1.id,
                tenant=self.tenant_b,
            ).exists()
        )

    def test_authenticated_user_can_delete_company_in_current_tenant(self):
        self.authenticate()

        url = reverse(
            "company-detail",
            kwargs={"pk": self.company_a1.id},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            Company.objects.filter(
                pk=self.company_a1.id,
                tenant=self.tenant_a,
            ).exists()
        )

    