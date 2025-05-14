#!/usr/bin/env python3
from microsoft_methods import *

# Fetch devices from Azure & Intune
# devices = fetch_devices()

# Fetch assets from TOPdesk
import requests
import auth_state
from env_variables import *

def fetch_all_assets(template_id, page_size=1000):
    all_assets = []
    page_start = 0
    has_more = True

    fields = [
        "name", "intune-id", "azure-ad-registered", "azure-id", "serial-number",
        "name-1", "manufacturer-1", "model-1", "operating-system", "os-version",
        "enrollment-date", "last-check-in", "management-certificate-expiration-date",
        "ismanaged", "imei", "encrypted", "subscriber-carrier", "total-storage",
        "storage", "compliance-status", "ownership", "user-id"
    ]

    base_url = "https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets"
    auth = (topdesk_username, topdesk_password)
    headers = {
        "Accept": "application/x.topdesk-am-assets-v2+json",  # v2 recommended
        "Content-Type": "application/json"
    }

    fields_param = ",".join(fields)

    while has_more:
        params = {
            "templateId": template_id,
            "fields": fields_param,
            "pageStart": page_start,
            "pageSize": page_size
        }

        response = requests.get(base_url, headers=headers, params=params, auth=auth)
        if response.status_code not in [200, 206]:
            raise Exception(f"Error {response.status_code}: {response.text}")

        data = response.json()

        if not data:
            break

        assets = data.get("dataSet")

        all_assets.extend(assets)
        print(f"Fetched {len(assets)} assets (total so far: {len(all_assets)})")

        # If 206 Partial Content, continue. If 200 OK, we're done.
        has_more = response.status_code == 206
        page_start += page_size

    return all_assets

topdesk_categories = [
    topdesk_computer_category_id,
    topdesk_mobile_category_id,
    topdesk_device_category_id
]

all_assets = []

for category in topdesk_categories:
    assets = fetch_all_assets(category)
    all_assets += assets

print(f"Total assets fetched: {len(all_assets)}")