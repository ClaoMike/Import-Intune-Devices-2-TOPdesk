import requests
from enum import Enum
from requests import Response
import json
from operating_systems import *
from env_variables import *

class RequestType(Enum):
    """
        Enum representing the types of HTTP requests supported by the TOPdesk API.
    """
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    GET = "GET"

class DeviceType(Enum):
    """
        Enum representing the types of devices.
    """
    COMPUTER = "COMPUTER"
    MOBILE = "MOBILE"

def evaluateResponse(response: Response):
    """
    Categorizes and handles the status code of an HTTP response.

    Args:
        response (requests.Response): The HTTP response object to evaluate.

    Raises:
        RequestFailedException: If the status code is not in the 2xx range.
    """

    if 200 <= response.status_code < 300:
        return
    elif response.status_code == 400:
        try:
            response_text_as_json = json.loads(response.text)
            error_text = response_text_as_json.get('errors')[0]

            if error_text.get('fieldName') == 'name' and error_text.get('fieldTitle') == 'Asset ID' and error_text.get('message') == 'This ID is already in use.':
                print("Error: Asset ID is already in use.")
                return
        except:
            error_message = f"Error {response.status_code}: {response.text}"
            raise ValueError(error_message)
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
    # print(f"Performing a {request_type.value} request at {request_params['url']}")

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

def get_access_token():
    response = make_request(
        request_type=RequestType.POST,
        url=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={
            'client_id': client_id,
            'scope': 'https://graph.microsoft.com/.default',
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
        }
    )

    return response['access_token']

def get_devices_from_curren_page(url, tkn):
    response = make_request(
        request_type=RequestType.GET,
        url=url,
        headers={
            'Authorization': f'Bearer {tkn}',
            'Content-Type': 'application/json'
        },
    )
    return response.get('value'), response.get('@odata.nextLink')

def get_topdesk_user_id_by_mainframe(user_id):
    topdesk_person = make_request(
        request_type=RequestType.GET,
        url=f"https://dlfseeds.topdesk.net/tas/api/persons?query=mainframeLoginName=={user_id}",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        }
    )

    try:
        if topdesk_person[0].get('status') != 'personArchived':
            return topdesk_person[0].get('id')
    except (AttributeError, KeyError, IndexError, TypeError):
        return None


def assign_user_to_asset(dvc, topdesk_asset_id):
    if topdesk_asset_id is None:
        print("Asset ID is required to assign user to asset!")
        return
    # get the ID of the user that uses the device;
    # This is the same as a persons' mainframe ID, stored in TOPdesk person cards
    user_id = dvc.get("userId")

    if user_id != "":
        print(f"User ID: {user_id}")

        topdesk_person_id = get_topdesk_user_id_by_mainframe(user_id)  # get the TOPdesk person card, searching by the above mainframe

        if topdesk_person_id is not None:
            print("Found its TOPdesk Person card.")

            # if the person card is found, attach the asset to it
            response = make_request(
                request_type=RequestType.PUT,
                url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{topdesk_asset_id}/assignments",
                auth=(topdesk_username, topdesk_password),
                headers={
                    'Content-Type': 'application/json'
                },
                json={
                    "linkToId": topdesk_person_id,
                    "linkType": "person"
                }
            )

            return response
        else:
            print(f"User ID exists on Azure, but there is no Person card for it in TOPdesk.")
    else:
        print("No user assigned to this device!")
        return

def get_device_type(operating_system: str):
    if operating_system in skip_os:  # Skip these
        return None
    elif operating_system in computer_os:
        return DeviceType.COMPUTER
    elif operating_system in mobile_os:
        return DeviceType.MOBILE
    else:
        print("New OS detected - please take action")
        return None

def validate_topdesk_asset(asset):
    if asset is None:  # no device created, thus we move to the next one
        return False

    if asset.get('data') is None:  # if no data here, it means it must be an accepted error
        print("No data for this device, check for errors!")
        return False

    return True

def create_device_asset(device_type: DeviceType, dvc):
    if device_type is None:
        print("Unknown OS")
        return None

    if device_type == DeviceType.COMPUTER:
        category_key = topdesk_computer_category_id
        name = dvc.get('serialNumber')

    elif device_type == DeviceType.MOBILE:
        category_key = topdesk_mobile_category_id
        name = dvc.get('id')

    else:
        print("Unknown device type")
        return None

    print(f"TOPdesk name: {device_type.value}-{name}")

    response = make_request(
        request_type=RequestType.POST,
        url="https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json={
            "name": f"{device_type.value}-{name}",
            "type_id": category_key,
            "assignmentWidget": {
                "assignPerson": "8bee9359-678b-43ca-a060-9b101b7bad6c"
            }
        }
    )

    if validate_topdesk_asset(response):
        topdesk_id = response.get('data').get('unid')
        print(f"TOPdesk ID: {topdesk_id}")

        return topdesk_id  # extract the newly created asset's ID
    else:
        return None