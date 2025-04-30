#!/usr/bin/env python3

from utils import make_request, RequestType, DeviceType
from env_variables import *
import time
from operating_systems import *

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

    if user_id is not None:
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

# get the intune access token, it lasts for 3599 seconds, so we have to re-get it if an hour passes
access_token = get_access_token()
start_time = time.time()

device_count=1
current_page_of_devices_url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices"
while current_page_of_devices_url:
    # see if you need a new access token
    end_time = time.time()
    elapsed_seconds = end_time - start_time

    if elapsed_seconds > 3000:
        access_token = get_access_token()
        start_time = time.time()

    # get devices from the current page and the link to the following page, if it exists
    devices, current_page_of_devices_url = get_devices_from_curren_page(current_page_of_devices_url, access_token)

    for device in devices:
        print(f"{device_count}. ID: {device.get('id')} OS: {device.get('operatingSystem')}")

        asset_id = create_device_asset(
            get_device_type(
                device.get('operatingSystem')
            ), device)

        # if the person card is found, attach the asset to it
        assign_user_to_asset(dvc=device, topdesk_asset_id=asset_id)

        device_count += 1