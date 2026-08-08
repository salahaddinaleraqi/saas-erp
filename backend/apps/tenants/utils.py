from django.http import HttpRequest


def get_current_tenant(request: HttpRequest):
    """
    Returns the tenant resolved for the current request.

    The tenant must be resolved by TenantContext before
    calling this utility.
    """
    return getattr(request, "tenant", None)


def get_current_membership(request: HttpRequest):
    """
    Returns the membership resolved for the current request.

    The membership must be resolved by TenantContext before
    calling this utility.
    """
    return getattr(request, "membership", None)