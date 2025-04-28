import requests
from enum import Enum
from requests import Response

class RequestType(Enum):
    """
        Enum representing the types of HTTP requests supported by the TOPdesk API.

        Attributes:
            POST: Represents an HTTP POST request (used for creating resources).
            PATCH: Represents an HTTP PATCH request (used for updating resources partially).
            PUT: Represents an HTTP PUT request (used for updating or replacing resources).
    """
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    GET = "GET"

def evaluateResponse(response: Response):
    """
    Categorizes and handles the status code of an HTTP response.

    Args:
        response (requests.Response): The HTTP response object to evaluate.

    Raises:
        RequestFailedException: If the status code is not in the 2xx range.
    """

    if 200 <= response.status_code < 300:
        print(f"Request was successful! Status code: {response.status_code}")
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def make_request(request_type: RequestType, url: str, headers, data=None, auth=None, json=None, params=None):
    """
        Makes an HTTP request with the specified request type.

        Returns:
            dict: The JSON response from the API.

        Raises:
            SystemExit: If an unsupported request type is provided.
    """
    # Construct request parameters
    request_params = {
        "url": url,
        "headers": headers,
    }

    if data is not None:
        request_params["data"] = data

    if auth is not None:
        request_params["auth"] = auth

    if json is not None:
        request_params["json"] = json

    if params is not None:
        request_params["params"] = params

    # Log the request attempt
    print(f"Performing a {request_type.value} request at {request_params['url']}")

    # Perform the appropriate HTTP request based on the request type
    if request_type == RequestType.GET:
        response = requests.get(**request_params)

    elif request_type == RequestType.PATCH:
        response = requests.patch(**request_params)

    elif request_type == RequestType.POST:
        response = requests.post(**request_params)

    elif request_type == RequestType.PUT:
        response = requests.put(**request_params)

    else:
        raise ValueError("Invalid request type")

    # Evaluate the response (this may log errors and raise exceptions if necessary)
    evaluateResponse(response)

    # Return the parsed JSON response
    try:
        return response.json()
    except:
        return None