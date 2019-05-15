"""
created at: 2018-12-19
author:     Volodymyr Biryuk

This module provides the api blueprints for retrieving backend debug_logs.
"""
import json
import os
import re
from datetime import datetime

from apscheduler.triggers.cron import CronTrigger
from dateutil import parser as datutil_parser
from flask import Blueprint, current_app, request, Response, Flask
from pymongo.collection import Collection
from pymongo.errors import ServerSelectionTimeoutError, NetworkTimeout

from microservice import auth, util, data_access

api = Blueprint('backend_logging_api', __name__, url_prefix='/backend')

backend_logs: Collection = None
back_end_log_dir: str = None


def get_backend_log_path():
    return current_app.config['DIR_BACKEND_LOG']


@api.record_once
def record_once(state):
    """
    Initialize all necessary components as soon as the Blueprint is registered with the app.
    :param state: The state of the Flask app.
    :return: None
    """
    app_object = state.app
    __init_db_connection(app_object)
    __init_directories(app_object)
    __init_scheduler(app_object)
    return None


def __init_directories(app_object: Flask):
    """
    Check if the backend log directory exists and is readable.
    :return: None
    """
    global back_end_log_dir
    back_end_log_dir = app_object.config['DIR_BACKEND_LOG']
    try:
        path = os.path.isdir(back_end_log_dir)
        if path:
            app_object.logger.info(f'Backend log directory exists in {path}.')
        else:
            app_object.logger.error('Backend log directory does not exists.')
    except PermissionError as e:
        app_object.logger.error('Backend log directory Read permission denied.')
        app_object.logger.debug(e)
    try:
        app_object.logger.debug('Backend log files:')
        for file in os.listdir(back_end_log_dir):
            app_object.logger.debug(file)
    except Exception as e:
        app_object.logger.debug(e)
    return None


def __init_db_connection(app_object: Flask):
    """
    Create a database connection before the first request reaches the designated function.
    The function initializes the db client regardless of whether the connection was successful.
    The client is able to reconnect if the database becomes available.
    :return: None
    """
    try:
        app_object.logger.info(f'Initializing database connection.')
        host = app_object.config['DB_HOST']
        port = app_object.config['DB_PORT']
        try:
            user = os.environ['DB_USER']
        except (KeyError, Exception):
            user = ''
        try:
            password = os.environ['DB_PASSWORD']
        except (KeyError, Exception):
            password = ''
        connect_timeout = app_object.config['DB_CONNECTION_TIMEOUT']
        auth_mechanism = app_object.config['DB_AUTH_MECHANISM']
        global backend_logs
        client = data_access.MongoDBConnection(
            host=host,
            port=port,
            username=user,
            password=password,
            auth_mechanism=auth_mechanism,
            connect_timeout=connect_timeout
        ).client
        db = client[app_object.config['DB_NAME_FRONTEND_LOGS']]
        backend_logs = db['backend']
        app_object.logger.info(f'Connected to database.')
    except ServerSelectionTimeoutError as e:
        app_object.logger.error(f'Could not connect to database.')
    return None


def __init_scheduler(app_object: Flask):
    """
    Initialize the scheduled job for the backend og import into the DB.
    :param app_object: The Flask app object.
    :return: None
    """
    scheduled_time = app_object.config['BACKEND_LOG_SCHEDULE']
    app_object.logger.info(f'Scheduled job for - {scheduled_time}')
    scheduled_time = scheduled_time.split(':')
    hour = scheduled_time[0]
    minute = scheduled_time[1]
    trigger = CronTrigger(hour=hour, minute=minute, timezone='Europe/Berlin')
    app_object.scheduler.add_job(import_logs_to_db, trigger=trigger, args=[app_object])
    app_object.logger.info(f'Added job to scheduler.')
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
        f'Processing backend log {request.method} request from remote address: {request.remote_addr}')
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
        f'Processing backend log {request.method} request from remote address: {request.remote_addr}')
    response_body = ''
    content_type = 'application/json'
    http_status = 200
    try:
        format = 'json'
        try:
            format = request.args.get('format')
        except KeyError:
            pass
        log_dir = get_backend_log_path()
        full_path = os.path.join(log_dir, log_name)
        if full_path.endswith('.gz'):
            unzipped_file = util.unzip(full_path).decode('utf-8')
            if format == 'text':
                response_body = unzipped_file
                content_type = 'text/plain'
            else:
                response_body = json.dumps({'log': unzipped_file})
        else:
            file_content = util.read_file(full_path)
            response_body = json.dumps({'log': file_content})
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


