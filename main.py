#!/usr/bin/env python3
from utils import *

devices, all_assets = fetch_devices_and_assets_in_parallel()

device_keys = set(devices.keys())
asset_keys = set(all_assets.keys())

# assets that need to be created
devices_to_create = device_keys - asset_keys
devices_to_create_list = [devices[key] for key in devices_to_create]

# assets that must be deleted
# assets_to_delete = asset_keys - device_keys
# assets_to_delete_list = [devices[key] for key in assets_to_delete]
#
# devices and assets that must be checked for comparison
# matching_keys = device_keys & asset_keys

print(f"Assets to be created: {len(devices_to_create_list)}")
# print(f"Assets to be deleted: {len(assets_to_delete)}")
# print(f"Assets to be matched: {len(matching_keys)}")
# print(f"Total: {len(assets_to_delete) + len(devices_to_create) + len(matching_keys)}")