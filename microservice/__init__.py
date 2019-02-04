import ast
import json
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, Response, request
from flask_cors import CORS

from . import auth, util, frontend_logging, backend_logging

root_path = os.path.abspath(os.path.join(__file__, '..', '..'))


def create_app(config_file_name: str = 'config.json'):
    # TODO: Use connexion framework
    app = Flask(__name__)

    # Load config file
    __init_config(app, config_file_name)
    # Config the logging handler to log the internal activities to a file in the diractory specified by the config.
    __init_debug_logging(app.config['LOGGING_LEVEL'], app.config['DIR_DEBUG_LOG'])

    # Blueprint must be initialized with the CORS handler BEFORE the registration with the app
    CORS(frontend_logging.api)
    CORS(backend_logging.api)

    # Register Blueprints after CORS initialization
    app.register_blueprint(frontend_logging.api)
    app.register_blueprint(backend_logging.api)

    # Init auth
    auth.init_auth(app.config['API_BEARER_TOKEN'])

    # Register generic error handlers
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def handle_error(e):
        split = str(e).split(': ')
        status = int(split[0].split(' ')[0])
        message = split[1]
        app.logger.info(f'Request from {request.remote_addr} returned {split[0]}')
        return Response(status=status, response=json.dumps({'message': message}), mimetype='text/plain')

    return app


def __init_debug_logging(logging_level: str = 'NOTSET', log_path: str = os.path.join(root_path, 'debug_logs')):
    """
    Create a logging handler with the specified logging level, outputting the logfile to a specified path.
    :param logging_level: The logging level.
    :param log_path: The directory path where to put the log file.
    :return: RotatingFileHandler
    """
    logging_levels = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET
    }

    # Create internal log directory in the configured directory
    try:
        os.makedirs(log_path)
    except PermissionError:
        logging.warning('No permission to init debug logging.')
    except FileExistsError:
        # If file exists already do nothing
        pass

    debug_log_file_path = os.path.join(log_path, 'debug.log')
    formatter = logging.Formatter("[%(asctime)s] {%(levelname)s - %(message)s")
    handler = RotatingFileHandler(debug_log_file_path, maxBytes=100 * 1024 * 1024, backupCount=1)
    handler.setLevel(logging_levels[logging_level])
    handler.setFormatter(formatter)
    return handler


def __init_config(app, config_file_name: str):
    """
    Initialize the config.json file in the project root from environment variables,
    if it doesn't exist and load it into the app.
    :param app: The flask app to be configured.
    :return: None
    """
    final_config_path = os.path.join(root_path, config_file_name)
    # If config.json file doesn't exist create it with values from the env vars.
    if not os.path.isfile(final_config_path):
        base_config_path = os.path.join(root_path, 'config_base.json')
        base_config = util.read_file(os.path.abspath(base_config_path))
        base_config = json.loads(base_config)
        for key, val in base_config.items():
            env_var = os.environ[key]
            if env_var == 'True' or env_var == 'False':
                val = ast.literal_eval(env_var)
            else:
                val = env_var
            base_config[key] = val

        final_config = json.dumps(base_config)
        util.write_file(final_config_path, final_config)

    app.config.from_json(final_config_path)
    return None
