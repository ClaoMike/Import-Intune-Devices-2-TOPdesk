#!/usr/bin/env python3
import authentication
from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed

from microsoft_methods import *

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

print(azure_user_map)
