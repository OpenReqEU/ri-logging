# dependencies
import microservice as rilogging
from microservice .lib.messages import RiLoggingError
from microservice .lib.configuration_validator import RiLoggingConfigurationValidator
import sys
import os
import json

# running validation and starting up
if __name__ == '__main__':
    status_code = 0
    # validate the given configuration for existence and type
    if len(sys.argv) < 2:
        status_code = 1
    if status_code == 0 and os.path.isfile(sys.argv[1]) is not True:
        status_code = 2
    if status_code == 0 and os.path.splitext(sys.argv[1])[1] != ".json":
        status_code = 3

    # validate the content of configuration
    configuration = None
    if status_code == 0:
        try:
            configuration = json.loads(open(sys.argv[1], "r").read())
        except json.JSONDecodeError as error:
            status_code = 4
        except TypeError as error:
            status_code = 5
    if status_code == 0 and type(configuration) is not dict:
        status_code = 6

    # validate the configuration structure
    if status_code == 0:
        validator = RiLoggingConfigurationValidator(configuration=configuration)
        validator.validate_strucutre()
        if len(validator.errors) > 0:
            status_code = 7
            for error in validator.errors:
                print(RiLoggingError.error_message(status_code=error.get("error"), prefix="Error", placeholder=error.get("placeholder")))
        if len(validator.warnings) > 0:
            for warning in validator.warnings:
                print(RiLoggingError.error_message(status_code=warning.get("warning"), prefix="Warning", placeholder=warning.get("placeholder")))

    # execute the script since everything is okey or abort
    if status_code == 0:
        rilogging.start(configuration)
    else:
        print(RiLoggingError.error_message(status_code=status_code))
