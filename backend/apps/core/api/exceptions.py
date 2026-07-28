from rest_framework.views import exception_handler

from .responses import error_response


def custom_exception_handler(exc, context):
    """
    Global exception handler.
    """

    response = exception_handler(exc, context)

    if response is None:
        return error_response(
            message="Internal server error.",
            status_code=500,
        )

    return error_response(
        message="Request failed.",
        errors=response.data,
        status_code=response.status_code,
    )