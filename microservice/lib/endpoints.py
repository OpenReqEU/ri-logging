# dependencies
from microservice.lib.request_handler import RiLoggingRequestHandler
from flask import Flask, Response, request
from flask_cors import CORS
import json
import os
import sys

# initializing the handler
logging_handler = Flask("RiLoggingHandler")
if len(sys.argv) >= 4 and sys.argv[3] is not None and str(sys.argv[3]) == "true":
    directoryLib = os.path.dirname(os.path.realpath(__file__))
    directoryMicroservice = os.path.join(directoryLib, "..")
    filename = os.path.join(directoryMicroservice, 'coverage-reports')
    for file in os.listdir(filename):
        logging_handler.logger.info(file)

# initializing routing
cors = CORS(logging_handler, resources={r'/*': {"origins": '*'}})

RiLoggingRequestHandler.logging_handler = logging_handler


# routes which are redirected into the handler
@logging_handler.route("/mysql_tables", methods=['GET'])
def create_mysql_tables():
    response_body = RiLoggingRequestHandler.create_mysql_tables()
    response_code = RiLoggingRequestHandler.get_response_code(response_body=response_body)

    response = Response(response=json.dumps(response_body), status=response_code, mimetype=RiLoggingRequestHandler.response_mimetype_default)
    return response

# saves the log into specific database
@logging_handler.route("/log", methods=['POST'])
def create_log():
    response_body = RiLoggingRequestHandler.create_log(request_json=request.get_json())
    response_code = RiLoggingRequestHandler.get_response_code(response_body=response_body)

    response = Response(response=json.dumps(response_body), status=response_code, mimetype=RiLoggingRequestHandler.response_mimetype_default)
    return response


# respondes to options request in case the logging receiver is having different host than the sender
@logging_handler.route("/log", methods=['OPTIONS'])
def request_options():
    response = Response(response=json.dumps(RiLoggingRequestHandler.get_response_default()), status=RiLoggingRequestHandler.response_status_ok, mimetype=RiLoggingRequestHandler.response_mimetype_default)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


# returns the given frontend configuration which was used to start the server
@logging_handler.route("/frontend_configuration", methods=["GET"])
def frontend_configuration():
    response = Response(response=json.dumps(RiLoggingRequestHandler.configuration.get("logging").get("frontend")), status=RiLoggingRequestHandler.response_status_ok, mimetype=RiLoggingRequestHandler.response_mimetype_default)
    return response


logging_handler.run(host=RiLoggingRequestHandler.configuration["logging"]["backend"]["server"]["host"], port=int(RiLoggingRequestHandler.configuration["logging"]["backend"]["server"]["port"]))