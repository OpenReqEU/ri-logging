# validates the given configuration
class RiLoggingConfigurationValidator:
    # saves the full configuration
    configuration: dict = None
    # saves the errors which occurred while validating
    errors: list = []
    # saves warnings which occurred while validating
    warnings: list = []
    # enum value for possible connections
    server_type_mysql: str = "mysql"
    server_type_mongodb: str = "mongodb"
    # enum values for possible additional validation procedures
    validator_additional_positive = "positive"
    validator_additional_not_empty = "not_empty"

    @classmethod
    # sets the configuration for the instance
    def __init__(cls, configuration):
        cls.configuration = configuration

    @classmethod
    # validates the given property of an object with given approach
    def validate_value(cls, dict_object: dict, dict_key: str, check_type=None, error: int = -1, additional: str = "", index: int = -1, placeholders: list = []):
        is_valid = True
        keys = sorted(dict_object.keys())

        try:
            keys.index(dict_key)
        except ValueError:
            is_valid = False
        else:
            # datatype validation
            if check_type is not None:
                if type(dict_object.get(dict_key)) is not check_type:
                    is_valid = False

                if is_valid is True and (check_type is int or check_type is float):
                    if additional == RiLoggingConfigurationValidator.validator_additional_positive and (check_type is int and dict_object.get(dict_key) < 0 or check_type is float and dict_object.get(dict_key) < 0.0):
                        is_valid = False
                    if additional == RiLoggingConfigurationValidator.validator_additional_not_empty and (check_type is int and dict_object.get(dict_key) == 0 or check_type is float and dict_object.get(dict_key) == 0.0):
                        is_valid = False

                if is_valid is True and (check_type is str or check_type is list):
                    if additional == RiLoggingConfigurationValidator.validator_additional_not_empty and len(dict_object.get(dict_key)) == 0:
                        is_valid = False

        # if validation failed, log as error
        if is_valid is False and error >= 0:
            placeholder = {}
            for placeholder_given in placeholders:
                placeholder.__setitem__(placeholder_given.get("name"), placeholder_given.get("value"))
            if index >= 0:
                placeholder.__setitem__("index", index)
            cls.errors.append({"error": error, "placeholder": placeholder})

        return is_valid

    @classmethod
    # validates the configuration
    def validate_strucutre(cls):
        if cls.validate_value(dict_object=cls.configuration, dict_key="connection", check_type=dict, error=10) is True:
            cls.validate_connection(connection=cls.configuration.get("connection"))

        if cls.validate_value(dict_object=cls.configuration, dict_key="logging", check_type=dict, error=20) is True:
            cls.validate_logging(logging=cls.configuration.get("logging"))

    @classmethod
    # validates the connection dictionary in the configuration
    def validate_connection(cls, connection: dict):
        if cls.validate_value(dict_object=connection, dict_key="server", check_type=dict, error=101) is True:
            cls.validate_connection_server(server=connection.get("server"))
            if cls.validate_value(dict_object=connection.get("server"), dict_key="type", check_type=str, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
                if connection.get("server").get("type") == RiLoggingConfigurationValidator.server_type_mysql:
                    if cls.validate_value(dict_object=connection, dict_key="user", check_type=dict, error=102) is True:
                        cls.validate_connection_user(user=connection.get("user"))

    @classmethod
    # validates the server dictionary in the connection dictionary
    def validate_connection_server(cls, server: dict):
        cls.validate_value(dict_object=server, dict_key="host", check_type=str, error=1011, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)
        cls.validate_value(dict_object=server, dict_key="port", check_type=int, error=1012, additional=RiLoggingConfigurationValidator.validator_additional_positive)
        if cls.validate_value(dict_object=server, dict_key="type", check_type=str, error=1013, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
            cls.validate_value(dict_object={RiLoggingConfigurationValidator.server_type_mysql: 1, RiLoggingConfigurationValidator.server_type_mongodb: 1}, dict_key=server.get("type"), check_type=int, error=10131)
        if cls.validate_value(dict_object=server, dict_key="database", check_type=dict, error=1014) is True:
            cls.validate_connection_server_database(database=server.get("database"), error_base=10140)

    @classmethod
    # validates the database dictionary in the server dictionary
    def validate_connection_server_database(cls, database: dict, error_base: int):
        cls.validate_value(dict_object=database, dict_key="name", check_type=str, error=error_base + 1, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)
        cls.validate_value(dict_object=database, dict_key="create_collection", check_type=bool, error=error_base + 2)
        if cls.validate_value(dict_object=database, dict_key="map", check_type=list, error=error_base + 3, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
            for database_map in database.get("map"):
                cls.validate_connection_server_database_map(database_map=database_map, index=database.get("map").index(database_map), error_base=(error_base + 3) * 10)

    @classmethod
    # validates the database_map dictionary in the map list
    def validate_connection_server_database_map(cls, database_map: dict, index: int, error_base: int):
        cls.validate_value(dict_object=database_map, dict_key="information", check_type=str, error=error_base + 1, additional=RiLoggingConfigurationValidator.validator_additional_not_empty, index=index)
        cls.validate_value(dict_object=database_map, dict_key="collection", check_type=str, error=error_base + 2, additional=RiLoggingConfigurationValidator.validator_additional_not_empty, index=index)

    @classmethod
    # validates the user dictionary in the connection dictionary
    def validate_connection_user(cls, user: dict):
        cls.validate_value(dict_object=user, dict_key="name", check_type=str, error=1021)
        cls.validate_value(dict_object=user, dict_key="password", check_type=str, error=1022)

    @classmethod
    # validates the logging dictionary in the configuration
    def validate_logging(cls, logging: dict):
        if cls.validate_value(dict_object=logging, dict_key="backend", check_type=dict, error=201) is True:
            cls.validate_logging_backend(backend=logging.get("backend"))
        if cls.validate_value(dict_object=logging, dict_key="frontend", check_type=dict, error=202) is True:
            cls.validate_logging_frontend(frontend=logging.get("frontend"))

    @classmethod
    # validates the backend dictionary in the logging dictionary
    def validate_logging_backend(cls, backend: dict):
        if cls.validate_value(dict_object=backend, dict_key="server", check_type=dict, error=2011) is True:
            cls.validate_logging_backend_server(server=backend.get("server"))

    @classmethod
    # validates the server dictionary in the backend dictionary
    def validate_logging_backend_server(cls, server: dict):
        cls.validate_value(dict_object=server, dict_key="host", check_type=str, error=20111, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)
        cls.validate_value(dict_object=server, dict_key="port", check_type=int, error=20112, additional=RiLoggingConfigurationValidator.validator_additional_positive)

    @classmethod
    # validates the frontend dictionary in the logging dictionary
    def validate_logging_frontend(cls, frontend: dict):
        cls.validate_value(dict_object=frontend, dict_key="receiver", check_type=str, error=2021, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)
        if cls.validate_value(dict_object=frontend, dict_key="debug", check_type=dict, error=2022) is True:
            cls.validate_logging_frontend_debug(debug=frontend.get("debug"), error_base=20220)

        if cls.validate_value(dict_object=frontend, dict_key="targets", check_type=list, error=2023, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
            for target in frontend.get("targets"):
                cls.validate_logging_frontend_target(target=target, index=frontend.get("targets").index(target), error_base=20230, frontend=frontend)
        if cls.validate_value(dict_object=frontend, dict_key="information", check_type=list, error=2024, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
            for information in frontend.get("information"):
                cls.validate_logging_frontend_information(information=information, informations=frontend.get("information"), frontend=frontend, index=frontend.get("information").index(information), error_base=20240)

    @classmethod
    # validates the debug dictionary in the frontend dictionary
    def validate_logging_frontend_debug(cls, debug: dict, error_base: int):
        cls.validate_value(dict_object=debug, dict_key="enabled", check_type=bool, error=error_base + 1)
        if cls.validate_value(dict_object=debug, dict_key="console", check_type=dict, error=error_base + 2) is True:
            cls.validate_logging_frontend_debug_console(console=debug.get("console"), error_base=(error_base + 2) * 10)

    @classmethod
    # validates the console dictionary in the debug dictionary
    def validate_logging_frontend_debug_console(cls, console: dict, error_base: int):
        cls.validate_value(dict_object=console, dict_key="date", check_type=bool, error=error_base + 1)
        cls.validate_value(dict_object=console, dict_key="class", check_type=bool, error=error_base + 2)

    @classmethod
    # validates the target dictionary in the targets list of frontend dictionary
    def validate_logging_frontend_target(cls, target: dict, index: int, error_base: int, frontend: dict):
        if cls.validate_value(dict_object=target, dict_key="bound") is True:
            cls.validate_value(dict_object=target, dict_key="bound", check_type=bool, error=error_base + 1, index=index)
        cls.validate_value(dict_object=target, dict_key="name", check_type=str, error=error_base + 2, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)

        if cls.validate_value(dict_object=target, dict_key="type", check_type=str, error=error_base + 3, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
            cls.validate_value(dict_object={"mouse": 1, "keyboard": 1}, dict_key=target.get("type"), check_type=int, error=(error_base + 3) * 10 + 1)

            if cls.validate_value(dict_object={"keyboard": 1}, dict_key=target.get("type"), check_type=int) is True:
                cls.validate_value(dict_object=target, dict_key="key", check_type=int, error=error_base + 4, index=index, additional=RiLoggingConfigurationValidator.validator_additional_positive)
                if cls.validate_value(dict_object=target, dict_key="key_alt") is True:
                    cls.validate_value(dict_object=target, dict_key="key_alt", index=index, check_type=bool, error=(error_base + 4) * 10 + 1)
                if cls.validate_value(dict_object=target, dict_key="key_shift") is True:
                    cls.validate_value(dict_object=target, dict_key="key_shift", index=index, check_type=bool, error=(error_base + 4) * 10 + 2)

        cls.validate_value(dict_object=target, dict_key="category", check_type=str, error=error_base + 5, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)
        cls.validate_value(dict_object=target, dict_key="selector", check_type=str, error=error_base + 6, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)
        if cls.validate_value(dict_object=target, dict_key="delayed") is True:
            cls.validate_value(dict_object=target, dict_key="delayed", check_type=bool, error=error_base + 8, index=index)

        validate_subtargets = False
        # information is only required if targets is not list of string
        if cls.validate_value(dict_object=target, dict_key="information") is True:
            cls.validate_value(dict_object=target, dict_key="information", check_type=str, error=error_base + 7, index=index)
            # if targets are defined, then information is not needed but optional
            if cls.validate_value(dict_object=target, dict_key="targets", check_type=list, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
                validate_subtargets = True
            # information is required, since the target is not used as trigger
            else:
                cls.validate_value(dict_object=target, dict_key="information", check_type=str, error=(error_base + 7) * 10 + 1, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)
                if cls.validate_value(dict_object=frontend, dict_key="information", check_type=list, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
                    informations = {}
                    for information in frontend.get("information"):
                        if cls.validate_value(dict_object=information, dict_key="id", check_type=str, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
                            informations.__setitem__(information.get("id"), 1)
                    cls.validate_value(dict_object=informations, dict_key=target.get("information"), check_type=int, error=(error_base + 7) * 10 + 2, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)

        else:
            validate_subtargets = True

        if validate_subtargets is True:
            if cls.validate_value(dict_object=target, dict_key="targets", check_type=list, error=error_base + 7, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
                for subtarget in target.get("targets"):
                    cls.validate_logging_frontend_target_target(target={"subtarget": subtarget}, target_parent=target, error_base=(error_base + 7) * 10, targets=frontend.get("targets"))

    @classmethod
    # validates the target string in the subtargets list of target dictionary
    def validate_logging_frontend_target_target(cls, target: dict, target_parent: dict, targets: list, error_base: int):
        placeholders = [{"name": "index", "value": targets.index(target_parent)}, {"name": "index_subtarget", "value": target_parent.get("targets").index(target.get("subtarget"))}]
        if cls.validate_value(dict_object=target, dict_key="subtarget", check_type=str, error=error_base + 1, additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders) is True:
            targets_dictionary = {}
            for target_main in targets:
                targets_dictionary.__setitem__(target_main.get("name"), 1)
            placeholders = [{"name": "index", "value": targets.index(target_parent)}, {"name": "index_subtarget", "value": target_parent.get("targets").index(target.get("subtarget"))}]
            cls.validate_value(dict_object=targets_dictionary, dict_key=target.get("subtarget"), check_type=int, error=error_base + 2, additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders)

    @classmethod
    # validates the information dictionary in the frontend dictionary
    def validate_logging_frontend_information(cls, information: dict, informations: list, frontend: dict, index: int, error_base: int):
        if cls.validate_value(dict_object=information, dict_key="id", check_type=str, error=error_base + 1, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
            if cls.validate_value(dict_object=frontend, dict_key="targets", check_type=list, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
                targets = {}
                for target in frontend.get("targets"):
                    if cls.validate_value(dict_object=target, dict_key="information", check_type=str, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
                        targets.__setitem__(target.get("information"), 1)
                if cls.validate_value(dict_object=targets, dict_key=information.get("id"), check_type=int, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is False:
                    placeholders_warning = {"index": index}
                    cls.warnings.append({"warning": (error_base + 1) * 10 + 1, "placeholder": placeholders_warning})

        cls.validate_value(dict_object=information, dict_key="target_name", check_type=str, error=error_base + 2, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)
        cls.validate_value(dict_object=information, dict_key="timestamp_name", check_type=str, error=error_base + 3, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty)
        if cls.validate_value(dict_object=information, dict_key="header") is True:
            cls.validate_value(dict_object=information, dict_key="header", check_type=list, error=error_base + 4, index=index)
        if cls.validate_value(dict_object=information, dict_key="fields") is True:
            cls.validate_value(dict_object=information, dict_key="fields", check_type=list, error=error_base + 5, index=index)
            if cls.validate_value(dict_object=information, dict_key="id", check_type=str, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
                for list_type in ["header", "fields"]:
                    if cls.validate_value(dict_object=information, dict_key=list_type, check_type=list, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
                        for selection_object in information.get(list_type):
                            cls.validate_logging_frontend_information_selection_object(selection_object=selection_object, object_type=list_type, information_index=informations.index(information), index=information.get(list_type).index(selection_object), error_base=(error_base + 6) * 10)

    @classmethod
    # validates the selection_target dictionary in ether header list or in the fields list of the information dictionary
    def validate_logging_frontend_information_selection_object(cls, selection_object: dict, object_type: str, information_index, index: int, error_base: int):
        placeholders = [{"name": "object", "value": object_type}, {"name": "index", "value": index}, {"name": "information_index", "value": information_index}]
        cls.validate_value(dict_object=selection_object, dict_key="name", check_type=str, error=error_base+1, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders)
        cls.validate_value(dict_object=selection_object, dict_key="source", check_type=str, error=error_base+2, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders)

        if cls.validate_value(dict_object=selection_object, dict_key="source") is True:
            if cls.validate_value(dict_object={"date": 1}, dict_key=selection_object.get("source"), check_type=int) is True:
                if cls.validate_value(dict_object=selection_object, dict_key="get", check_type=str, additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders) is False:
                    cls.validate_value(dict_object=selection_object, dict_key="value", check_type=str, error=(error_base + 3) * 10 + 1, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders)
            else:
                cls.validate_value(dict_object=selection_object, dict_key="value", check_type=str, error=(error_base + 3), additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders)

        if cls.validate_value(dict_object=selection_object, dict_key="get") is True:
            cls.validate_value(dict_object=selection_object, dict_key="get", check_type=str, error=(error_base + 4), additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders)
            if cls.validate_value(dict_object=selection_object, dict_key="parameter") is True:
                cls.validate_value(dict_object=selection_object, dict_key="parameter", check_type=str, error=(error_base + 5), additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders)

        if cls.validate_value(dict_object=selection_object, dict_key="divisor") is True:
            if cls.validate_value(dict_object=selection_object, dict_key="divisor", check_type=float, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is False:
                cls.validate_value(dict_object=selection_object, dict_key="divisor", check_type=int, error=error_base+6, index=index, additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders)
        if cls.validate_value(dict_object=selection_object, dict_key="split") is True:
            cls.validate_value(dict_object=selection_object, dict_key="split", check_type=str, error=error_base + 7, additional=RiLoggingConfigurationValidator.validator_additional_not_empty, placeholders=placeholders)
            cls.validate_value(dict_object=selection_object, dict_key="position", check_type=int, error=error_base + 8, additional=RiLoggingConfigurationValidator.validator_additional_positive, placeholders=placeholders)

        if cls.validate_value(dict_object=cls.configuration, dict_key="connection", check_type=dict) is True:
            if cls.validate_value(dict_object=cls.configuration.get("connection"), dict_key="server", check_type=dict) is True:
                if cls.validate_value(dict_object=cls.configuration.get("connection").get("server"), dict_key="type", check_type=str, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is True:
                    if cls.configuration.get("connection").get("server").get("type") == RiLoggingConfigurationValidator.server_type_mysql:
                        if cls.validate_value(dict_object=selection_object, dict_key="datatype", check_type=str, additional=RiLoggingConfigurationValidator.validator_additional_not_empty) is False:
                            placeholders_warning = {}
                            for placeholder in placeholders:
                                placeholders_warning.__setitem__(placeholder.get("name"), placeholder.get("value"))
                            cls.warnings.append({"warning": error_base + 9, "placeholder": placeholders_warning})

