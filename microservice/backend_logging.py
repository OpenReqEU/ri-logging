"""
created at: 2018-12-19
author:     Volodymyr Biryuk

This module provides the api blueprints for retrieving backend debug_logs.
"""
import os
import json
import re

from flask import Blueprint, current_app, request, Response
from dateutil import parser as datutil_parser
from datetime import datetime
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.collection import Collection

from . import auth, util, data_access

api = Blueprint('backend_logging_api', __name__, url_prefix='/backend')

backend_logs: Collection = None


def get_backend_log_path():
    return current_app.config['DIR_BACKEND_LOG']


def get_backend_log_collection():
    return current_app.config['DIR_BACKEND_LOG']


@api.before_app_first_request
def __init_api():
    __init_directories()
    __init_db_connection()
    return None


def __init_directories():
    """
    Check if the backend log directory exists and is readable.
    :return: None
    """
    global back_end_log_dir
    back_end_log_dir = get_backend_log_path()
    try:
        path = os.path.isdir(back_end_log_dir)
        if path:
            current_app.logger.info(f'Backend log directory exists in {path}.')
        else:
            current_app.logger.error('Backend log directory does not exists.')
    except PermissionError as e:
        current_app.logger.error('Backend log directory Read permission denied.')
        current_app.logger.debug(e)
    try:
        current_app.logger.debug('Backend log files:')
        for file in os.listdir(back_end_log_dir):
            current_app.logger.debug(file)
    except Exception as e:
        current_app.logger.debug(e)
    return None


def __init_db_connection():
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
        global backend_logs
        client = data_access.MongoDBConnection(
            host=host,
            port=port,
            username=user,
            password=password,
            auth_mechanism=auth_mechanism,
            connect_timeout=connect_timeout
        ).client
        db = client[current_app.config['DB_NAME_FRONTEND_LOGS']]
        backend_logs = db['backend']
        current_app.logger.info(f'Connected to database.')
    except ServerSelectionTimeoutError as e:
        current_app.logger.error(f'Could not connect to database.')
    return None


@api.route('/log', methods=['GET'])
@auth.auth_single
def logs_get():
    """
    :reqheader Accept: application/json
    Return all logfile names.
    :return: The filenames for all backend debug_logs as json.
    """
    current_app.logger.info(
        f'Processing backend logfiles {request.method} '
        f'request from remote address: {request.remote_addr}'
    )
    response_body = ''
    content_type = 'application/json'
    http_status = 200
    try:
        response_body = json.dumps({'filenames': os.listdir(get_backend_log_path())})
        content_type = 'application/json'
        http_status = 200
    except (PermissionError, Exception)as e:
        current_app.logger.error(f'OS error: {e}')
        response_body = json.dumps({'message': 'Internal error.'})
        content_type = 'application/json'
        http_status = 500
    except FileNotFoundError as e:
        current_app.logger.error(f'OS error: {e}')
        response_body = json.dumps({'message': "Log doesn't exist."})
        content_type = 'application/json'
        http_status = 204
    finally:
        response = Response(response=response_body, status=http_status, content_type=content_type)
        current_app.logger.debug(f'Responding with code: {http_status}')
        return response


@api.route('/log/<string:log_name>', methods=['GET'])
@auth.auth_single
def log_get(log_name):
    """
    :reqheader Accept: application/json
    Return all logfile names.
    :return: The filenames for all backend debug_logs as json.
    """
    current_app.logger.info(
        f'Processing backend log {request.method} '
        f'request from remote address: {request.remote_addr}'
    )
    response_body = ''
    content_type = 'application/json'
    http_status = 200
    try:
        log_dir = get_backend_log_path()
        full_path = os.path.join(log_dir, log_name)
        if full_path.endswith('.gz'):
            response_body = json.dumps({'log': util.unzip(full_path).decode('utf-8')})
            print(response_body)
        else:
            file_content = util.read_file(full_path)
            response_body = json.dumps({'log': file_content})
        content_type = 'application/json'
        http_status = 200
    except (PermissionError, Exception)as e:
        current_app.logger.error(f'OS error: {e}')
        response_body = json.dumps({'message': 'Internal error.'})
        content_type = 'application/json'
        http_status = 500
    except (OSError, FileNotFoundError) as e:
        current_app.logger.error(f'OS error: {e}')
        response_body = json.dumps({'message': "Log doesn't exist."})
        content_type = 'application/json'
        http_status = 404
    finally:
        response = Response(response=response_body, status=http_status, content_type=content_type)
        current_app.logger.info(f'Responding with code: {http_status}')
        return response


