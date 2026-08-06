from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Core APIs
    path("api/", include("apps.core.api.urls")),

    # Authentication APIs
    path("api/auth/", include("apps.users.api.urls")),

    # Tenant APIs
    path("api/tenant/", include("apps.tenants.api.urls")),
]