"""
created at: 2018-12-19
author:     Volodymyr Biryuk

The module to run the micro service locally for development purposes.
"""
import os

import microservice

if __name__ == '__main__':
    app = microservice.create_app('config_dev.json')
    app.run(host=app.config['MS_HOST'], port=int(app.config['MS_PORT']))
