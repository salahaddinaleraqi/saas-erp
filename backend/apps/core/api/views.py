from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    Health check endpoint.
    """

    def get(self, request):
        return Response(
            {
                "status": "healthy",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
            }
        )


class VersionView(APIView):
    """
    Application version endpoint.
    """

    def get(self, request):
        return Response(
            {
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
            }
        )