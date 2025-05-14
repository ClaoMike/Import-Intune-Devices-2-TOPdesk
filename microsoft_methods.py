import auth_state
import authentication

import requests
import time

from AzureDevice import *
from IntuneDevice import *

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
        raise ValueError(f"Error {response.status_code}: {response.text}")

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
        for device_id in device_ids
    ]

    all_results = {}
    for i in range(0, len(requests_payload), 20):
        chunk = requests_payload[i:i + 20]
        response = requests.post(url, headers=headers, json={"requests": chunk})
        data = response.json()

        for item in data.get("responses", []):
            dev_id = item.get("id")
            if item["status"] == 200:
                users = item["body"].get("value", [])
                user_id = users[0].get("id") if users else None
                all_results[dev_id] = user_id
            else:
                all_results[dev_id] = None
    return all_results

def fetch_all_devices_from_platform(platform, url, azure_queue=None, azure_devices=None, intune_devices=None):
    next_page = url
    start_time = time.time()

    while next_page:
        if time.time() - start_time > 3000:
            authentication.get_access_token()
            start_time = time.time()

        current_page, next_page = get_devices_from_curren_page(next_page)

        for device in current_page:
            if platform == "azure":
                az_device = AzureDevice(device)
                azure_devices.append(az_device)
                azure_queue.put(device)
            elif platform == "intune":
                intune_devices.append(IntuneDevice(device))

    if platform == "azure":
        azure_queue.put(None)

def user_batch_worker(device_queue, result_dict):
    buffer = []
    while True:
        item = device_queue.get()
        if item is None:
            if buffer:
                ids = [d.get("id") for d in buffer if d.get("id")]
                result_dict.update(batch_get_registered_users(ids))
            break

        buffer.append(item)
        if len(buffer) == 20:
            ids = [d.get("id") for d in buffer if d.get("id")]
            result_dict.update(batch_get_registered_users(ids))
            buffer.clear()