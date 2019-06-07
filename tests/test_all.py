"""
created at: 2019-02-01
author: Volodymyr Biryuk

<module comment>
"""
import os
import sys
import unittest
import tempfile

import requests

import microservice
from microservice import auth, util
from dateutil import parser as datutil_parser
import datetime


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


class UtilTest(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def test_serialize_datetime(self):
        now = datetime.datetime.now()
        serialized = util.serialize(now)
        self.assertEqual(now.__str__(), serialized)

    def test_read_write(self):
        # Create temporary diractory write and read files from it and delet it.
        with tempfile.TemporaryDirectory() as tmpdirname:
            full_path = os.path.join(tmpdirname, 'test_file')
            util.write_file(full_path, 'Hello World!')
            file_on_disk = util.read_file(full_path)
            self.assertEqual('Hello World!', file_on_disk)
            self.assertNotEqual('Hallo Welt!', file_on_disk)
            # Test the exception
            try:
                file_on_disk = util.read_file('')
                self.fail('The exception failed to raise.')
            except FileNotFoundError:
                pass
            # Test exception for empty path.
            try:
                util.write_file('', 'Hello World!')
                self.fail('No exception or wrong exception was raised.')
            except FileNotFoundError:
                pass
            # Test exception for missing path.
            try:
                util.write_file(None, 'Hello World!')
                self.fail('No exception or wrong exception was raised.')
            except TypeError:
                pass
            # Test the exception for missing file
            try:
                full_path = os.path.join(tmpdirname, 'test_file')
                util.write_file(full_path, None)
                self.fail('No exception or wrong exception was raised.')
            except TypeError:
                pass

    def test_unzip(self):
        # Create temporary directory zip and unzip files from it and delete it.
        with tempfile.TemporaryDirectory() as tmpdirname:
            full_path = os.path.join(tmpdirname, 'test_file.zip')
            util.write_file(full_path, 'Hello World!')
            try:
                util.unzip(full_path)
                self.fail('No exception or wrong exception was raised.')
            except OSError:
                pass


if __name__ == '__main__':
    unittest.main()
