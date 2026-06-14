import functools

from authn.helpers import check_user_permissions


def require_auth(view):
    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        access_denied = check_user_permissions(request)
        if access_denied:
            return access_denied

        return view(request, *args, **kwargs)

    return wrapper
