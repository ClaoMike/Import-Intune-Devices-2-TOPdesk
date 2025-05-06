from enum import Enum

class RequestType(Enum):
    """
        Enum representing the types of HTTP requests supported by the TOPdesk API.
    """
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    GET = "GET"