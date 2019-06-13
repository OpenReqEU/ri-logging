"""
created at: 2019-02-01
author: Volodymyr Biryuk

<module comment>
"""
import datetime
import json
import os
import tempfile
import unittest

from dateutil.tz import tzutc

import microservice
from microservice import auth, util, backend_logging, data_access


class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir_debug_log = tempfile.mkdtemp()
        cls.dir_backend_log = tempfile.mkdtemp()
        cls.user_bearer_token = '12345'
        cls.admin_bearer_token = '54321'
        try:
            os.remove(os.path.join(os.path.dirname(__file__), '..', 'config_test.json'))
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
        os.environ['DB_CONNECTION_TIMEOUT'] = '500'

        os.environ['API_URL'] = '0.0.0.0:9798/frontend/log'
        os.environ['USER_BEARER_TOKEN'] = cls.user_bearer_token
        os.environ['ADMIN_BEARER_TOKEN'] = cls.admin_bearer_token
        os.environ['DIR_DEBUG_LOG'] = cls.dir_debug_log
        os.environ['DIR_BACKEND_LOG'] = cls.dir_backend_log
        os.environ['BACKEND_LOG_SCHEDULE'] = '18:00'

        os.environ['DEBUG'] = 'True'
        os.environ['LOGGING_LEVEL'] = 'DEBUG'
        cls.app = microservice.create_app('config_test.json')

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(os.path.join(os.path.dirname(__file__), '..', 'config_test.json'))
        except FileNotFoundError:
            pass


class DataAccessTest(BaseTest):
    def test_connection(self):
        client = data_access.MongoDBConnection('0.0.0.0', 27017)


class AuthTest(BaseTest):
    def test_bearer_auth_user(self):
        # Auth service not initialized. Test for None token.
        role = None
        given_token = None
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test empty token
        role = ''
        given_token = ''
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test token without 'Bearer' keyword
        role = 'user'
        given_token = '12345'
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test for invalid token
        role = 'user'
        given_token = 'Bearer 12346'
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test for valid token
        role = 'user'
        given_token = 'Bearer 12345'
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertTrue(auth_result)

    def test_bearer_auth_admin(self):
        # Auth service not initialized. Test for None token.
        role = None
        given_token = None
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test empty token
        role = ''
        given_token = ''
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test token without 'Bearer' keyword
        role = 'admin'
        given_token = '12345'
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test for invalid token
        role = 'admin'
        given_token = 'Bearer 12345'
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertFalse(auth_result)
        # Test for valid token
        role = 'admin'
        given_token = 'Bearer 54321'
        auth_result = auth.bearer_token_auth(role, given_token)
        self.assertTrue(auth_result)


