#!/usr/bin/env python3
import authentication
from microsoft_methods import *
from concurrent.futures import ThreadPoolExecutor, as_completed

# Platform endpoints
platforms = {
    "intune": "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices",
    "azure": "https://graph.microsoft.com/v1.0/devices"
}

# Initialize auth
authentication.get_access_token()

# Containers
devices = []
azure_devices = []
intune_devices = []

# Run fetches in parallel
with ThreadPoolExecutor(max_workers=2) as executor:
    futures = {
        executor.submit(fetch_all_devices_from_platform, platform, url): platform
        for platform, url in platforms.items()
    }

    for future in as_completed(futures):
        platform = futures[future]
        try:
            platform_devices = future.result()
            print(f"Finished loading {len(platform_devices)} {platform} devices.")

            if platform == "azure":
                azure_devices.extend(platform_devices)
            elif platform == "intune":
                intune_devices.extend(platform_devices)

        except Exception as e:
            print(f"Error while loading {platform} devices: {e}")

azure_device_ids = [device.id for device in azure_devices if device.id is not None]
users = batch_get_registered_users(azure_device_ids)