from django.urls import path

from .views import (
    CompanyDetailView,
    CompanyListView,
    TenantContextView,
)

urlpatterns = [
    path(
        "context/",
        TenantContextView.as_view(),
        name="tenant-context",
    ),
    path(
        "companies/",
        CompanyListView.as_view(),
        name="company-list",
    ),
    path(
        "companies/<uuid:pk>/",
        CompanyDetailView.as_view(),
        name="company-detail",
    ),
]
