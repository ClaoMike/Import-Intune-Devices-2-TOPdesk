#!/usr/bin/env python3
from utils import *

devices, all_assets = fetch_devices_and_assets_in_parallel()

# for asset in all_assets:
#     print(asset.toString())

print(devices)