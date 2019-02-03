"""
created at: 2018-05-16
author:     Volodymyr Biryuk

Authorization and Authentication module.
"""
from functools import wraps
from flask import request, Response
import json

api_key = None


def init_auth(secret_key: str):
    global api_key
    api_key = secret_key


def bearer_token_auth(bearer_token):
    """
    Check the validity of the bearer token.
    :param bearer_token: The bearer token from the authentication header.
    :return:
    """
    result = False
    try:
        split = bearer_token.split(' ')
        bearer = split[0]
        token = split[1]
        if bearer == 'Bearer' and token == api_key:
            result = True
    except AttributeError:
        pass
    finally:
        return result


def authenticate():
    """
    Sends a 401 response that hints the usage of bearer auth.
    :return: Respond with status 401.
    """
    return Response(
        response=json.dumps({'message': 'Authorization error.'}),
        status=401,
        headers={'WWW-Authenticate': 'Bearer'}, content_type='application/json'
    )


def requires_multiple(arg):
    """
    Decorator function that takes arguments and calls the decorator that decorates the actual function.
    The function that requires authentication for certain HTTP methods should have the @requires_auth(arg) annotation.
    :param arg: List of HTTP methods that require auth.
    :return: The decorator function.
    """

    def decorator(func):
        """
        Decorator function that takes the decorated function as parameter.
        :param func:
        :return:
        """

        @wraps(func)
        def decorated(*args, **kwargs):
            """
            The authentication happens here.
            :param args: Positional arguments.
            :param kwargs: Keyword arguments.
            :return: The actual decorated function (that has the @ annotation above it.)
            """
            method = request.method
            # Authorize only the HTTP methods that were passed to the decorator.
            if method in arg:
                bearer_token = request.headers.get('Authorization')
                if not bearer_token or not bearer_token_auth(bearer_token):
                    return authenticate()
            return func(*args, **kwargs)

        return decorated

    return decorator


def auth_single(f):
    """
    Decorator function that to enable auth for API functions.
    :param f: Must be empty in annotation.
    :return: The auth result.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        bearer_token = request.headers.get('Authorization')
        if not bearer_token or not bearer_token_auth(bearer_token):
            return authenticate()
        return f(*args, **kwargs)

    return decorated
