"""
created at: 2019-02-01
author: Volodymyr Biryuk

<module comment>
"""
import datetime
import os
import tempfile
import unittest

from dateutil.tz import tzutc

import microservice
from microservice import auth, util, backend_logging


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


class APITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_bearer_token = '12345'
        cls.admin_bearer_token = '54321'
        try:
            os.remove('config.json')
        except FileNotFoundError:
            pass
        os.environ['MS_HOST'] = '0.0.0.0'
        os.environ['MS_PORT'] = '9798'
        os.environ['DB_HOST'] = '0.0.0.0'
        os.environ['DB_PORT'] = '27017'
        os.environ['DB_AUTH_MECHANISM'] = ''
        os.environ['DB_AUTH_SOURCE'] = ''
        os.environ['DB_NAME_FRONTEND_LOGS'] = 'riLoggingTest'
        os.environ['DB_USER'] = ''
        os.environ['DB_PASSWORD'] = ''
        os.environ['DB_CONNECTION_TIMEOUT'] = '3000'

        os.environ['API_URL'] = '0.0.0.0:9798/frontend/log'
        os.environ['USER_BEARER_TOKEN'] = cls.user_bearer_token
        os.environ['ADMIN_BEARER_TOKEN'] = cls.admin_bearer_token
        os.environ['DIR_DEBUG_LOG'] = '~/Desktop'
        os.environ['DIR_BACKEND_LOG'] = '~/Desktop'
        os.environ['BACKEND_LOG_SCHEDULE'] = '18:00'

        os.environ['DEBUG'] = 'True'
        os.environ['LOGGING_LEVEL'] = 'DEBUG'
        cls.app = microservice.create_app('config_test.json')


