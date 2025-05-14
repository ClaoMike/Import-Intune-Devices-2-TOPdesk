#!/usr/bin/env python3
from utils import *

devices, all_assets = fetch_devices_and_assets_in_parallel()

devices_to_create_list, assets_to_delete_list, assets_to_be_updated = filter_assets_and_devices(
    devices,
    all_assets
)

# create_assets(devices_to_create_list)
# delete_assets(assets_to_delete_list)
update_assets(assets_to_be_updated)