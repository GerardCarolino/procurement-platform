from django.core.exceptions import PermissionDenied


def require_agency_admin(user):
    if not user.is_authenticated or not user.is_agency_admin:
        raise PermissionDenied
    return True


def require_verified_vendor(user):
    if not user.is_authenticated or not user.is_verified_vendor:
        raise PermissionDenied
    return True


def require_authenticated(user):
    if not user.is_authenticated:
        raise PermissionDenied
    return True