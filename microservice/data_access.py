"""
created at: 2018-12-19
author:     Volodymyr Biryuk

This module provides functionality for database access.
"""
import logging
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError, NetworkTimeout, ConnectionFailure, \
    ConfigurationError, AutoReconnect
from pymongo import errors

logger = logging.getLogger('flask.app')


# TODO: Pull backend log daily and insert into DB


class MongoDBConnection():
    """A connector object for MongoDB"""

    def __init__(self, host: str, port: int, auth_mechanism: str = None, username: str = None,
                 password: str = None, connect_timeout: int = 30000):
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
            try:
                # Check if admin
                logger.debug(client.list_database_names())
                logger.debug(client['admin'].list_collection_names())
                logger.debug('Connected as admin')
            except OperationFailure:
                logger.debug('Connected as user')
        except OperationFailure as e:
            logger.debug(e)
            # raise e
        except NetworkTimeout as e:
            logger.debug(e)
            # raise e
        except ServerSelectionTimeoutError as e:
            logger.debug(e)
            # raise e
        except AutoReconnect as e:
            logger.debug(e)
            # raise e
        except ConnectionFailure as e:
            logger.debug(e)
            # raise e
        except ConfigurationError as e:
            # when username but no password given
            logger.debug(e)
            # raise e
        except Exception as e:
            # Generic case if none of the above triggers
            logger.error(f"Unexpected Exception: {e}")
            # raise e
        finally:
            return client

    def test_connection(self, db_name):
        """
        Test the connection to a particular database
        :param db_name: The databse name.
        :return: True is connection possible, False if
        """
        try:
            db = self.client[db_name]
            result = db.list_collection_names() is not None
        except OperationFailure as e:
            result = 'DB doesn\'t exist or no permission'
        except ServerSelectionTimeoutError as e:
            result = 'Server selection timed out.'
        return result

    def get_database_names(self):
        return self.client.list_database_names()

    def get_collection_names(self, db_name: str):
        return self.client[db_name].collection_names()

    def save_document(self, db_name: str, collection_name: str, document: dict):
        try:
            logger.debug(f'Saving to database {db_name}.{collection_name}')
            db = self.client[db_name]
            collection = db[collection_name]
            return collection.save(document)
        except (errors.ServerSelectionTimeoutError, errors.NetworkTimeout, errors.ConnectionFailure, TypeError) as e:
            raise e

    def find_document(self, db_name: str, collection_name: str):
        try:
            db = self.client[db_name]
            collection = db[collection_name]
            return collection.find()
        except (errors.ServerSelectionTimeoutError, errors.NetworkTimeout, errors.ConnectionFailure, TypeError) as e:
            raise e


if __name__ == "__main__":
    conn = MongoDBConnection('localhost', 27017)
    conn.test_connection('ri_logging')
