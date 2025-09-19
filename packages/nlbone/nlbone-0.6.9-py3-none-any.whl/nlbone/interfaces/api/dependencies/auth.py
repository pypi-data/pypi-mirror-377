import functools

from nlbone.adapters.auth import KeycloakAuthService
from nlbone.interfaces.api.exceptions import ForbiddenException, UnauthorizedException
from nlbone.utils.context import current_request


def current_user_id() -> int:
    user_id = current_request().state.user_id
    if user_id is not None:
        return int(user_id)
    raise UnauthorizedException()


def current_client_id() -> str:
    request = current_request()
    if client_id := KeycloakAuthService().get_client_id(request.state.token):
        return str(client_id)
    raise UnauthorizedException()


def client_has_access(*, permissions=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request = current_request()
            if not KeycloakAuthService().client_has_access(request.state.token, permissions=permissions):
                raise ForbiddenException(f"Forbidden {permissions}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def user_authenticated(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user_id():
            raise UnauthorizedException()
        return func(*args, **kwargs)

    return wrapper


def has_access(*, permissions=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request = current_request()
            if not current_user_id():
                raise UnauthorizedException()
            if not KeycloakAuthService().has_access(request.state.token, permissions=permissions):
                raise ForbiddenException(f"Forbidden {permissions}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def client_or_user_has_access(*, permissions=None, client_permissions=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request = current_request()
            token = getattr(request.state, "token", None)
            if not token:
                raise UnauthorizedException()

            auth = KeycloakAuthService()

            if auth.get_client_id(token):
                needed = client_permissions or permissions
                if not auth.client_has_access(token, permissions=needed):
                    raise ForbiddenException(f"Forbidden (client) {needed}")
            else:
                if not current_user_id():
                    raise UnauthorizedException()
                if not auth.has_access(token, permissions=permissions):
                    raise ForbiddenException(f"Forbidden (user) {permissions}")

            return func(*args, **kwargs)
        return wrapper
    return decorator