# dependencies
from microservice.lib.request_handler import RiLoggingRequestHandler
from microservice.lib.messages import RiLoggingError


# executes the initialization
def start(configuration):
    RiLoggingRequestHandler.configuration = configuration
    import microservice.lib.endpoints
