"""
created at: 2019-02-01
author: Volodymyr Biryuk

<module comment>
"""
import os
import re
import unittest

import requests

import microservice
from microservice import auth
from dateutil import parser as datutil_parser


class AuthTest(unittest.TestCase):

    def test_bearer_auth_user(self):
        # Auth service not initialized. Test for None token.
        role = None
        admin_token = None
        user_token = None
        given_token = None
        auth.init_auth(user_token, admin_token)
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test empty token
        role = ''
        user_token = ''
        given_token = ''
        auth.init_auth(user_token, admin_token)
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test token without 'Bearer' keyword
        role = 'user'
        user_token = '12345'
        given_token = '12345'
        auth.init_auth(user_token, admin_token)
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test for invalid token
        role = 'user'
        user_token = '12346'
        given_token = 'Bearer 12345'
        auth.init_auth(user_token, admin_token)
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test for valid token
        role = 'user'
        user_token = '12345'
        given_token = 'Bearer 12345'
        auth.init_auth(user_token, admin_token)
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertTrue(auth_result)

    def test_bearer_auth_admin(self):
        # Auth service not initialized. Test for None token.
        role = None
        admin_token = None
        user_token = None
        given_token = None
        auth.init_auth(user_token, admin_token)
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test empty token
        role = ''
        user_token = ''
        given_token = ''
        auth.init_auth(user_token, admin_token)
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test token without 'Bearer' keyword
        role = 'admin'
        user_token = '12345'
        given_token = '12345'
        auth.init_auth(user_token, admin_token)
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test for invalid token
        role = 'admin'
        user_token = '12346'
        given_token = 'Bearer 12345'
        auth.init_auth(user_token, admin_token)
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test for valid token
        role = 'admin'
        user_token = '12345'
        given_token = 'Bearer 12345'
        auth.init_auth(user_token, admin_token)
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertTrue(auth_result)


class FrontendAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            os.remove('config_test.json')
        except FileNotFoundError:
            pass
        os.environ['DB_HOST'] = '0.0.0.0'
        os.environ['DB_PORT'] = '27017'
        os.environ['DB_AUTH_MECHANISM'] = ''
        os.environ['DB_AUTH_SOURCE'] = ''
        os.environ['DB_NAME_FRONTEND_LOGS'] = ''
        os.environ['DB_USER'] = ''
        os.environ['DB_PASSWORD'] = ''
        os.environ['DB_CONNECTION_TIMEOUT'] = '5000'
        os.environ['API_URL'] = 'http://localhost:9798/frontend/log'
        os.environ['API_BEARER_TOKEN'] = '12345'
        os.environ['DIR_DEBUG_LOG'] = ''
        os.environ['DIR_BACKEND_LOG'] = ''
        os.environ['DEBUG'] = 'True'
        os.environ['LOGGING_LEVEL'] = 'INFO'
        cls.url_base = '/frontend'
        cls.app = microservice.create_app('config_test.json')

    def test_frontend_script(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/script')
            self.assertEqual(200, response.status_code)

    def test_frontend_log_get(self):
        # Test with auth
        bearer_token = ''
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/log')
            self.assertEqual(response.status_code, 401)
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {bearer_token}'})
            self.assertEqual(response.status_code, 401)
            bearer_token = '7kyT5sGL8d5ax6qHJU32L4CJ'
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {bearer_token}'})
            self.assertEqual(response.status_code, 401)
            bearer_token = '12345'
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {bearer_token}'})
            self.assertEqual(response.status_code, 200)

    def test_frontend_log_post(self):
        with self.app.test_client() as c:
            response = c.post(f'{self.url_base}/log', )
            self.assertEqual(response.status_code, 400)


class BackendAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            os.remove('config_test.json')
        except FileNotFoundError:
            pass
        os.environ['DB_HOST'] = '0.0.0.0'
        os.environ['DB_PORT'] = '27017'
        os.environ['DB_AUTH_MECHANISM'] = ''
        os.environ['DB_AUTH_SOURCE'] = ''
        os.environ['DB_NAME_FRONTEND_LOGS'] = ''
        os.environ['DB_USER'] = ''
        os.environ['DB_PASSWORD'] = ''
        os.environ['DB_CONNECTION_TIMEOUT'] = '5000'
        os.environ['API_URL'] = 'http://localhost:9798/frontend/log'
        os.environ['API_BEARER_TOKEN'] = '12345'
        os.environ['DIR_DEBUG_LOG'] = ''
        os.environ['DIR_BACKEND_LOG'] = ''
        os.environ['DEBUG'] = 'True'
        os.environ['LOGGING_LEVEL'] = 'INFO'
        cls.url_base = '/backend'
        cls.app = microservice.create_app('config.json')

    def test_backend_logging_get(self):
        # Test with auth
        bearer_token = ''
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/log')
            self.assertEqual(response.status_code, 401)
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {bearer_token}'})
            self.assertEqual(response.status_code, 401)
            bearer_token = '7kyT5sGL8d5ax6qHJU32L4CJ'
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {bearer_token}'})
            self.assertEqual(response.status_code, 401)
            bearer_token = '12345'
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {bearer_token}'})
            self.assertEqual(response.status_code, 200)
            response = c.get(f'{self.url_base}/log/error.log.6.gz', headers={'Authorization': f'Bearer {bearer_token}'})
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
