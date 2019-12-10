# dependencies
import microservice.lib.messages as message_module
from pymongo import MongoClient


# class for handling the mongodb database
class MongoDBConnection:
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""
    database: str = ""
    connection: MongoClient = None

    @classmethod
    def __init__(cls, host, port, username: str = "", password: str = "", database: str = ""):
        cls.host = host
        cls.port = port
        cls.username = username
        cls.password = password
        cls.database = database

    @classmethod
    # creates new connection
    def create_connection(cls):
        try:
            cls.connection = MongoClient(
                host=cls.host,
                port=cls.port,
                document_class=dict
            )
        except Exception:
            exit(message_module.RiLoggingError.error_message(8))

    @classmethod
    # inserts the dataset, if needed creates the database and the collection
    def insert(cls, logging_data: dict, database_name: str, collection_name: str):
        result = None
        cls.create_connection()
        if cls.connection is not None:
            database = cls.connection[database_name]
            collection = database[collection_name]
            entry_id = collection.save(logging_data)
            result = type(entry_id) is not None

            cls.connection.close()

        return result

