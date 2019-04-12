"""
created at: 2018-12-19
author:     Volodymyr Biryuk

This module provides the api blueprints for retrieving frontend debug_logs.
"""
import copy
import json
import os
import re
from collections import Counter

import dateutil.parser as dp
from flask import Blueprint, Response, current_app, request
from jsmin import jsmin
from pymongo.collection import Collection
from pymongo.errors import ServerSelectionTimeoutError

from . import auth
from . import data_access
from . import util

api = Blueprint('frontend_logging_api', __name__, url_prefix='/frontend')

frontend_logs: Collection = None

dom_element_mapping = {
    'or-requirement-title form-control': 'title',
    'or-requirement-title': 'title',
    'note-editable or-description-active': 'description',
    'note-editable': 'description',
    'select-dropdown': 'status',
    'title': 'or-requirement-title form-control',
    'description': 'note-editable or-description-active',
    'status': 'select-dropdown'
}

default_count = {
    'description': 0,
    'status': 0,
    'title': 0
}


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


@api.route('/log/<project_id>', defaults={'requirement_id': None}, methods=['GET'])
@api.route('/log/<project_id>/<requirement_id>')
@auth.auth_single
def log_by_project_id_get(project_id: str, requirement_id: str = None):
    """
    Return all logs for a given project and requirement.
    :param project_id: The project id.
    :param requirement_id: The requirement item's id (optional).
    :return: The logs.
    """
    http_status = 200
    mimetype = 'application/json'
    response_body = json.dumps({})
    try:
        query = {'body.projectId': project_id}
        if requirement_id:
            query['body.requirementId'] = requirement_id
        query_result = list(frontend_logs.find(query, {'_id': 0}))
        print(query_result)
        response_body = json.dumps({'logs': query_result}, default=util.serialize)
    except (data_access.ServerSelectionTimeoutError, data_access.NetworkTimeout, Exception) as e:
        http_status = 500
        mimetype = 'application/json'
        current_app.logger.error(f'Error: {e}')
        response_body = json.dumps({'message': f'Something went wrong.'})
    finally:
        response = Response(response=response_body, status=http_status, mimetype=mimetype)
        current_app.logger.debug(f'Responding with code: {http_status}')
        return response


