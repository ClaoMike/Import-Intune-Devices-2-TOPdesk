#!/usr/bin/env python3

from utils import make_request, RequestType
from env_variables import *
import time

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

def get_devices_from_curren_page(url, access_token):
    return make_request(
        request_type=RequestType.GET,
        url=url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
    )

def create_device_asset(name: str):
    response = make_request(
        request_type=RequestType.POST,
        url="https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json={
            "name": name, # ,
            "type_id": topdesk_devices_category_id,
            "assignmentWidget": {
                "assignPerson": "8bee9359-678b-43ca-a060-9b101b7bad6c"
            }
        }
    )

    return response

def get_device_user(access_token, device_id):
    user = make_request(
        request_type=RequestType.GET,
        url=f"https://graph.microsoft.com/v1.0/devices/{device_id}/registeredUsers",
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )

    try:
        return user.get('value')[0].get('id')
    except:
        return None

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
    except:
        return None

def assign_user_to_asset(asset_id, topdesk_person_id):
    response = make_request(
        request_type=RequestType.PUT,
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments",
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

# get the intune access token, it lasts for 3599 seconds, so we have to re0get it if an hour passes
access_token = get_access_token()
start_time = time.time()

device_count=1
url = "https://graph.microsoft.com/v1.0/devices"
while url:
    # see if you need a new access token
    end_time = time.time()
    elapsed_seconds = end_time - start_time

    if elapsed_seconds > 3000:
        access_token = get_access_token()
        start_time = time.time()

    # get devices from the current page
    response = get_devices_from_curren_page(url, access_token)

    devices = response['value']
    for device in devices:
        # print(str(device_count) + ". " + str(device))
        device_count += 1

        # create the TOPdesk asset
        device_as_topdesk_asset = create_device_asset(device["id"])
        asset_id = device_as_topdesk_asset.get('data').get('unid')
        # print(f"TOPdesk asset's ID: {asset_id}")

        # get the device's user id from Intune (the mainframe in TOPdesk)
        user_id = get_device_user(access_token, device["id"])

        if user_id is not None:
            # print(f"User ID: {user_id}")

            topdesk_person_id = get_topdesk_user_id_by_mainframe(user_id)

            if topdesk_person_id is not None:
                # print(f"Person card in TOPdesk ID: {topdesk_person_id}")

                assign_user_to_asset(asset_id, topdesk_person_id)

        device_count += 1

    url = response.get('@odata.nextLink')