# dependencies
from flask import Flask
from microservice.lib.mysql_query_generator import RiLoggingMySqlQueryCreator
from microservice.connectors.MySQL import MySQLConnection
from microservice.connectors.MongoDB import MongoDBConnection


# class for handling the requests
class RiLoggingRequestHandler:
    # enum value for possible connections
    server_type_mysql: str = "mysql"
    server_type_mongodb: str = "mongodb"
    # full configuration of the tool
    configuration: dict = None
    # request-response-communication
    logging_handler: Flask = None
    # default mime-type for data exchange
    response_mimetype_default: str = "application/json"
    # mime-type for delivering JavaScript file
    response_mimetype_javascript: str = "application/javascript"
    # key for the response to return the textual status
    response_key_message: str = "message"
    # textual response status indicating that everything went ok
    response_message_ok: str = "ok"
    # textual response status indicating that something went wrong
    response_message_error: str = "error"
    # http response status indicating that everything went ok
    response_status_ok: int = 200
    # http response status indicating that something went wrong
    response_status_bad_request: int = 400

    @staticmethod
    # returns the basic response dict which describes the structure of all responses
    def get_response_default() -> dict:
        response_body = {
            RiLoggingRequestHandler.response_key_message: RiLoggingRequestHandler.response_message_ok
        }
        return response_body

    @staticmethod
    # returns the http response code based on the body object
    def get_response_code(response_body: dict) -> int:
        response_code = RiLoggingRequestHandler.response_status_ok
        if type(response_body) is not dict or type(response_body.get("message")) is not str or response_body.get("message") != "ok":
            response_code = RiLoggingRequestHandler.response_status_bad_request

        return response_code

    @staticmethod
    # executive function to generate tables and return the sql strings
    def create_mysql_tables() -> dict:
        response_body = RiLoggingRequestHandler.get_response_default()
        response_body.__setitem__("tables", [])
        for database_map in RiLoggingRequestHandler.configuration.get("connection").get("server").get("database").get("map"):
            for information in RiLoggingRequestHandler.configuration.get("logging").get("frontend").get("information"):
                if database_map.get("information") == information.get("id"):
                    table_sql = RiLoggingMySqlQueryCreator.create_table(database_map.get("collection"), information.get("target_name"), information.get("timestamp_name"), information.get("fields"))
                    response_body.get("tables").append(table_sql)

        if len(response_body.get("tables")) == 0 or len(response_body.get("tables")) != len(RiLoggingRequestHandler.configuration.get("logging").get("frontend").get("information")):
            response_body.__setitem__(RiLoggingRequestHandler.response_key_message, RiLoggingRequestHandler.response_message_error)

        return response_body

    @staticmethod
    # executive function for writing the log to the database
    def create_log(request_json: dict) -> dict:
        save_success = False
        request_database_map = None
        request_information = None
        response_body = RiLoggingRequestHandler.get_response_default()

        for information in RiLoggingRequestHandler.configuration.get("logging").get("frontend").get("information"):
            # find information's where target_name is in request
            if type(request_json.get(information.get("target_name"))) is str:
                # find the right target based on the name of the target
                for target in RiLoggingRequestHandler.configuration.get("logging").get("frontend").get("targets"):
                    # find the target which triggered this request
                    if request_json.get(information.get("target_name")) == target.get("name") and target.get("information") == information.get("id"):
                        request_information = information

                        # find the right database table/collection for the received information
                        for database_map in RiLoggingRequestHandler.configuration.get("connection").get("server").get("database").get("map"):
                            if target.get("information") == database_map.get("information"):
                                request_database_map = database_map

        if request_database_map is not None and request_information is not None:
            server_type = RiLoggingRequestHandler.configuration.get("connection").get("server").get("type")

            if server_type == RiLoggingRequestHandler.server_type_mysql:
                save_success = RiLoggingRequestHandler.create_log_mysql(request_database_map, request_information, request_json)

            if server_type == RiLoggingRequestHandler.server_type_mongodb:
                save_success = RiLoggingRequestHandler.create_log_mongodb(request_database_map, request_json)

        if save_success is False:
            response_body.__setitem__(RiLoggingRequestHandler.response_key_message, RiLoggingRequestHandler.response_message_error)

        return response_body

    @staticmethod
    def create_log_mysql(database_map: dict, information: dict, request: dict) -> bool:
        success = False
        query = RiLoggingMySqlQueryCreator.create_insert_query(database_map.get("collection"), information.get("target_name"), information.get("timestamp_name"), information.get("fields"), request)
        connection = MySQLConnection(
            username=RiLoggingRequestHandler.configuration.get("connection").get("user").get("name"),
            password=RiLoggingRequestHandler.configuration.get("connection").get("user").get("password"),
            host=RiLoggingRequestHandler.configuration.get("connection").get("server").get("host"),
            port=RiLoggingRequestHandler.configuration.get("connection").get("server").get("port"),
            database=RiLoggingRequestHandler.configuration.get("connection").get("server").get("database").get("name")
        )
        try:
            if RiLoggingRequestHandler.configuration.get("connection").get("server").get("database").get("create_collection") is True:
                for database_map in RiLoggingRequestHandler.configuration.get("connection").get("server").get("database").get("map"):
                    if database_map.get("information") == information.get("id"):
                        if connection.table_exists(database_map.get("collection")) is False:
                            table_sql_query = RiLoggingMySqlQueryCreator.create_table(database_map.get("collection"), information.get("target_name"), information.get("timestamp_name"), information.get("fields"))
                            connection.insert_query(query=table_sql_query, database=RiLoggingRequestHandler.configuration.get("connection").get("server").get("database").get("name"))
        except Warning:
            pass

        result = connection.insert_query(query=query, database=RiLoggingRequestHandler.configuration.get("connection").get("server").get("database").get("name"))

        if result == 1:
            success = True

        return success

    @staticmethod
    def create_log_mongodb(database_map, request) -> bool:
        connection = MongoDBConnection(
            host=RiLoggingRequestHandler.configuration.get("connection").get("server").get("host"),
            port=RiLoggingRequestHandler.configuration.get("connection").get("server").get("port")
        )

        success = connection.insert(logging_data=request, database_name=RiLoggingRequestHandler.configuration.get("connection").get("server").get("database").get("name"), collection_name=database_map.get("collection"))

        return success