class FrontendAPITest(APITest):
    def setUp(self):
        self.url_base = '/frontend'

    def test_frontend_script(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/script')
            self.assertEqual(200, response.status_code)

    def test_frontend_log_get(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/log')
            self.assertEqual(response.status_code, 401)
            given_token = 'invalid token'
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {given_token}'})
            self.assertEqual(response.status_code, 401)
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(response.status_code, 500)

    def test_frontend_log_change_get(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/log/change')
            self.assertEqual(response.status_code, 401)
            given_token = 'invalid token'
            response = c.get(f'{self.url_base}/log/change', headers={'Authorization': f'Bearer {given_token}'})
            self.assertEqual(response.status_code, 401)
            response = c.get(f'{self.url_base}/log/change',
                             headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(response.status_code, 500)

    def test_frontend_change_get(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/change')
            self.assertEqual(response.status_code, 401)
            given_token = 'invalid token'
            response = c.get(f'{self.url_base}/change', headers={'Authorization': f'Bearer {given_token}'})
            self.assertEqual(response.status_code, 401)
            response = c.get(f'{self.url_base}/change', headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(response.status_code, 500)

    def test_frontend_log_porject_get(self):
        with self.app.test_client() as c:
            project_id = 'test'
            response = c.get(f'{self.url_base}/log/{project_id}')
            self.assertEqual(response.status_code, 401)
            requirement_id = 'test'
            response = c.get(f'{self.url_base}/log/{project_id}/{requirement_id}')
            self.assertEqual(response.status_code, 401)
            given_token = 'invalid token'
            response = c.get(f'{self.url_base}/log/{project_id}', headers={'Authorization': f'Bearer {given_token}'})
            self.assertEqual(response.status_code, 401)
            response = c.get(f'{self.url_base}/log/{project_id}/{requirement_id}',
                             headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(response.status_code, 500)

    def test_frontend_log_post(self):
        with self.app.test_client() as c:
            response = c.post(f'{self.url_base}/log', )
            self.assertEqual(response.status_code, 400)


class BackendAPITest(APITest):
    def setUp(self):
        self.url_base = '/backend'

    def test_backend_logging_get(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/log')
            self.assertEqual(response.status_code, 401)


class UtilTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

    def test_serialize_datetime(self):
        now = datetime.datetime.now()
        serialized = util.serialize(now)
        self.assertEqual(now.__str__(), serialized)

    def test_read_write(self):
        # Create temporary diractory write and read files from it and delet it.
        with self.test_dir:
            full_path = os.path.join(self.test_dir.name, 'test_file')
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
                full_path = os.path.join(self.test_dir.name, 'test_file')
                util.write_file(full_path, None)
                self.fail('No exception or wrong exception was raised.')
            except TypeError:
                pass

    def test_unzip(self):
        # Create temporary directory zip and unzip files from it and delete it.
        with self.test_dir:
            full_path = os.path.join(self.test_dir.name, 'test_file.zip')
            util.write_file(full_path, 'Hello World!')
            try:
                util.unzip(full_path)
                self.fail('No exception or wrong exception was raised.')
            except OSError:
                pass


class AdminAPITest(APITest):
    def setUp(self):
        self.url_base = '/admin'

    def test_export_collections(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/test/export')
            self.assertEqual(response.status_code, 401)


class NginxLogConverterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nlc = backend_logging.NginxLogConverter()

    def test_convert_local_time_to_iso_date(self):
        time_local_string = '11/Jun/2019:08:41:02 +0000'
        iso_date_expected = datetime.datetime(2019, 6, 11, 8, 41, 2, tzinfo=tzutc())
        iso_date_given = self.nlc._time_local_to_iso_date(time_local_string)
        self.assertEqual(iso_date_expected, iso_date_given)

    def test_split_request(self):
        request_string = 'GET /requirements-classifier/ HTTP/2.0'
        split_request_expected = {'httpMethod': 'GET', 'path': '/requirements-classifier/', 'protocol': 'HTTP/2.0'}
        split_request_given = self.nlc._split_request(request_string)
        self.assertEqual(split_request_expected, split_request_given)

        request_string = 'GET /eclipse/plugins/io.projectreactor.netty.reactor-netty_0.8.6.RELEASE.jar HTTP/1.1'
        split_request_expected = {'httpMethod': 'GET',
                                  'path': '/eclipse/plugins/io.projectreactor.netty.reactor-netty_0.8.6.RELEASE.jar',
                                  'protocol': 'HTTP/1.1'}
        split_request_given = self.nlc._split_request(request_string)
        self.assertEqual(split_request_expected, split_request_given)

        request_string = 'HEAD /eclipse/artifacts.xml.xz HTTP/1.1'
        split_request_expected = {'httpMethod': 'HEAD', 'path': '/eclipse/artifacts.xml.xz', 'protocol': 'HTTP/1.1'}
        split_request_given = self.nlc._split_request(request_string)
        self.assertEqual(split_request_expected, split_request_given)

        request_string = 'GET /registry/robots.txt HTTP/1.0'
        split_request_expected = {'httpMethod': 'GET', 'path': '/registry/robots.txt', 'protocol': 'HTTP/1.0'}
        split_request_given = self.nlc._split_request(request_string)
        self.assertEqual(split_request_expected, split_request_given)

        request_string = 'GET / HTTP/1.0'
        split_request_expected = {'httpMethod': 'GET', 'path': '/', 'protocol': 'HTTP/1.0'}
        split_request_given = self.nlc._split_request(request_string)
        self.assertEqual(split_request_expected, split_request_given)

    def test_log_entry_to_log_object(self):
        log_entry = '217.172.12.199 - 3346c17ac8a179541c7c13654202816866d44377 [11/Jun/2019:05:28:00 +0000] "GET /sonarqube/api/rules/search.protobuf?f=repo,name,severity,lang,internalKey,templateKey,params,actives,createdAt,updatedAt&activation=true&qprofile=AWjcRabH3KB239lnMkuI&p=1&ps=500 HTTP/1.1" 0.015 0.015 200 7603 "-" "ScannerCli/3.3.0.1492" "-"'
        expected_log_object = {
            'remote_address': '217.172.12.199',
            'remote_user': '3346c17ac8a179541c7c13654202816866d44377',
            'time_local': '11/Jun/2019:05:28:00 +0000',
            'request': 'GET /sonarqube/api/rules/search.protobuf?f=repo,name,severity,lang,internalKey,templateKey,params,actives,createdAt,updatedAt&activation=true&qprofile=AWjcRabH3KB239lnMkuI&p=1&ps=500 HTTP/1.1',
            'request_time': '0.015',
            'upstream_response_time': '0.015',
            'status': '200',
            'body_bytes_sent': '7603',
            'http_referer': '-',
            'http_user_agent': 'ScannerCli/3.3.0.1492',
            'gzip_ratio': '-',
        }
        given_log_object = self.nlc._log_entry_to_log_object(log_entry)
        self.assertEqual(expected_log_object, given_log_object)

    def test_log_object_to_document(self):
        log_object = {
            'remote_address': '217.172.12.199',
            'remote_user': '3346c17ac8a179541c7c13654202816866d44377',
            'time_local': '11/Jun/2019:08:49:39 +0000',
            'request': 'POST /analytics-backend/tweetClassification HTTP/1.1',
            'request_time': '0.578',
            'upstream_response_time': '0.578',
            'status': '200',
            'body_bytes_sent': '110',
            'http_referer': '-',
            'http_user_agent': 'Go-http-client/1.1',
            'gzip_ratio': '-',
        }
        expected_document = {
            'remoteAddress': '217.172.12.199',
            'remoteUser': '3346c17ac8a179541c7c13654202816866d44377',
            'timeLocal': datetime.datetime(2019, 6, 11, 8, 49, 39, tzinfo=tzutc()),
            'request': 'POST /analytics-backend/tweetClassification HTTP/1.1',
            'requestTime': 0.578,
            'upstreamResponseTime': 0.578,
            'status': '200',
            'bodyBytesSent': 110,
            'httpReferer': '-',
            'httpUserAgent': 'Go-http-client/1.1',
            'gzipRatio': '-'
        }
        given_document = self.nlc._log_object_to_document(log_object)
        self.assertNotEqual(expected_document, given_document)
        expected_document['httpMethod'] = 'POST'
        expected_document['path'] = '/analytics-backend/tweetClassification'
        expected_document['protocol'] = 'HTTP/1.1'
        self.assertEqual(expected_document, given_document)

    def test_logfile_to_documents(self):
        remote_addr = '123.123.12.123'
        remote_user = 'LTkfA46WENjRSDLxggXyZsVbMpWtSrLcKdHCz6L5'
        local_time = '[11/Jun/2019:05:27:58 +0000]'
        request = '"GET /this/is/some/path HTTP/1.0"'
        request_time = '0.020'
        response_time = '0.020'
        status = '200'
        body_bytes_sent = '452'
        user_agent = '"This is a user agent"'
        # Valid log file should be converted
        log_file = f'{remote_addr} - {remote_user} {local_time} {request} {request_time} {response_time} {status} ' \
            f'{body_bytes_sent} "-" {user_agent} "-"'
        log_documents = self.nlc.logfile_to_documents(log_file)
        self.assertEqual(1, len(log_documents))
        log_file += '\n'
        # Another valid log file should be converted
        log_file += '217.172.12.199 - - [11/Jun/2019:05:56:37 +0000] ' \
                    '"GET /ri-collection-explicit-feedback-twitter/mention/WindItalia/lang/it/fast HTTP/1.1" ' \
                    '0.514 - 200 42098 "-" "Go-http-client/1.1" "-"'
        log_documents = self.nlc.logfile_to_documents(log_file)
        self.assertEqual(2, len(log_documents))
        log_file += '\n'
        # Bad log file should not be converted
        log_file += '217.172.12.199 - - [something is wrong] ' \
                    '"GET /ri-collection-explicit-feedback-twitter/mention/WindItalia/lang/it/fast HTTP/1.1" ' \
                    '0.514 - 200 42098 "-" "Go-http-client/1.1" "-"'
        log_documents = self.nlc.logfile_to_documents(log_file)
        self.assertEqual(2, len(log_documents))


if __name__ == '__main__':
    unittest.main()
