import requests
import json
from microsoft_methods import *
from topdesk_methods import *
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_devices_and_assets_in_parallel():
    all_assets = []
    topdesk_categories = [
        topdesk_computer_category_id,
        topdesk_mobile_category_id,
        topdesk_device_category_id
    ]

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []

        # Start asset fetching for each category
        for category_id in topdesk_categories:
            futures.append(executor.submit(fetch_all_assets, category_id))

        # Start fetching Azure and Intune devices
        device_future = executor.submit(fetch_devices)

        # Wait for asset futures
        for future in as_completed(futures):
            try:
                assets = future.result()
                all_assets.extend(assets)
            except Exception as e:
                print(f"[✗] Error fetching assets: {e}")

        # Wait for devices
        devices = device_future.result()

    # Transforming the assets into dictionary as well
    all_assets_as_dict = {}
    for asset in all_assets:
        if asset.name:
            all_assets_as_dict[asset.name] = asset

    print(f"\n[✓] Total assets fetched: {len(all_assets)}")
    print(f"[✓] Total devices fetched: {len(devices)}")

    return devices, all_assets_as_dict

def update_TOPdesk(devices_to_create_list, assets_to_delete_list, assets_to_be_updated):
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_label = {
            executor.submit(create_assets, devices_to_create_list): "Create",
            executor.submit(delete_assets, assets_to_delete_list): "Delete",
            executor.submit(update_assets, assets_to_be_updated): "Update"
        }

        for future in as_completed(future_to_label):
            label = future_to_label[future]
            try:
                future.result()
                print(f"[✓] {label} task completed.")
            except Exception as e:
                print(f"[✗] {label} task failed: {e}")