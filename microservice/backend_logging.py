"""
created at: 2018-12-19
author:     Volodymyr Biryuk

This module provides the api blueprints for retrieving backend debug_logs.
"""
import os
import json

from flask import Blueprint, current_app, request, Response

from . import auth, util

api = Blueprint('backend_logging_api', __name__, url_prefix='/backend')


@api.before_app_first_request
def __init_api():
    __init_directories()
    return None


def __init_directories():
    """
    Check if the backend log directory exists and is readable.
    :return: None
    """
    back_end_log_dir = current_app.config['DIR_BACKEND_LOG']
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
        response_body = json.dumps({'filenames': os.listdir(current_app.config['DIR_BACKEND_LOG'])})
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
        log_dir = current_app.config['DIR_BACKEND_LOG']
        full_path = os.path.join(log_dir, log_name)
        if full_path.endswith('.gz'):
            response_body = json.dumps({'log': util.unzip(full_path).decode('utf-8')})
            print(response_body)
        else:
            response_body = json.dumps({'log': util.read_file(full_path)})
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


if __name__ == '__main__':
    pass
