"""
created at: 2018-12-19
author:     Volodymyr Biryuk

This module provides the api blueprints for retrieving frontend debug_logs.
"""
import copy
import json
import os
import re

import dateutil.parser as dp
from flask import Blueprint, Response, current_app, request, Flask
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


@api.record_once
def record_once(state):
    """
    Initialize all necessary components as soon as the Blueprint is registered with the app.
    :param state: The state of the Flask app.
    :return: None
    """
    app_object = state.app
    init_db_connection(app_object)
    init_script(app_object)
    return None


def init_db_connection(app_object: Flask):
    """
    Create a database connection before the first request reaches the designated function.
    The function initializes the db client regardless of whether the connection was successful.
    The client is able to reconnect if the database becomes available.
    :return: None
    """
    global frontend_logs
    client = data_access.init_mongodb_connection(app_object)
    db = client[app_object.config['DB_NAME_FRONTEND_LOGS']]
    frontend_logs = db[app_object.config['DB_COLLECTION_NAME_FRONTEND_LOGS']]
    app_object.logger.info(f'Connected to database.')
    return None


def init_script(app_object: Flask):
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
        endpoint_url = app_object.config['API_URL']
        file = re.sub(r'(const endpoint_url = "";)', f'const endpoint_url = "{endpoint_url}";', file)
        # Minify js file
        file = jsmin(file)
        # Obfuscate js file
        # file = jsobf.obfuscate(file)
        full_path = os.path.join(dirname, 'logger.min.js')
        util.write_file(full_path, file)
    except Exception as e:
        pass
        # print(e)
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
        # print(query_result)
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
    except (Exception) as e:
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
        query = _build_query(request.args)
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
        project_id = body['projectId']
        requirement_id = body['requirementId']
        log_dict = {'ip': ip, 'event_type': event_type, 'header': header, 'body': body}
        frontend_logs.insert_one(log_dict)
        response_text = f'Saved {event_type} for requirementId: {requirement_id} ; projectId: {project_id}'
        http_status = 200
    except (TypeError, KeyError, AttributeError) as e:
        http_status = 400
        response_text = 'Log is missing in the request or Missing property "type" in the log.'
        current_app.logger.debug(f'Responding with code: {http_status}. Caused by {e}')
    except Exception as e:
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


def _build_query(parameters: dict, base_query: dict = None):
    """
    Build a query to get logs by parameters
    :param parameters: Dict of parameters specified by the API.
    :param base_query: A base query where to add sub_queries to.
    :return:
    """
    # Query parameters
    query = base_query if base_query else {}
    if bool(parameters):
        query = {'$and': []}
        for k, v in parameters.items():
            # Ignore parameter if value is made up of space characters only
            if not v.isspace():
                if k == 'from' or k == 'to':
                    iso_date_string = f'{v}T00:00:00.000Z'
                    iso_date = dp.parse(iso_date_string)
                    if k == 'from':
                        query['$and'].append({'body.isoTime': {'$gte': iso_date}})
                    elif k == 'to':
                        query['$and'].append({'body.isoTime': {'$lte': iso_date}})
                else:
                    sub_query = {f'body.{k}': v}
                    query['$and'].append(sub_query)
    return query


if __name__ == '__main__':
    pass