def import_logs_to_db(app_object: Flask):
    """
    Imports all gzipped access logs into the DB excluding already imported files and the current log file.
    Only gzipped logs are imported as they are finalized.
    :return: HTTP Response.
    """
    def log_entry_to_dict(log_entry: str):
        """
        Convert a default formatted log entry (one line) of a NGINX log file to a python dict.
        :param log_entry: One line of a NGINX log file.
        :return: A pyhon dict representation of a log entry.
        """

        def nginx_local_time_to_iso_date(nginx_date: str):
            """
            Convert the log timestamp to iso date.
            :param nginx_date: The default Nginx formatted timestamp e.g. 29/Sep/2016:10:20:48 +0100.
            :return: The iso date representation of the timestamp.
            """
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
            log_object['httpMethod'] = ''
            log_object['path'] = ''
            log_object['httpVersion'] = ''
            log_object['request'] = split_line
            if len(split1) >= 3:
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
        # if log_entry.startswith('61.219'):
        #     print('aaa')
        split_line = log_entry.split('"')
        split_line = [split for split in split_line if split != ' ']

        part0(split_line[0])

        part1(split_line[1])

        part2(split_line[2])

        part3(split_line[3])

        part4(split_line[4])

        part5(split_line[5])

        return log_object

    def import_log_to_db(app_object: Flask, file_name: str):
        """
        Import a Nginx log file into the backend log database.
        :return:
        """
        full_path = os.path.join(back_end_log_dir, file_name)
        file_content = util.unzip(full_path).decode('utf-8')
        log = file_content
        lines = log.split('\n')
        log_objects = []
        now = datetime.now()
        for line in lines:
            # Non empty lines only
            if line:
                try:
                    log_object = log_entry_to_dict(line)
                    log_object['insertionTime'] = now
                    log_object['fileName'] = file_name
                    log_objects.append(log_object)
                except IndexError as e:
                    app_object.logger.warn(f'Error converting line: {line}')
        try:
            app_object.logger.info(f'Inserting backend log into DB.')
            backend_logs.insert_many(log_objects)
        except (ServerSelectionTimeoutError, NetworkTimeout)as e:
            app_object.logger.error(f'Database error: {e}')
            app_object.logger.debug(e)
            raise e
        app_object.logger.info(f'Inserted {len(log_objects)}.')
        return None

    try:
        dir_path = app_object.config['DIR_BACKEND_LOG']
        files = os.listdir(dir_path)
        # Match logs with names such as access.log-20190425.gz
        files_in_dir = [file for file in files if re.match(r'access\.log-.+\.gz', file)]
        files_in_db = backend_logs.distinct('fileName')
        # Only keep files that are in the dir but not in the db
        files_missing = [file for file in files_in_dir if file not in files_in_db]
        file_count = len(files_missing)
        if file_count > 0:
            app_object.logger.info(f'Inserting {file_count} files into db.')
            for i, file in enumerate(files_missing):
                app_object.logger.info(f'Inserting file {i + 1}/{file_count} into DB.')
                import_log_to_db(app_object, file)
        else:
            app_object.logger.info(f'No new log files detected.')
    except (ServerSelectionTimeoutError, PermissionError)as e:
        app_object.logger.error(f'Database error: {e}')
        app_object.logger.debug(e)
    except (Exception) as e:
        app_object.logger.error(f'Unexpected error : {e}')
        app_object.logger.debug(e)
    return None


if __name__ == '__main__':
    pass
