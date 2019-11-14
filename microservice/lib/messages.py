# all kinds of error messages, that will be used in this module
class RiLoggingError:
    def __init__(self):
        self.configuration_not_given = "Configuration file wasn't given, please pass the location of the configuration file"
        self.configuration_doesnt_exist = "The given location of the configuration file doesn't exist"
        self.configuration_file_type = "The given configuration file is not an JSON Object, please check the example"

        self.configuration_encoding = "The file is invalid JSON or is in UTF-8 BOM, which is not allowed. Please validate the file and use UTF-8 without BOM"
        self.configuration_content = "The content of the configuration file is not a string"
        self.configuration_type = "The configuration should be an JSON object"
        self.configuration_structure = "The structure of the configuration file is invalid or incomplete"

        self.connection_adapter = "The connection adapter couldn't establish connection, please check the configuration"
        self.connection_mysql = "The connection to MySQL server couldn't be established, please check the configuration"

        self.configuration_structure_connection = "The configuration should contain 'connection' property which is a dictionary"

        self.configuration_structure_connection_server = "The 'connection' dictionary should contain 'server' property which is a dictionary"
        self.configuration_structure_connection_server_host = "The 'server' dictionary should contain 'host' property which is a string and not empty"
        self.configuration_structure_connection_server_port = "The 'server' dictionary should contain 'port' property which is a positive integer value"
        self.configuration_structure_connection_server_type = "The 'server' dictionary should contain 'type' property which is a string and not empty"
        self.configuration_structure_connection_server_type_selection = "The 'server' dictionary should contain 'type' property which is a string and ether 'mysql' or 'mongodb'"
        self.configuration_structure_connection_server_database = "The 'server' dictionary should contain 'database' property which is a dictionary"
        self.configuration_structure_connection_server_database_name = "The 'database' dictionary should contain 'name' property which is a string and not empty"
        self.configuration_structure_connection_server_database_create_collection = "The 'database' dictionary should contain 'create_collection' property which is a bool"
        self.configuration_structure_connection_server_database_map = "The 'database' dictionary should contain 'map' property which is a list and not empty"
        self.configuration_structure_connection_server_database_map_information = "The dictionary on index [index] in the 'map' list should have property 'information' which is a string and not empty."
        self.configuration_structure_connection_server_database_map_collection = "The dictionary on index [index] in the 'map' list should have property 'collection' which is a string and not empty"

        self.configuration_structure_connection_user = "The 'connection' dictionary should contain 'user' property which is a dictionary"
        self.configuration_structure_connection_user_name = "The 'user' dictionary should contain 'name' property which is a string and not empty"
        self.configuration_structure_connection_user_password = "The 'user' dictionary should contain 'password' property which is a string and not empty"

        self.configuration_structure_logging = "The configuration should contain 'logging' property which is a dictionary"

        self.configuration_structure_logging_backend = "The 'logging' dictionary should contain 'backend' property which is a dictionary"
        self.configuration_structure_logging_backend_server = "The 'backend' dictionary should contain 'server' property which is a dictionary"
        self.configuration_structure_logging_backend_server_host = "The 'server' dictionary should contain 'host' property which is a string and not empty"
        self.configuration_structure_logging_backend_server_port = "The 'server' dictionary should contain 'port' property which is a positive integer value"

        self.configuration_structure_logging_frontend = "The 'logging' dictionary should contain 'frontend' property which is a dictionary"
        self.configuration_structure_logging_frontend_receiver = "The 'frontend' dictionary should contain 'receiver' property which is a string and not empty"
        self.configuration_structure_logging_frontend_debug = "The 'frontend' dictionary should contain 'debug' property which is a dictionary"
        self.configuration_structure_logging_frontend_debug_enabled = "The 'debug' dictionary should contain 'enabled' property which is a bool"
        self.configuration_structure_logging_frontend_debug_console = "The 'debug' dictionary should contain 'console' property which is a dictionary"
        self.configuration_structure_logging_frontend_debug_console_date = "The 'console' dictionary should contain 'date' property which is a bool"
        self.configuration_structure_logging_frontend_debug_console_class = "The 'console' dictionary should contain 'class' property which is a bool"
        self.configuration_structure_logging_frontend_targets = "The 'frontend' dictionary should contain 'targets' property which is a list and not empty"

        self.configuration_structure_logging_frontend_targets_bound = "The 'target' dictionary on position [index] contains optional 'bound' property which is not a bool"
        self.configuration_structure_logging_frontend_targets_name = "The 'target' dictionary on position [index] should contain 'name' property which is a string and not empty"
        self.configuration_structure_logging_frontend_targets_type = "The 'target' dictionary on position [index] should contain 'type' property which is a string and not empty"
        self.configuration_structure_logging_frontend_targets_type_enum = "The 'target' dictionary on position [index] contains 'type' property which is not equal to 'mouse' or 'keyboard'"
        self.configuration_structure_logging_frontend_targets_key = "The 'target' dictionary on position [index] should contain 'key' property which is a positive number and matches the JQuery definitions of keyboard key"
        self.configuration_structure_logging_frontend_targets_key_alt = "The 'target' dictionary on position [index] should contain 'key_alt' property which is a bool"
        self.configuration_structure_logging_frontend_targets_key_shift = "The 'target' dictionary on position [index] should contain 'key_shift' property which is a bool"
        self.configuration_structure_logging_frontend_targets_category = "The 'target' dictionary on position [index] should contain 'category' property which is a string and not empty"
        self.configuration_structure_logging_frontend_targets_selector = "The 'target' dictionary on position [index] should contain 'selector' property which is a string and not empty"
        self.configuration_structure_logging_frontend_targets_delayed = "The 'target' dictionary on position [index] contains 'delayed' property which is not a bool"
        self.configuration_structure_logging_frontend_targets_information = "The 'target' dictionary on position [index] contains 'information' property which is not a string"
        self.configuration_structure_logging_frontend_targets_information_required = "The 'target' dictionary on position [index] should contain required 'information' property which is a string and not empty"
        self.configuration_structure_logging_frontend_targets_information_undefined = "The 'target' dictionary on position [index] should contain required 'information' property which is defined as property 'id' in 'information' dictionary"
        self.configuration_structure_logging_frontend_targets_targets = "The 'target' dictionary on position [index] contains optional 'targets' property which is not a list or add 'information' property to the target dictionary to track the target"
        self.configuration_structure_logging_frontend_targets_targets_datatype = "The 'target' dictionary on position [index] contains 'information' property which is not a string which is not a string"
        self.configuration_structure_logging_frontend_targets_targets_reference = "The 'targets' list of 'target' dictionary on positon [index] contains a value on position [index_subtarget] which is not matching with the 'name' property of any target dictionary"

        self.configuration_structure_logging_frontend_information = "The 'frontend' dictionary should contain 'information' property which is a list and not empty"
        self.configuration_structure_logging_frontend_information_id = "The 'information' dictionary on position [index] should contain 'id' property which is a string and not empty"
        self.configuration_structure_logging_frontend_information_id_unused = "The 'information' dictionary on position [index] is not used in any target"
        self.configuration_structure_logging_frontend_information_target_name = "The 'information' dictionary on position [index] should contain 'target_name' property which is a string and not empty"
        self.configuration_structure_logging_frontend_information_timestamp_name = "The 'information' dictionary on position [index] should contain 'timestamp_name' property which is a string and not empty"
        self.configuration_structure_logging_frontend_information_header = "The 'information' dictionary on position [index] contains optional 'header' property which is not a list"
        self.configuration_structure_logging_frontend_information_fields = "The 'information' dictionary on position [index] contains optional 'fields' property which is not a list"

        self.configuration_structure_logging_frontend_selection_object_name = "The 'selection_object' dictionary on position [index] in the '[object]' list of information on position [information_index] should contain 'name' property which is a string and not empty"
        self.configuration_structure_logging_frontend_selection_object_source = "The 'selection_object' dictionary on position [index] in the '[object]' list of information on position [information_index] should contain 'source' property which is a string and not empty"
        self.configuration_structure_logging_frontend_selection_object_value = "The 'selection_object' dictionary on position [index] in the '[object]' list of information on position [information_index] should contain 'value' property which is a string and not empty"
        self.configuration_structure_logging_frontend_selection_object_value_date = "The 'selection_object' dictionary on position [index] in the '[object]' list of information on position [information_index] should contain 'value' property which is a string and not empty, or it should be defined the property 'get' to use a function"
        self.configuration_structure_logging_frontend_selection_object_get = "The 'selection_object' dictionary on position [index] in the '[object]' list of information on position [information_index] contains 'get' property which is not a string or is empty"
        self.configuration_structure_logging_frontend_selection_object_parameter = "The 'selection_object' dictionary on position [index] in the '[object]' list of information on position [information_index] contains 'parameter' property which is not a string or is empty"
        self.configuration_structure_logging_frontend_selection_object_divisor = "The 'selection_object' dictionary on position [index] in the '[object]' list of information on position [information_index] contains 'divisor' property which is not a string or is empty"
        self.configuration_structure_logging_frontend_selection_object_split = "The 'selection_object' dictionary on position [index] in the '[object]' list of information on position [information_index] contains 'split' property which is not a string or is empty"
        self.configuration_structure_logging_frontend_selection_object_position = "The 'selection_object' dictionary on position [index] in the '[object]' list of information on position [information_index] contains 'position' property which is not a string or is empty"
        self.configuration_structure_logging_frontend_selection_object_datatype = "The 'selection_object' dictionary on position [index] in the '[object]' list of information on position [information_index] should contain 'datatype' property which is a string, is not empty and is one of the values 'string', 'integer' or 'float'. Missing parameter will result in default value 'string'"

        self.unknown_error = "Unknown error occurred"

    @classmethod
    def error_message(cls, status_code: int, prefix: str = "Abort with error", placeholder: dict = {}):
        messages_object = RiLoggingError()
        messages = {
            1: messages_object.configuration_not_given,
            2: messages_object.configuration_doesnt_exist,
            3: messages_object.configuration_file_type,
            4: messages_object.configuration_encoding,
            5: messages_object.configuration_content,
            6: messages_object.configuration_type,
            7: messages_object.configuration_structure,
            8: messages_object.connection_adapter,

            10: messages_object.configuration_structure_connection,
            101: messages_object.configuration_structure_connection_server,
            1011: messages_object.configuration_structure_connection_server_host,
            1012: messages_object.configuration_structure_connection_server_port,
            1013: messages_object.configuration_structure_connection_server_type,
            10131: messages_object.configuration_structure_connection_server_type_selection,
            1014: messages_object.configuration_structure_connection_server_database,
            10141: messages_object.configuration_structure_connection_server_database_name,
            10142: messages_object.configuration_structure_connection_server_database_create_collection,
            10143: messages_object.configuration_structure_connection_server_database_map,
            101431: messages_object.configuration_structure_connection_server_database_map_information,
            101432: messages_object.configuration_structure_connection_server_database_map_collection,

            102: messages_object.configuration_structure_connection_user,
            1021: messages_object.configuration_structure_connection_user_name,
            1022: messages_object.configuration_structure_connection_user_password,

            20: messages_object.configuration_structure_logging,
            201: messages_object.configuration_structure_logging_backend,
            2011: messages_object.configuration_structure_logging_backend_server,
            20111: messages_object.configuration_structure_logging_backend_server_host,
            20112: messages_object.configuration_structure_logging_backend_server_port,

            202: messages_object.configuration_structure_logging_frontend,
            2021: messages_object.configuration_structure_logging_frontend_receiver,
            2022: messages_object.configuration_structure_logging_frontend_debug,
            20221: messages_object.configuration_structure_logging_frontend_debug_enabled,
            20222: messages_object.configuration_structure_logging_frontend_debug_console,
            202221: messages_object.configuration_structure_logging_frontend_debug_console_date,
            202222: messages_object.configuration_structure_logging_frontend_debug_console_class,
            2023: messages_object.configuration_structure_logging_frontend_targets,
            20231: messages_object.configuration_structure_logging_frontend_targets_bound,
            20232: messages_object.configuration_structure_logging_frontend_targets_name,
            20233: messages_object.configuration_structure_logging_frontend_targets_type,
            202331: messages_object.configuration_structure_logging_frontend_targets_type_enum,
            20234: messages_object.configuration_structure_logging_frontend_targets_key,
            202341: messages_object.configuration_structure_logging_frontend_targets_key_alt,
            202342: messages_object.configuration_structure_logging_frontend_targets_key_shift,
            20235: messages_object.configuration_structure_logging_frontend_targets_category,
            20236: messages_object.configuration_structure_logging_frontend_targets_selector,
            20237: messages_object.configuration_structure_logging_frontend_targets_information,
            202361: messages_object.configuration_structure_logging_frontend_targets_information_required,
            202362: messages_object.configuration_structure_logging_frontend_targets_information_undefined,
            20238: messages_object.configuration_structure_logging_frontend_targets_targets,
            202371: messages_object.configuration_structure_logging_frontend_targets_targets_datatype,
            202372: messages_object.configuration_structure_logging_frontend_targets_targets_reference,
            2024: messages_object.configuration_structure_logging_frontend_information,
            20241: messages_object.configuration_structure_logging_frontend_information_id,
            202411: messages_object.configuration_structure_logging_frontend_information_id_unused,
            20242: messages_object.configuration_structure_logging_frontend_information_target_name,
            20243: messages_object.configuration_structure_logging_frontend_information_timestamp_name,
            20244: messages_object.configuration_structure_logging_frontend_information_header,
            20245: messages_object.configuration_structure_logging_frontend_information_fields,
            202461: messages_object.configuration_structure_logging_frontend_selection_object_name,
            202462: messages_object.configuration_structure_logging_frontend_selection_object_source,
            202463: messages_object.configuration_structure_logging_frontend_selection_object_value,
            2024631: messages_object.configuration_structure_logging_frontend_selection_object_value_date,
            202464: messages_object.configuration_structure_logging_frontend_selection_object_get,
            202465: messages_object.configuration_structure_logging_frontend_selection_object_parameter,
            202466: messages_object.configuration_structure_logging_frontend_selection_object_divisor,
            202467: messages_object.configuration_structure_logging_frontend_selection_object_split,
            202468: messages_object.configuration_structure_logging_frontend_selection_object_position,
            202469: messages_object.configuration_structure_logging_frontend_selection_object_datatype,


            99: messages_object.unknown_error
        }
        if len(prefix) > 0:
            prefix += " "
        else:
            prefix = ""

        error_message = prefix + str(status_code) + " : " + messages.get(status_code, messages.get(99))

        keys = sorted(placeholder.keys())
        for key in keys:
            error_message = error_message.replace("[" + key + "]", str(placeholder.get(key)))

        return error_message
