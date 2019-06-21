# OpenReq - Improving Requirements Quality  

![EPL 2.0](https://img.shields.io/badge/License-EPL%202.0-blue.svg "EPL 2.0")

This component was created as a result of the OpenReq project funded by the European Union Horizon 2020 Research and 
Innovation programme under grant agreement No 732463.

## Technical Description

This microservice captures implicit feedback on a website (frontend) by tracking and logging user interactions e.g. clicks and on the server (backend).
The frontend module uses a simple JavaScript script to track user interactions.

### Technologies Used

* jQuery (-> https://jquery.com/)
* JavaScript Obfuscator (-> https://github.com/safflower/javascript-obfuscator)

### Requirements

* Python >=3.6 (-> https://www.python.org/)
* MongoDB (-> https://www.mongodb.com/)
* NGINX (-> https://nginx.org/)
* Docker (-> https://www.docker.com/)
* virtualenv (-> https://github.com/pypa/virtualenv)

### Configuration
The microservice can be ran from the shell or in a Docker container that need to be configured differently.
The configuration properties are specified in the `config_base.json`:

```json
{
  "DB_HOST": "<The host of the database e.g. 0.0.0.0>",
  "DB_PORT": "<The port of the databse service as integer>",
  "DB_AUTH_MECHANISM": "<The DB auth mechanism, must be empty if no auth enabled>",
  "DB_AUTH_SOURCE": "<The auth database, empty if no auth enabled>",
  "DB_USER": "<The username for db auth, empty if no auth enabled>",
  "DB_PASSWORD": "<The password for db auth, empty if no auth enabled>",
  "DB_CONNECTION_TIMEOUT": "<The timeout duration for database selection>",
  "DB_NAME_FRONTEND_LOGS": "<The database name where the frontend logs shall be stored>",
  "API_URL": "<The full url of the frontend logging API e.g. http://0.0.0.0:9798/frontend/log>",
  "API_BEARER_TOKEN": "<An alphanumerical Bearer token for the API auth>",
  "DIR_DEBUG_LOG": "",
  "DIR_BACKEND_LOG": "",
  "DEBUG": "<\"True\" if debug should be enabled, \"False\" if debug should be disabled>",
  "LOGGING_LEVEL": "<The logging level CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET for no logging"
}
```

#### Shell

Create a copy of `config_base.json` as `config.json` in the project root directory and fill the attribute values.

#### Docker

1. In the `docker run` command set a -e flag for each property of the `config_base.json`. All attributes are mandatory, optional attributes can have an empty value.

### Installation


#### Shell

For the shell version:

1. Create a virtual environment.
    ```console
    foo@bar:~$ virtualenv venv
    foo@bar:~$ source venv/bin/activate
    ```

2. Install required packages
    ```console
    foo@bar:~$ pip install requirements.txt
    ```

#### Docker

For the dockerized version: With Docker installed on your machine, run the following commands to run the service.
For each property in the base_confg.json the -e flag in Docker:

1. Build:
    1. Without cache, re-installs all packages.
        ```console
        foo@bar:~$ docker build --no-cache -t ri-logging .
        ```

    1. With the previous builds' cache (faster):
        ```console
        foo@bar:~$ docker build -t ri-logging .
        ```
### Run

#### Shell

1. Run from the project root directory
    ```console
    foo@bar:~$ python run run.py
    ```
    
#### Docker

1. Run from the project root directory. The `docker run` command requires an `-e` flag for each property form the `config_base.json`. 
    ```console
    foo@bar:~$ docker run -d -p 9798:9798 -v /directory_of_nginx_logs:/back_end_log -e DB_HOST="0.0.0.0" --name ri-logging
    ```

### How to Use This Microservice

The frontend logging is done by the logging script. To use the logging script include following line in the head of your website: 
```html
<script src="https://yourhost/frontend/script"></script>
```

The access to the frontend and backend logs is documented in the included Swagger file or the API documentation ([web page] (https://api.openreq.eu/#/services/ri-logging)).

### Notes for Developers

The configuration and installation for development is the same as the shell version. But requires the `config_dev.json` file to be in the root directory. The file can be created by duplicating the `config_base.json` and filling it with config values. 

#### Updating requirements.txt

Run the following command to update the requirements.txt before pushing to GIT:
1) `venv/bin/pip freeze > requirements.txt`
2) Remove `pymongo` from requirements.txt

NOTE: If you run `pip freeze > requirements.txt` from a normal terminal, you will include all global packages, 
creating a bloated file. Please only use this command from a virtual environment where you are certain of the packages.

#### Running Tests

To run the tests:
1) Navigate to the root folder
2) Run `python tests/test_all.py`

## Sources

None

## How to contribute

See OpenReq project contribution 
[Contribution Guidelines](https://github.com/OpenReqEU/OpenReq/blob/master/CONTRIBUTING.md)

## License

Free use of this software is granted under the terms of the EPL version 2 ([EPL2.0](https://www.eclipse.org/legal/epl-2.0/)).