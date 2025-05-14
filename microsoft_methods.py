import requests
import time

import auth_state
import authentication

from AzureDevice import *
from IntuneDevice import *

def fetch_all_devices_from_platform(platform, start_url):
    devices = []
    next_devices_page_url = start_url
    start_time = time.time()

    while next_devices_page_url:
        elapsed_seconds = time.time() - start_time
        if elapsed_seconds > 3000:
            authentication.get_access_token()
            start_time = time.time()

        current_page_devices, next_devices_page_url = get_devices_from_curren_page(next_devices_page_url)

        for device in current_page_devices:
            if platform == "intune":
                devices.append(IntuneDevice(device))
            else:
                devices.append(AzureDevice(device))
    return devices

def get_devices_from_curren_page(url):
    response = requests.get(
        url=url,
        headers={
            'Authorization': f'Bearer {auth_state.access_token}',
            'Content-Type': 'application/json'
        },
    )

    if 200 <= response.status_code < 300:
        return response.json().get('value'), response.json().get('@odata.nextLink')
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def batch_get_registered_users(device_ids):
    url = "https://graph.microsoft.com/v1.0/$batch"
    headers = {
        "Authorization": f"Bearer {auth_state.access_token}",
        "Content-Type": "application/json"
    }

    requests_payload = [
        {
            "id": device_id,
            "method": "GET",
            "url": f"/devices/{device_id}/registeredUsers"
        }
        for i, device_id in enumerate(device_ids)
    ]

    # Split into chunks of 20
    all_results = {}
    for i in range(0, len(requests_payload), 20):
        chunk = requests_payload[i:i+20]
        _json = {"requests": chunk}

        response = requests.post(url, headers=headers, json=_json)
        data = response.json()

        for item in data.get("responses", []):
            dev_id = item.get("id")
            if item["status"] == 200:
                users = item["body"].get("value", [])
                if len(users) == 0:
                    user_id = None
                else:
                    user_id = users[0].get("id")
                all_results[dev_id] = user_id
            else:
                all_results[dev_id] = None  # or log error
    return all_results

# def get_user_id_of_azure_device(device_id):
#     response = requests.get(
#         url=f"https://graph.microsoft.com/v1.0/devices/{device_id}/registeredUsers",
#         headers={
#             'Authorization': f'Bearer {auth_state.access_token}',
#             'Content-Type': 'application/json'
#         },
#     )
#
#     if 200 <= response.status_code < 300:
#         user = response.json().get('value')
#         if len(user) == 0:
#             return None
#         else:
#             user = user[0].get('id')
#         return user
#     else:
#         error_message = f"Error {response.status_code}: {response.text}"
#         raise ValueError(error_message)