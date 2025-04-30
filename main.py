#!/usr/bin/env python3

from utils import *
import time

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