import requests
from requests import Response
import json
from operating_systems import *
from env_variables import *
from json_parsing import *
from requests_types import *
from device_types import *

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

    return response

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

    if 200 <= response.status_code < 300:
        print("Successfully obtained access token")
        return response.json()['access_token']
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def get_devices_from_curren_page(url, tkn):
    response = make_request(
        request_type=RequestType.GET,
        url=url,
        headers={
            'Authorization': f'Bearer {tkn}',
            'Content-Type': 'application/json'
        },
    )

    if 200 <= response.status_code < 300:
        return response.json().get('value'), response.json().get('@odata.nextLink')
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def get_device_type(operating_system: str):
    if operating_system in device_os:  # Skip these
        return DeviceType.DEVICE
    elif operating_system in computer_os:
        return DeviceType.COMPUTER
    elif operating_system in mobile_os:
        return DeviceType.MOBILE
    else:
        print("New OS detected - please take action")
        return None

def generate_asset_name(platform, device):
    if platform == "intune":
        id = device.get('azureADDeviceId')
    else:
        id = device.get('id')

    operating_system = device.get('operatingSystem')
    type = get_device_type(operating_system).value

    return f"{type}-{id}"

def search_for_topdesk_asset_by_asset_name(asset_name):
    response = make_request(
        request_type=RequestType.GET,
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets?nameFragment={asset_name}",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        }
    )

    if 200 <= response.status_code < 300:
        data_set = response.json().get('dataSet')
        if len(data_set) == 0:
            return None
        else:
            return data_set[0].get('id')
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def get_device_template(device):
    operating_system = device.get('operatingSystem')
    type = get_device_type(operating_system)

    if type is DeviceType.DEVICE:  # Skip these
        return topdesk_device_category_id
    elif type is DeviceType.COMPUTER:
        return topdesk_computer_category_id
    elif type is DeviceType.MOBILE:
        return topdesk_mobile_category_id
    else:
        print("New OS detected - please take action")
        return None

def create_asset_for(platform, device, tkn):
    # create_asset
    asset_name = generate_asset_name(platform, device)
    template_id = get_device_template(device)

    if platform == "intune":
        json = generate_intune_asset_as_json(device, asset_name, template_id)
    else:

        userId = get_user_id_of_azure_device(device, tkn)
        # json = generate_azure_asset_as_json(device, asset_name, template_id, userId)

    # response = make_request(
    #     request_type=RequestType.POST,
    #     url="https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets",
    #     auth=(topdesk_username, topdesk_password),
    #     headers={
    #         'Content-Type': 'application/json'
    #     },
    #     json=json
    # )

    # if 200 <= response.status_code < 300:
    #     print("Asset successfully created")
    # else:
    #     error_message = f"Error {response.status_code}: {response.text}"
    #     raise ValueError(error_message)

    # assign_user

def get_user_id_of_azure_device(device, tkn):
    response = make_request(
        request_type=RequestType.GET,
        url=f"https://graph.microsoft.com/v1.0/devices/{device.get('id')}/registeredUsers",
        headers={
            'Authorization': f'Bearer {tkn}',
            'Content-Type': 'application/json'
        },
    )

    if 200 <= response.status_code < 300:
        user = response.json().get('value')
        if len(user) == 0:
            print(f"No user for this device!")
            return None
        else:
            user = user[0].get('id')
            print(f"User found: {user}")
        return user
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

# def get_topdesk_user_id_by_mainframe(user_id):
#     topdesk_person = make_request(
#         request_type=RequestType.GET,
#         url=f"https://dlfseeds.topdesk.net/tas/api/persons?query=mainframeLoginName=={user_id}",
#         auth=(topdesk_username, topdesk_password),
#         headers={
#             'Content-Type': 'application/json'
#         }
#     )
#
#     try:
#         if topdesk_person[0].get('status') != 'personArchived':
#             return topdesk_person[0].get('id')
#     except (AttributeError, KeyError, IndexError, TypeError):
#         return None


# def assign_user_to_asset(dvc, topdesk_asset_id):
#     if topdesk_asset_id is None:
#         print("Asset ID is required to assign user to asset!")
#         return
#     # get the ID of the user that uses the device;
#     # This is the same as a persons' mainframe ID, stored in TOPdesk person cards
#     user_id = dvc.get("userId")
#
#     if user_id != "":
#         print(f"User ID: {user_id}")
#
#         topdesk_person_id = get_topdesk_user_id_by_mainframe(user_id)  # get the TOPdesk person card, searching by the above mainframe
#
#         if topdesk_person_id is not None:
#             print("Found its TOPdesk Person card.")
#
#             # if the person card is found, attach the asset to it
#             response = make_request(
#                 request_type=RequestType.PUT,
#                 url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{topdesk_asset_id}/assignments",
#                 auth=(topdesk_username, topdesk_password),
#                 headers={
#                     'Content-Type': 'application/json'
#                 },
#                 json={
#                     "linkToId": topdesk_person_id,
#                     "linkType": "person"
#                 }
#             )
#
#             return response
#         else:
#             print(f"User ID exists on Azure, but there is no Person card for it in TOPdesk.")
#     else:
#         print("No user assigned to this device!")
#         return

