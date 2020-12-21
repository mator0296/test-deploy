from functools import wraps
from typing import Callable

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from graphene_django.settings import graphene_settings
from graphql_jwt.middleware import JSONWebTokenMiddleware, _authenticate


def api_only_request_handler(get_response: Callable, handler: Callable):
    @wraps(handler)
    def handle_request(request):
        api_path = reverse("api")
        if request.path != api_path:
            return get_response(request)
        return handler(request)

    return handle_request


def api_only_middleware(middleware):
    @wraps(middleware)
    def wrapped(get_response):
        handler = middleware(get_response)
        return api_only_request_handler(get_response, handler)

    return wrapped


@api_only_middleware
def jwt_middleware(get_response):
    """Authenticate user using JSONWebTokenMiddleware.

    This middleware authenticates the user with
    graphql_jwt.middleware.JSONWebTokenMiddleware
    if the user is not already authenticated.
    """
    # Disable warnings for django-graphene-jwt
    graphene_settings.MIDDLEWARE.append(JSONWebTokenMiddleware)
    # jwt_middleware_inst = JSONWebTokenMiddleware()
    graphene_settings.MIDDLEWARE.remove(JSONWebTokenMiddleware)

    def middleware(request):
        if not hasattr(request, "user"):
            request._cached_user = AnonymousUser()
            request.user = AnonymousUser()
        # Authenticate using JWT middleware
        # process_request checks if the user is already authenticated
        # jwt_middleware_inst.resolve(request, None, None)
        _authenticate(request)
        return get_response(request)

    return middleware
