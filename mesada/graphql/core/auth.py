from functools import wraps

import django_cache_url

# import redis
from graphql_jwt import exceptions
from graphql_jwt.decorators import context

_cache_url = django_cache_url.config().get("LOCATION")


# _blacklist_storage = redis.StrictRedis(decode_responses=True).from_url(_cache_url)


BANNED_TOKENS_COLLECTION = "banned_tokens_collection"


def _user_passes_test(test_func):
    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):
            if test_func(context):
                return f(*args, **kwargs)
            raise exceptions.PermissionDenied()

        return wrapper

    return decorator


# def _blacklisted_token(token):
#     return _blacklist_storage.sismember(BANNED_TOKENS_COLLECTION, token)


def _login_test(context):
    is_authenticated = context.user.is_authenticated
    token = context.headers.get("Authorization", None)
    if not token:
        return is_authenticated
    return is_authenticated  # and not _blacklisted_token(token)


"""
This decorator improves the functionality of login_required
>>> from graphql_jwt.decorators import login_required
and adds blacklist check for Sign Out support
"""
login_required = _user_passes_test(_login_test)


# def add_token_to_blacklist(token):
#     _blacklist_storage.sadd(BANNED_TOKENS_COLLECTION, token)
