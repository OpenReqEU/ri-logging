"""
created at: 2019-02-08
author: Volodymyr Biryuk

This module provides functionality to access admin functions of the microservice.
"""
import json
import os

from bson import json_util
from flask import Blueprint, Response, current_app, Flask, request
from pymongo.errors import ServerSelectionTimeoutError

from . import auth
from . import data_access

api = Blueprint('admin_api', __name__, url_prefix='/admin')
db = None


@api.record_once
def record_once(state):
    """
    Initialize all necessary components as soon as the Blueprint is registered with the app.
    :param state: The state of the Flask app.
    :return: None
    """
    __init_db_connection(state.app)


def __init_db_connection(app_object: Flask):
    """
    Create a database connection before the first request reaches the designated function.
    The function initializes the db client regardless of whether the connection was successful.
    The client is able to reconnect if the database becomes available.
    :return: None
    """
    global db
    global frontend_logs
    client = data_access.init_mongodb_connection(app_object)
    db = client[app_object.config['DB_NAME_FRONTEND_LOGS']]
    frontend_logs = db[app_object.config['DB_COLLECTION_NAME_FRONTEND_LOGS']]
    app_object.logger.info(f'Connected to database.')
    return None


@api.route('/<collection_name>/remove', methods=['DELETE'])
@auth.auth_admin
def delete_documents(collection_name):
    """
    Use with extreme caution as this will delete all documents in the frontend logging collection.
    :param collection_name: The name of the collection to be cleaned out.
    :return: HTTP Response
    """
    http_status = 200
    mimetype = 'application/json'
    response_body = json.dumps({})
    try:
        query_result = db[collection_name].delete_many({})
        response_body = json.dumps(
            {'message': f'Removed {query_result.deleted_count} entries from {db.name} -- {collection_name}'})
    except (data_access.ServerSelectionTimeoutError, data_access.NetworkTimeout, Exception) as e:
        http_status = 500
        mimetype = 'application/json'
        current_app.logger.error(f'Error: {e}')
        response_body = json.dumps({'message': f'Something went wrong.'})
    finally:
        response = Response(response=response_body, status=http_status, mimetype=mimetype)
        current_app.logger.debug(f'Responding with code: {http_status}')
        return response


@api.route('/<collection_name>/export', methods=['GET'])
@auth.auth_admin
def export_documents(collection_name):
    """
    Export a collection from the database as json.
    :param collection_name: The name of the collection to be exported.
    :return: HTTP Response
    """
    http_status = 200
    mimetype = 'application/json'
    response_body = json.dumps({})
    try:
        query_result = db[collection_name].find()
        response_body = ''
        for item in query_result:
            string_item = json_util.dumps(item)
            response_body += string_item
    except (data_access.ServerSelectionTimeoutError, data_access.NetworkTimeout, Exception) as e:
        http_status = 500
        mimetype = 'application/json'
        current_app.logger.error(f'Error: {e}')
        response_body = json.dumps({'message': f'Something went wrong.'})
    finally:
        response = Response(response=response_body, status=http_status, mimetype=mimetype)
        current_app.logger.debug(f'Responding with code: {http_status}')
        return response


@api.route('/<collection_name>/clean', methods=['PATCH'])
@auth.auth_admin
def clean_documents(collection_name):
    """
    Clean a collection from invalid value .
    :param collection_name: The name of the collection to be exported.
    :return: HTTP Response
    """
    http_status = 200
    mimetype = 'application/json'
    response_body = json.dumps({})
    body = request.get_json()
    try:
        db[collection_name].remove(body['query'])
        response_body = ''
    except Exception as e:
        http_status = 500
        mimetype = 'application/json'
        current_app.logger.error(f'Error: {e}')
        response_body = json.dumps({'message': f'Something went wrong.'})
    except KeyError as e:
        http_status = 400
        mimetype = 'application/json'
        current_app.logger.error(f'Error: {e}')
        response_body = json.dumps({'message': f'Query attribute is missing'})
    finally:
        response = Response(response=response_body, status=http_status, mimetype=mimetype)
        current_app.logger.debug(f'Responding with code: {http_status}')
        return response


if __name__ == '__main__':
    pass
