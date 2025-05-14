import auth_state
import authentication

import requests
import time
from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def fetch_devices():
    authentication.get_access_token()

    platforms = {
        "intune": "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices",
        "azure": "https://graph.microsoft.com/v1.0/devices"
    }

    azure_devices = []
    intune_devices = []
    azure_user_map = {}
    azure_queue = Queue()

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(
                fetch_all_devices_from_platform,
                platform,
                url,
                azure_queue if platform == "azure" else None,
                azure_devices if platform == "azure" else None,
                intune_devices if platform == "intune" else None
            ): platform
            for platform, url in platforms.items()
        }

        # Start user lookup thread
        user_thread = Thread(target=user_batch_worker, args=(azure_queue, azure_user_map))
        user_thread.start()

        # Wait for both fetch threads
        for future in as_completed(futures):
            platform = futures[future]
            try:
                future.result()
                print(f"[✓] Finished fetching {platform} devices.")
            except Exception as e:
                print(f"[✗] Error fetching {platform}: {e}")

        user_thread.join()

    print(f"\n[Summary]")
    print(f"Azure Devices: {len(azure_devices)}")
    print(f"Intune Devices: {len(intune_devices)}")
    print(f"Azure Devices with User IDs: {len(azure_user_map)}")

    # assing users for azure devices
    for azure_device in azure_devices:
        azure_device.user_id = azure_user_map.get(azure_device.id)

    all_devices = azure_devices + intune_devices

    return all_devices