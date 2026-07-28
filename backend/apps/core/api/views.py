from django.conf import settings
from rest_framework.views import APIView

from .responses import success_response

class HealthCheckView(APIView):
    """
    Health check endpoint.
    """

    def get(self, request):
        return success_response(
            data={
                "status": "healthy",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
            },
            message="Service is healthy",
        )


class VersionView(APIView):
    """
    Application version endpoint.
    """

    def get(self, request):
        return success_response(
            data={
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            },
            message="Version retrieved successfully",
        )