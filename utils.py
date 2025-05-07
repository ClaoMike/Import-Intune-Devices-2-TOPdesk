import requests
import json
from operating_systems import *
from env_variables import *
from json_parsing import *
from device_types import *

def get_access_token():
    response = requests.post(
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
    response = requests.get(
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
    response = requests.get(
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
        userId = device.get('userId')
        json = generate_intune_asset_as_json(device, asset_name, template_id)
    else:
        userId = get_user_id_of_azure_device(device, tkn)
        json = generate_azure_asset_as_json(device, asset_name, template_id, userId)

    response = requests.post(
        url="https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json=json
    )

    if 200 <= response.status_code < 300:
        asset_id = response.json().get('data').get('unid')
        print(f"Successfully created the asset with ID:{asset_id}")
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

    # assign_user
    if userId is None or userId == '':
        return

    topdesk_person_card_id = get_topdesk_user_id_by_mainframe(userId)

    if topdesk_person_card_id is None:
        return

    print(f"TOPdesk card ID: {topdesk_person_card_id}")

    assign_user_to_asset(topdesk_person_card_id, asset_id)

def get_user_id_of_azure_device(device, tkn):
    response = requests.get(
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
            return ''
        else:
            user = user[0].get('id')
            print(f"User found: {user}")
        return user
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def get_topdesk_user_id_by_mainframe(user_id):
    response = requests.get(
        url=f"https://dlfseeds.topdesk.net/tas/api/persons?query=mainframeLoginName=={user_id}",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        }
    )

    if 200 <= response.status_code < 300:
        if response.text != '':
            print(response.json())

            if len(response.json()) == 0:
                return None

            person_card = response.json()[0]
            if person_card.get('status') != 'personArchived':
                return person_card.get('id')
            else:
                return None
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def assign_user_to_asset(person_card_id, asset_id):
    response = requests.put(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json={
            "linkToId": person_card_id,
            "linkType": "person"
        }
    )

    if 200 <= response.status_code < 300:
        print("Successfully assigned user to asset")
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)