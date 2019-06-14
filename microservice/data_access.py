"""
created at: 2018-12-19
author:     Volodymyr Biryuk

This module provides functionality for database access.
"""
import logging
from pymongo import MongoClient
from pymongo.errors import OperationFailure

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


if __name__ == "__main__":
    pass
