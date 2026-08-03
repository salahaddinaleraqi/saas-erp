from django.urls import path

from .views import ApiRootView, HealthCheckView, VersionView

urlpatterns = [
    path("", ApiRootView.as_view(), name="api-root"),
    path("health/", HealthCheckView.as_view(), name="health"),
    path("version/", VersionView.as_view(), name="version"),
]