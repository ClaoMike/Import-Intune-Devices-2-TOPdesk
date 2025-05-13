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

assets_that_should_stay = set()
all_assets = set()
assets_that_must_be_deleted = set()

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
            # print(f"{device_count}. Device: {device}")
            asset_name = generate_asset_name(platform, device)



            # search if the device already has an asset
            # topdesk_asset_id = search_for_topdesk_asset_by_asset_name(asset_name)
            #
            # # if the device does have an asset:
            # if topdesk_asset_id:
            #     print(f"Asset found: {topdesk_asset_id}")
            #     # update device
            #     update_asset(device, topdesk_asset_id, platform, access_token)
            # # if the device does not have an asset
            # else:
            #     print(f"Asset not found: {asset_name}")
            #     # create asset with this device
            #     create_asset_for(platform, device, access_token)

            # at this point, we know the asset exists
            assets_that_should_stay.add(asset_name)

            device_count += 1

# get all assets

# response = requests.delete(
#         url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments/{link_id}",
#         auth=(topdesk_username, topdesk_password),
#         headers={
#             'Content-Type': 'application/json'
#         },
#     )
#
#     if 200 <= response.status_code < 300:
#         print("Successfully deleted the assignment link!")
#     else:
#         error_message = f"Error {response.status_code}: {response.text}"
#         raise ValueError(error_message)

# all_assets = ...

# get the assets that should be deleted
assets_that_must_be_deleted = all_assets.difference(assets_that_should_stay)

# delete them
