#!/usr/bin/env python3
from utils import *
import time
from authentication import *
from microsoft_methods import *
from device_methods import *

# get the intune access token, it lasts for 3599 seconds, so we have to re-get it if an hour passes
access_token = get_access_token()
start_time = time.time()

platforms = {
    "intune": "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices",
    "azure": "https://graph.microsoft.com/v1.0/devices"
}

device_count=1
for platform, next_devices_page_url in platforms.items():
    print(f"Platform: {platform}, URL: {next_devices_page_url}")

    while next_devices_page_url:
        # see if you need a new access token
        end_time = time.time()
        elapsed_seconds = end_time - start_time

        if elapsed_seconds > 3000:
            access_token = get_access_token()
            start_time = time.time()

        # get devices from the current page and the link to the following page, if it exists
        devices, next_devices_page_url = get_devices_from_curren_page(next_devices_page_url, access_token)

        for device in devices:
            print(f"{device_count}. Device: {device}")
            asset_name = generate_asset_name(platform, device)

            # search if the device already has an asset
            topdesk_asset_id = search_for_topdesk_asset_by_asset_name(asset_name)

            # if the device does have an asset:
            if topdesk_asset_id:
                print(f"Asset found: {topdesk_asset_id}")
                # update device
                update_asset(device, topdesk_asset_id, platform)
            # if the device does not have an asset
            else:
                print(f"Asset not found")
                # create asset with this device
                create_asset_for(platform, device, access_token)

            device_count += 1