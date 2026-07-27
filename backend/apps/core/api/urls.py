from django.urls import path

from .views import HealthCheckView, VersionView

app_name = "core"

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("version/", VersionView.as_view(), name="version"),
]