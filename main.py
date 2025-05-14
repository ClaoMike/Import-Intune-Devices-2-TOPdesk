#!/usr/bin/env python3
import time
from utils import *

start_time = time.time()

# Fetch devices and assets
devices, all_assets = fetch_devices_and_assets_in_parallel()

# Filter to-dos
devices_to_create_list, assets_to_delete_list, assets_to_be_updated = filter_assets_and_devices(
    devices,
    all_assets
)

# Update TOPdesk
update_TOPdesk(devices_to_create_list, assets_to_delete_list, assets_to_be_updated)

end_time = time.time()
elapsed = end_time - start_time

print(f"\n[✓] Total time: {elapsed:.2f} seconds")