@api.route('/change', defaults={'project_id': None}, methods=['GET'])
@api.route('/change/<project_id>')
@auth.auth_single
def changes_get(project_id):
    """
    Return for a given project the number of changes to the title, description or status per requirement.
    :param project_id: The project id.
    :return: Count of changes to the title, description or status of requirements of a given project.
    """
    http_status = 200
    mimetype = 'application/json'
    response_body = json.dumps({})
    try:
        request_arguments = request.args
        aggregation = [
            {
                "$match": {
                    '$and': [
                        {'$or': [
                            {'body.type': 'blur'},
                            {'body.type': 'change'}
                        ]},
                        {'$or': [
                            {'body.targetclassName': 'note-editable'},
                            {'body.targetclassName': 'note-editable or-description-active'},
                            {'body.targetclassName': 'or-requirement-title form-control'},
                            {'body.targetclassName': 'or-requirement-title'},
                            {'body.targetclassName': 'select-dropdown'}
                        ]},
                    ]
                }
            },
            {
                "$group": {
                    "_id": {
                        "domElement": "$body.targetclassName"
                    },
                    "count": {
                        "$sum": 1.0
                    }
                }
            },
            {
                "$group": {
                    "changes": {
                        "$push": {
                            "k": "$_id.domElement",
                            "v": "$count"
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0.0,
                    "changeCount": {
                        "$arrayToObject": "$changes"
                    }
                }
            }
        ]
        if project_id:
            # Add project Id to the match query
            aggregation[0]['$match']['$and'].append({"body.projectId": project_id})
            aggregation[1]['$group']['_id']['requirementId'] = '$body.requirementId'
            aggregation[2]['$group']['_id'] = '$_id.requirementId'
            aggregation[3]['$project']['requirementId'] = '$_id'
        else:
            aggregation[1]['$group']['_id']['projectId'] = '$body.projectId'
            aggregation[2]['$group']['_id'] = '$_id.projectId'
            aggregation[3]['$project']['projectId'] = '$_id'
        if request_arguments:
            try:
                username = request.args.get('username')
                # Add username to the match query
                aggregation[0]['$match']['$and'].append({"body.username": username})
            except KeyError:
                pass
        aggregation_result = list(frontend_logs.aggregate(aggregation))
        result = []
        for item in aggregation_result:
            change_count = copy.deepcopy(default_count)
            for k, v in item['changeCount'].items():
                try:
                    change_count[dom_element_mapping[k]] = v
                except KeyError as e:
                    raise e
            item['changeCount'] = change_count
            result.append(item)
        response_body = json.dumps({'changes': result}, default=util.serialize)
    except (data_access.ServerSelectionTimeoutError, data_access.NetworkTimeout, Exception) as e:
        http_status = 500
        mimetype = 'application/json'
        current_app.logger.error(f'Error: {e}')
        response_body = json.dumps({'message': f'Something went wrong.'})
    finally:
        response = Response(response=response_body, status=http_status, mimetype=mimetype)
        current_app.logger.debug(f'Responding with code: {http_status}')
        return response


@api.route('/log', methods=['GET'])
@auth.auth_single
def log_get():
    http_status = 200
    mimetype = 'application/json'
    response_body = json.dumps({})
    try:
        # Query parameters
        username_ = request.args.get('username')
        from_ = request.args.get('from')
        to_ = request.args.get('to')
        project_id = request.args.get('projectId')
        requirement_id = request.args.get('requirementId')
        query = {}
        if username_ or from_ or to_ or project_id or requirement_id:
            query['$and'] = []
            if username_:
                sub_query = {'body.username': username_}
                query['$and'].append(sub_query)
            if requirement_id:
                sub_query = {'body.requirementId': username_}
                query['$and'].append(sub_query)
            if project_id:
                sub_query = {'body.projectId': project_id}
                query['$and'].append(sub_query)
            if from_:
                from_ = f'{from_}T00:00:00.000Z'
                print(from_)
                from_parsed = dp.parse(from_)
                query['$and'].append({'body.isoTime': {'$gte': from_parsed}})
            if to_:
                to_ = f'{to_}T00:00:00.000Z'
                print(to_)
                to_parsed = dp.parse(to_)
                query['$and'].append({'body.isoTime': {'$lte': to_parsed}})
        print(query)
        response_body = json.dumps({'logs': list(frontend_logs.find(query, {'_id': 0}))}, default=util.serialize)
    except (data_access.ServerSelectionTimeoutError, data_access.NetworkTimeout, Exception) as e:
        http_status = 500
        mimetype = 'application/json'
        current_app.logger.error(f'Error: {e}')
        response_body = json.dumps({'message': f'Something went wrong.'})
    finally:
        response = Response(response=response_body, status=http_status, mimetype=mimetype)
        current_app.logger.debug(f'Responding with code: {http_status}')
        return response


@api.route('/log/change', methods=['GET'])
@auth.auth_single
def log_change_get():
    http_status = 200
    mimetype = 'application/json'
    response_body = json.dumps({})
    try:
        # Query parameters
        username_ = request.args.get('username')
        from_ = request.args.get('from')
        to_ = request.args.get('to')
        project_id = request.args.get('projectId')
        requirement_id = request.args.get('requirementId')
        query = {}
        # Only query for blur and change events
        query['$and'] = [{'$or': [{'body.type': 'change'}, {'body.type': 'blur'}]}]
        if username_ or from_ or to_ or project_id or requirement_id:
            if username_:
                sub_query = {'body.username': username_}
                query['$and'].append(sub_query)
            if requirement_id:
                sub_query = {'body.requirementId': username_}
                query['$and'].append(sub_query)
            if project_id:
                sub_query = {'body.projectId': project_id}
                query['$and'].append(sub_query)
            if from_:
                from_ = f'{from_}T00:00:00.000Z'
                print(from_)
                from_parsed = dp.parse(from_)
                query['$and'].append({'body.isoTime': {'$gte': from_parsed}})
            if to_:
                to_ = f'{to_}T00:00:00.000Z'
                print(to_)
                to_parsed = dp.parse(to_)
                query['$and'].append({'body.isoTime': {'$lte': to_parsed}})
        print(query)
        query_result = list(frontend_logs.find(query, {'_id': 0}))
        change_count = Counter(log['body']['targetclassName'] for log in query_result)
        print(change_count)
        result = {
            'projectId': project_id,
            'title': change_count['or-requirement-title'],
            'description': change_count['note-editable'],
            'status': change_count['select-dropdown']
        }
        # print(list(query_result))
        response_body = json.dumps({'logs': result}, default=util.serialize)
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
