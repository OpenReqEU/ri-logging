"""
created at: 2018-12-19
author:     Volodymyr Biryuk

This module provides functionality for database access.
"""
import os
from flask import Flask
import logging
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

logger = logging.getLogger('flask.app')

class MongoDBConnection():
    """A connector object for MongoDB"""

    def __init__(self, host: str, port: int, auth_mechanism: str = None, username: str = None,
                 password: str = None, connect_timeout: int = 500):
        self.host = host
        self.port = int(port)
        self.auth_mechanism = auth_mechanism
        self.username = username
        self.password = password
        self.connect_timeout = int(connect_timeout)
        self.client = self.__connect()

    def __connect(self) -> MongoClient:
        logger.debug(f'Connecting to database with settings:')
        logger.debug(f'{self.__dict__}')
        if self.auth_mechanism:
            client = MongoClient(host=self.host,
                                 port=self.port,
                                 authMechanism=self.auth_mechanism,
                                 username=self.username,
                                 password=self.password,
                                 serverSelectionTimeoutMS=self.connect_timeout)
        else:
            client = MongoClient(host=self.host,
                                 port=self.port,
                                 serverSelectionTimeoutMS=self.connect_timeout)
        try:
            logger.debug(client.server_info())
        except Exception as e:
            logger.debug(e)
        finally:
            return client


def init_mongodb_connection(app_object: Flask):
    """
    Create a database connection before the first request reaches the designated function.
    The function initializes the db client regardless of whether the connection was successful.
    The client is able to reconnect if the database becomes available.
    :return: None
    """
    client = None
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
        client = MongoDBConnection(
            host=host,
            port=port,
            username=user,
            password=password,
            auth_mechanism=auth_mechanism,
            connect_timeout=connect_timeout
        ).client
    except ServerSelectionTimeoutError as e:
        app_object.logger.error(e)
    return client


if __name__ == "__main__":
    pass
