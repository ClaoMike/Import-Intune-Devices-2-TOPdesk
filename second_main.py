#!/usr/bin/env python3
import authentication
import auth_state

from utils import *
import time
from microsoft_methods import *
from device_methods import *
from AzureDevice import *
from IntuneDevice import *

platforms = {
    "intune": "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices",
    "azure": "https://graph.microsoft.com/v1.0/devices"
}
devices = []

# get the intune access token, it lasts for 3599 seconds, so we have to re-get it if an hour passes
authentication.get_access_token()
start_time = time.time()

for platform, next_devices_page_url in platforms.items():
    print(f"Platform: {platform}, URL: {next_devices_page_url}")

    while next_devices_page_url:
        end_time = time.time()
        elapsed_seconds = end_time - start_time

        if elapsed_seconds > 3000:
            authentication.get_access_token()
            start_time = time.time()

        current_page_devices, next_devices_page_url = get_devices_from_curren_page(next_devices_page_url)

        for device in current_page_devices:
            if platforms == "intune":
                devices.append(IntuneDevice(device))
            else:
                devices.append(AzureDevice(device))

print(len(devices))