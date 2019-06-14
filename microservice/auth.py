"""
created at: 2018-05-16
author:     Volodymyr Biryuk

Authorization and Authentication module.
"""
import json
from functools import wraps

from flask import request, Response

auth_store = {
    'user': None,
    'admin': None
}


def init_auth(user_key: str, admin_key: str):
    global auth_store
    auth_store['user'] = user_key
    auth_store['admin'] = admin_key


def bearer_token_auth(role: str, bearer_token: str):
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
        if bearer == 'Bearer':
            result = token == auth_store[role]
    except (AttributeError, KeyError):
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

def auth_single(f):
    """
    Decorator function that to enable auth for API functions.
    :param f: Must be empty in annotation.
    :return: The auth result.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        bearer_token = request.headers.get('Authorization')
        if not bearer_token or not bearer_token_auth('user', bearer_token):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def auth_admin(f):
    """
    Decorator function that to enable auth for API functions.
    :param f: Must be empty in annotation.
    :return: The auth result.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        bearer_token = request.headers.get('Authorization')
        if not bearer_token or not bearer_token_auth('admin', bearer_token):
            return authenticate()
        return f(*args, **kwargs)

    return decorated
