"""
created at: 2018-12-19
author:     Volodymyr Biryuk

The module to run the micro service in the shell.
"""
import microservice

if __name__ == '__main__':
    app = microservice.create_app()
    app.run(host=app.config['MS_HOST'], port=int(app.config['MS_PORT']))