class FrontendAPITest(BaseTest):
    url_base = '/frontend'

    def test_frontend_script(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/script')
            self.assertEqual(200, response.status_code)

    def test_frontend_log_post(self):
        with self.app.test_client() as c:
            url = f'{self.url_base}/log'
            response = c.post(
                url,
                data=dict(type='click'),
                headers={
                    'Host': 'localhost:9798',
                    'Connection': 'close',
                    'Content-Length': '1200',
                    'User-Agent': 'insomnia/6.3.2',
                    'Content-Type': 'application/json',
                    'Sessionid': '1q2w3e4r5t6y', 'Accept': '*/*'
                },
                content_type='application/json',
                follow_redirects=True)
            self.assertEqual(200, response.status_code)
            response = c.post(
                url,
                data=dict(foo='bar'),
                headers={
                    'Host': 'localhost:9798',
                    'Connection': 'close',
                    'Content-Length': '1200',
                    'User-Agent': 'insomnia/6.3.2',
                    'Content-Type': 'application/json',
                    'Sessionid': '1q2w3e4r5t6y', 'Accept': '*/*'
                },
                content_type='application/json',
                follow_redirects=True)
            self.assertEqual(400, response.status_code)

    def test_frontend_log_get(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/log')
            self.assertEqual(401, response.status_code)
            given_token = 'invalid token'
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {given_token}'})
            self.assertEqual(401, response.status_code)
            # Test valid auth
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(200, response.status_code)
            # Test with params
            url = f'{self.url_base}/log?username=foo&from=20190112&to20190601&projectId=123&requirementId=312'
            response = c.get(url, headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(200, response.status_code)

    def test_frontend_log_change_get(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/log/change')
            self.assertEqual(401, response.status_code)
            given_token = 'invalid token'
            response = c.get(f'{self.url_base}/log/change', headers={'Authorization': f'Bearer {given_token}'})
            self.assertEqual(401, response.status_code)
            response = c.get(f'{self.url_base}/log/change',
                             headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(400, response.status_code)
            response = c.get(f'{self.url_base}/log/change/123?username=foo',
                             headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(200, response.status_code)
            url = f'{self.url_base}/log/change?usernam=foo&userId=555&from=20190112&to=20190601&projectId=123&requirementId=312'
            response = c.get(url, headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(200, response.status_code)

    def test_frontend_change_get(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/change')
            self.assertEqual(401, response.status_code)
            given_token = 'invalid token'
            response = c.get(f'{self.url_base}/change', headers={'Authorization': f'Bearer {given_token}'})
            self.assertEqual(401, response.status_code)
            response = c.get(f'{self.url_base}/change', headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(200, response.status_code)
            # Test with params
            response = c.get(f'{self.url_base}/change/123?username=foo', headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(200, response.status_code)

    def test_frontend_log_project_get(self):
        with self.app.test_client() as c:
            project_id = 'test'
            response = c.get(f'{self.url_base}/log/{project_id}')
            self.assertEqual(401, response.status_code)
            requirement_id = 'test'
            response = c.get(f'{self.url_base}/log/{project_id}/{requirement_id}')
            self.assertEqual(401, response.status_code)
            given_token = 'invalid token'
            response = c.get(f'{self.url_base}/log/{project_id}', headers={'Authorization': f'Bearer {given_token}'})
            self.assertEqual(401, response.status_code)
            response = c.get(f'{self.url_base}/log/{project_id}/{requirement_id}',
                             headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(200, response.status_code)

    def test_frontend_log_post(self):
        with self.app.test_client() as c:
            response = c.post(f'{self.url_base}/log', )
            self.assertEqual(400, response.status_code)


class BackendAPITest(BaseTest):
    url_base = '/backend'

    def test_backend_log_get(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/log')
            self.assertEqual(401, response.status_code)
            response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {self.user_bearer_token}'})
            self.assertEqual(200, response.status_code)
            response_data = json.loads(response.get_data())
            self.assertEqual(0, len(response_data['filenames']))
            with tempfile.NamedTemporaryFile(dir=self.dir_backend_log, suffix='.log'):
                response = c.get(f'{self.url_base}/log', headers={'Authorization': f'Bearer {self.user_bearer_token}'})
                response_data = json.loads(response.get_data())
                self.assertEqual(1, len(response_data['filenames']))

    def test_backend_logfile_get(self):
        with self.app.test_client() as c:
            logfile = tempfile.NamedTemporaryFile(dir=self.dir_backend_log, suffix='.log')
            with logfile:
                filename = logfile.name
                filename = filename.split('/')[-1]
                response = c.get(f'{self.url_base}/log/{filename}')
                self.assertEqual(401, response.status_code)
                response = c.get(f'{self.url_base}/log/{filename}',
                                 headers={'Authorization': f'Bearer {self.user_bearer_token}'})
                self.assertEqual(200, response.status_code)
                response_data = json.loads(response.get_data())
                self.assertIsNotNone(response_data)
                filename = 'valid_but_wrong_name.log'
                response = c.get(f'{self.url_base}/log/{filename}',
                                 headers={'Authorization': f'Bearer {self.user_bearer_token}'})
                self.assertEqual(404, response.status_code)

    def test_import_logfiles_into_db(self):
        logs0 = f'''123.123.12.123 - 11111aaaaa11111aaaaa11111aaaaa11111aaaaa [11/Jun/2019:05:28:00 +0000] "GET /this/is/a/path HTTP/1.1" 0.009 0.009 200 3470 "-" "ScannerCli/3.3.0.1492" "-"
123.123.12.123 - 11111aaaaa11111aaaaa11111aaaaa11111aaaaa [11/Jun/2019:05:28:07 +0000] "POST /this/is/a/path HTTP/1.1" 0.070 0.066 200 44 "-" "ScannerCli/3.3.0.1492" "-"
217.172.12.148 - - [11/Jun/2019:05:28:08 +0000] "GET /this/is/a/path/ HTTP/1.1" 0.004 0.004 200 11 "-" "Scanner for Jenkins" "-"
217.172.12.148 - 11111aaaaa11111aaaaa11111aaaaa11111aaaaa [11/Jun/2019:05:28:08 +0000] "GET /this/is/a/path HTTP/1.1" 0.008 0.008 200 347 "-" "Scanner for Jenkins" "-"
123.123.12.123 - - [11/Jun/2019:05:56:37 +0000] "GET /this/is/a/path HTTP/1.1" 0.292 0.292 200 5 "-" "Go-http-client/1.1" "-"
123.123.12.123 - - [11/Jun/2019:05:56:37 +0000] "POST / HTTP/1.1" 0.003 0.003 200 0 "-" "Go-http-client/1.1" "-"'''
        logs1 = f'''128.214.138.171 - - [11/Jun/2019:07:50:02 +0000] "GET /this/is/another/path HTTP/1.1" 222.042 189.637 302 255958653 "-" "Apache-HttpClient/4.5.3 (Java/11.0.3)" "-"
123.123.12.123 - - [11/Jun/2019:07:51:12 +0000] "HEAD /this/is/another/path HTTP/2.0" 0.000 - 200 0 "-" "Apache-HttpClient/4.5.6 (Java/1.8.0_201)" "-"
::1 - - [11/Jun/2019:07:52:23 +0000] "GET /this/is/another/path HTTP/1.0" 0.006 0.006 404 2055 "-" "bot" "-"
123.123.12.123 - - [11/Jun/2019:07:52:23 +0000] "GET /robots.txt HTTP/1.1" 0.007 0.007 404 2055 "-" "bot" "-"
123.123.12.123 - - [11/Jun/2019:07:56:02 +0000] "GET /this/is/another/path HTTP/1.1" 210.919 185.142 302 255958653 "-" "Apache-HttpClient/4.5.3 (Java/11.0.3)" "-"
'''
        # Create multiple logfiles
        logfile0 = tempfile.NamedTemporaryFile(dir=self.dir_backend_log, suffix='.log')
        logfile1 = tempfile.NamedTemporaryFile(dir=self.dir_backend_log, suffix='.log')
        logs0 = str.encode(logs0)
        logs1 = str.encode(logs1)
        logfile0.write(logs0)
        logfile1.write(logs1)
        print(os.listdir(self.dir_backend_log))
        print(logfile0.name)
        backend_logging.import_logs_to_db(self.app)


class UtilTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

    def test_serialize_datetime(self):
        now = datetime.datetime.now()
        serialized = util.serialize(now)
        self.assertEqual(now.__str__(), serialized)

    def test_read_write(self):
        # Create temporary directory write and read files from it and delet it.
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


class AdminAPITest(BaseTest):
    url_base = '/admin'

    def test_export_collection(self):
        with self.app.test_client() as c:
            response = c.get(f'{self.url_base}/test/export')
            self.assertEqual(401, response.status_code)
            response = c.get(
                f'{self.url_base}/test/export',
                headers={'Authorization': f'Bearer {self.admin_bearer_token}'}
            )
            self.assertEqual(200, response.status_code)

    def test_remove_collection(self):
        with self.app.test_client() as c:
            response = c.delete(f'{self.url_base}/test/remove')
            self.assertEqual(401, response.status_code)
            response = c.delete(
                f'{self.url_base}/test/remove',
                headers={'Authorization': f'Bearer {self.admin_bearer_token}'}
            )
            self.assertEqual(200, response.status_code)


class NginxLogConverterTest(BaseTest):
    def setUp(self):
        self.nlc = backend_logging.NginxLogConverter(self.app)

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
        log_entry = '217.172.12.199 - 3332v17ac8g179541c6c67574202811111d44377 [11/Jun/2019:05:28:00 +0000] ' \
                    '"GET /sonarqube/api/?param=foo HTTP/1.1" 0.015 0.015 200 7603 "-" "ScannerCli/3.3.0.1492" "-"'
        expected_log_object = {
            'remote_address': '217.172.12.199',
            'remote_user': '3332v17ac8g179541c6c67574202811111d44377',
            'time_local': '11/Jun/2019:05:28:00 +0000',
            'request': 'GET /sonarqube/api/?param=foo HTTP/1.1',
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
        # Test exception
        try:
            # Remove the remote address from string so it would fail
            self.nlc._log_entry_to_log_object(log_entry[14:])
            self.fail()
        except AttributeError:
            pass

    def test_log_object_to_document(self):
        log_object = {
            'remote_address': '217.172.12.199',
            'remote_user': '3332v17ac8g179541c6c67574202811111d44377',
            'time_local': '11/Jun/2019:08:49:39 +0000',
            'request': 'POST /this/is/a/path HTTP/1.1',
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
            'remoteUser': '3332v17ac8g179541c6c67574202811111d44377',
            'timeLocal': datetime.datetime(2019, 6, 11, 8, 49, 39, tzinfo=tzutc()),
            'request': 'POST /this/is/a/path HTTP/1.1',
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
        expected_document['path'] = '/this/is/a/path'
        expected_document['protocol'] = 'HTTP/1.1'
        self.assertEqual(expected_document, given_document)
        try:
            # Remove the remote address from string so it would fail
            del log_object['remote_address']
            self.nlc._log_object_to_document(log_object)
            self.fail()
        except KeyError:
            pass

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
                    '"GET /another/path/ HTTP/1.1" ' \
                    '0.514 - 200 42098 "-" "Some browser / 13 4pojfd" "-"'
        log_documents = self.nlc.logfile_to_documents(log_file)
        self.assertEqual(2, len(log_documents))
        log_file += '\n'
        # Bad log file should not be converted
        log_file += '217.172.12.199 - - [something is wrong] ' \
                    '"GET / HTTP/2.0" ' \
                    '0.514 - 200 42098 "-" "A user agent <.39" "-"'
        log_documents = self.nlc.logfile_to_documents(log_file)
        self.assertEqual(2, len(log_documents))


if __name__ == '__main__':
    unittest.main()
