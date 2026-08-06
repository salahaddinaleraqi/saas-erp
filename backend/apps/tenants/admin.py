from django.contrib import admin

from .models import Company, Membership, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tenant", "is_active")
    search_fields = ("name", "code")
    list_filter = ("tenant", "is_active")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "tenant", "is_active", "joined_at")
    search_fields = ("user__username", "user__email", "tenant__name")
    list_filter = ("tenant", "is_active")