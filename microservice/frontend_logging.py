"""
created at: 2018-12-19
author:     Volodymyr Biryuk

This module provides the api blueprints for retrieving frontend debug_logs.
"""
from flask import Blueprint, Response, current_app, request
from . import auth
import json
from jsmin import jsmin
import re
import os
from . import util
from . import data_access
from . import jsobf
from pymongo.collection import Collection
from pymongo.errors import ServerSelectionTimeoutError

api = Blueprint('frontend_logging_api', __name__, url_prefix='/frontend')

frontend_logs: Collection = None


@api.before_app_first_request
def __init_api():
    init_db_connection()
    init_script()


def init_db_connection():
    """
    Create a database connection before the first request reaches the designated function.
    The function initializes the db client regardless of whether the connection was successful.
    The client is able to reconnect if the database becomes available.
    :return: None
    """
    try:
        current_app.logger.info(f'Initializing database connection.')
        host = current_app.config['DB_HOST']
        port = current_app.config['DB_PORT']
        try:
            user = os.environ['DB_USER']
        except (KeyError, Exception):
            user = ''
        try:
            password = os.environ['DB_PASSWORD']
        except (KeyError, Exception):
            password = ''
        connect_timeout = current_app.config['DB_CONNECTION_TIMEOUT']
        auth_mechanism = current_app.config['DB_AUTH_MECHANISM']
        global frontend_logs
        client = data_access.MongoDBConnection(
            host=host,
            port=port,
            username=user,
            password=password,
            auth_mechanism=auth_mechanism,
            connect_timeout=connect_timeout
        ).client
        db = client[current_app.config['DB_NAME_FRONTEND_LOGS']]
        frontend_logs = db['log']
        current_app.logger.info(f'Connected to database.')
    except ServerSelectionTimeoutError as e:
        current_app.logger.error(f'Could not connect to database.')
    return None


def init_script():
    """
    Initialize the frontend logging script:
    1) Set the endpoint URL where the logs shall be sent.
    2) Minify the script.
    3) Obfuscate the script.
    :return: None
    """
    try:
        dirname = os.path.join(os.path.dirname(__file__), 'js')
        full_path = os.path.join(dirname, 'logger.js')
        file = util.read_file(full_path)
        endpoint_url = current_app.config['API_URL']
        file = re.sub(r'(const endpoint_url = "";)', f'const endpoint_url = "{endpoint_url}";', file)
        # Minify js file
        file = jsmin(file)
        # Obfuscate js file
        # file = jsobf.obfuscate(file)
        full_path = os.path.join(dirname, 'logger.min.js')
        util.write_file(full_path, file)
    except Exception as e:
        print(e)
    return None


@api.route('/log', methods=['GET'])
@auth.auth_single
def log_get():
    http_status = 200
    mimetype = 'application/json'
    response_body = json.dumps({})
    try:
        response_body = json.dumps({'logs': list(frontend_logs.find({}, {'_id': 0}))})
    except (data_access.ServerSelectionTimeoutError, data_access.NetworkTimeout, Exception) as e:
        http_status = 500
        mimetype = 'application/json'
        current_app.logger.error(f'Error: {e}')
        response_body = json.dumps({'message': f'Something went wrong.'})
    finally:
        response = Response(response=response_body, status=http_status, mimetype=mimetype)
        current_app.logger.debug(f'Responding with code: {http_status}')
        return response


@api.route('/log', methods=['POST'])
def log_post():
    """
    .. :quickref: Posts Log; Add new log to database.
    :status 200: log written
    :status 500: database failure
    :return:
    """
    current_app.logger.debug(
        f'Processing frontend logging {request.method} request from remote address: {request.remote_addr}')
    mimetype = 'application/json'
    response_text = ''
    http_status = 200
    ip = request.remote_addr
    header = {t[0]: t[1] for t in request.headers.items()}
    body = request.get_json()
    try:
        event_type = body['type']
        log_dict = {'ip': ip, 'event_type': event_type, 'header': header, 'body': body}
        frontend_logs.insert_one(log_dict)
        response_text = 'Saved to database.'
        http_status = 200
    except (TypeError, KeyError) as e:
        http_status = 400
        response_text = 'Log is missing in the request or Missing property "type" in the log.'
        current_app.logger.debug(f'Responding with code: {http_status}. Caused by {e}')
    except (data_access.ServerSelectionTimeoutError, data_access.NetworkTimeout, AttributeError)as e:
        current_app.logger.error(f'Database error: {e}')
        response_text = f'Could not save to database: {e}'
        mimetype = 'text/plain'
        http_status = 500
    finally:
        response_body = json.dumps({'message': response_text})
        response = Response(response=response_body, status=http_status, mimetype=mimetype)
        current_app.logger.debug(f'Responding with code: {http_status}')
        return response


@api.route('/script', methods=['GET'])
def get_logger_script():
    """
    Serve the JavaScript file like a CDN.
    :return: The JavaScript file
    """
    current_app.logger.debug(f'Processing logger.js request from remote address: {request.remote_addr}')
    response_body = {}
    http_status = 200
    mimetype = 'application/javascript'
    try:
        response_body = util.read_file(os.path.join(os.path.dirname(__file__), 'js', 'logger.min.js'))
        http_status = 200
        mimetype = 'application/javascript'
    except FileNotFoundError:
        response_body = json.dumps("No such file exists.")
        http_status = 404
        mimetype = 'text/plain'
    finally:
        current_app.logger.debug(f'Responding with code: {http_status}')
        response = Response(response=response_body, status=http_status, mimetype=mimetype)
        return response


if __name__ == '__main__':
    pass