@api.route('/import', methods=['GET'])
@auth.auth_single
def log_entry_to_dict(log_entry: str):
    """
    Convert a log entry (one line) of a NGINX log file to a python dict.
    :param log_entry: One line of a NGINX log file.
    :return: A pyhon dict representation of a log entry.
    """

    def nginx_local_time_to_iso_date(nginx_date: str):
        months = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5, 'Jul': 6, 'Aug': 7, 'Sep': 8,
                  'Oct': 9, 'Nov': 10, 'Dec': 11}
        nginx_date = nginx_date.replace(' ', '')
        split = nginx_date.split('/')
        day = split[0]
        month = months[split[1]]
        split = split[2].split(':')
        year = split[0]
        hour = split[1]
        minute = split[2]
        split = split[3].split('+')
        second = split[0]
        timezone = f'{split[1][:-2]}:{split[1][2:]}'
        iso_date = f'{year}-{month}-{day}T{hour}:{minute}:{second}+{timezone}'
        return datutil_parser.parse(iso_date)

    def part0(line_split: str):
        split = re.split(r'\[|\]', line_split)
        remote_address_and_user = split[0].split(' ')
        remote_addr = remote_address_and_user[0]
        hyphen = remote_address_and_user[1]
        remote_user = remote_address_and_user[2]
        log_object['remoteAddr'] = remote_addr
        log_object['remoteUser'] = remote_user
        log_object['isoDate'] = nginx_local_time_to_iso_date(split[1])
        return None

    def part1(split_line: str):
        split1 = split_line.split(' ')
        http_method = split1[0]
        path = split1[1]
        http_version = split1[2]
        log_object['httpMethod'] = http_method
        log_object['path'] = path
        log_object['httpVersion'] = http_version
        return None

    def part2(split_line: str):
        split = split_line.split(' ')
        status = split[1]
        body_bytes_sent = split[2]
        log_object['status'] = status
        log_object['bodyBytesSent'] = body_bytes_sent
        return None

    def part3(split_line: str):
        log_object['httpReferer'] = split_line
        return None

    def part4(split_line: str):
        log_object['httpUserAgent'] = split_line
        return None

    def part5(split_line: str):
        log_object['httpXForwardedFor'] = split_line
        return None

    log_object = {}
    split_line = log_entry.split('"')
    split_line = [split for split in split_line if split != ' ']
    part0(split_line[0])
    part1(split_line[1])
    part2(split_line[2])
    part3(split_line[3])
    part4(split_line[4])
    part5(split_line[5])
    return log_object


def import_log_to_db():
    """
    Import an NGINX log file into the backend log database.
    :return:
    """
    log_dir = get_backend_log_path()
    full_path = os.path.join(log_dir, 'access.log')
    file_content = util.read_file(full_path)
    log = file_content
    lines = log.split('\n')
    log_objects = []
    now = datetime.now()
    for line in lines:
        log_object = log_entry_to_dict(line)
        log_object['insertionTime'] = now
        log_objects.append(log_object)
    try:
        current_app.logger.info(f'Inserting backend log into DB.')
        backend_logs.insert_many(log_objects)
    except (data_access.ServerSelectionTimeoutError, data_access.NetworkTimeout)as e:
        current_app.logger.warning(e)
    current_app.logger.info(f'Inserted {len(log_objects)}.')


# TODO: Implement scheduler for log import


if __name__ == '__main__':
    pass
