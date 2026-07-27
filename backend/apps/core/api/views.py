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
                "service": "saas-erp",
                "version": "0.1.0",
            }
        )