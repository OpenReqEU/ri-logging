"""
created at: 2018-12-19
author:     Volodymyr Biryuk

The module to run the micro service locally for development purposes.
"""
import os

import microservice

if __name__ == '__main__':
    app = microservice.create_app()
    dirname = os.path.dirname(os.path.realpath(__file__))
    try:
        filename = os.path.join(dirname, 'coverage-reports')
        for file in os.listdir(filename):
            app.logger.info(file)
    except FileNotFoundError as e:
        pass
    app.run(host=app.config['MS_HOST'], port=int(app.config['MS_PORT']))
