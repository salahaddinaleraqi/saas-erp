import uuid

from django.db import models


class Tenant(models.Model):
    """
    Represents a tenant (subscription/workspace) in the SaaS ERP system.
    A tenant can own one or more companies.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self):
        return self.name


class Company(models.Model):
    """
    Represents a legal company owned by a tenant.
    A tenant can have one or more companies.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="companies",
    )

    name = models.CharField(
        max_length=255,
    )

    code = models.CharField(
        max_length=50,
        db_index=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "code"],
                name="unique_company_code_per_tenant",
            ),
        ]

    def __str__(self):
        return self.name