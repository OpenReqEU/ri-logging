import pymysql as adapter
import microservice.lib.messages as message_module
from microservice.lib.mysql_query_generator import RiLoggingMySqlQueryCreator


class MySQLConnection:
    host: str = ""
    port: int = 3306
    username: str = ""
    password: str = ""
    database: str = ""
    connection: adapter.connections.Connection = None

    @classmethod
    def __init__(cls, host, port, username, password, database):
        cls.host = host
        cls.port = port
        cls.username = username
        cls.password = password
        cls.database = database
        cls.create_connection()
        if cls.connection is not None:
            cls.connection.select_db(cls.database)

    @classmethod
    def create_connection(cls):
        try:
            cls.connection = adapter.connections.Connection(host=cls.host, port=cls.port, user=cls.username, password=cls.password, database=cls.database)
            cls.connection.connect()
        except Exception:
            exit(message_module.RiLoggingError.error_message(8))

    @classmethod
    def is_connected(cls):
        return cls.connection is not None and cls.connection.open is True

    @classmethod
    def table_exists(cls, table_name: str) -> bool:
        result = False
        if cls.connection is not None:
            cls.connection.select_db(cls.database)
            cursor = cls.connection.cursor()
            result = cursor.execute(query=RiLoggingMySqlQueryCreator.table_exists(table_name=table_name))
            cursor.close()
            
            result = type(result) is int and result == 1

        return result

    @classmethod
    def insert_query(cls, query, database=None):
        result = None
        if cls.connection is not None:
            cls.create_connection()
            if database is not None and cls.database != database:
                cls.database = database
                cls.connection.select_db(cls.database)
            cursor = cls.connection.cursor()
            result = cursor.execute(query=query)
            cursor.close()
            cls.connection.close()
        return result

