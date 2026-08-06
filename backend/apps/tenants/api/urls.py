from django.urls import path

from .views import TenantContextView

urlpatterns = [
    path("context/", TenantContextView.as_view(), name="tenant-context"),
]