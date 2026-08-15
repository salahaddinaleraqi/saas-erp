from django.db import models


class TenantAwareQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        if tenant is None:
            return self.none()

        from apps.tenants.models import Tenant

        if not isinstance(tenant, Tenant):
            raise TypeError(
                "tenant must be a Tenant instance or None."
            )

        return self.filter(tenant=tenant)


class TenantAwareManager(models.Manager):
    def get_queryset(self):
        return TenantAwareQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant):
        return self.get_queryset().for_tenant(tenant)
