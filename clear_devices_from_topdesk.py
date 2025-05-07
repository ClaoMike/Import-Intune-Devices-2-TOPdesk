#!/usr/bin/env python3
from utils import make_request, RequestType
from env_variables import *
import requests
import json

page_size = 500
asset_counter = 1

removable_assets_categories = [topdesk_computer_category_id, topdesk_mobile_category_id, topdesk_device_category_id]
for removable_asset_category in removable_assets_categories:
    page_start = 0
    while True:
        response = make_request(
            request_type=RequestType.GET,
            url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets?templateId={removable_asset_category}&fields=name",
            auth=(topdesk_username, topdesk_password),
            headers={
                'Content-Type': 'application/json'
            },
            params={
                'templateId': removable_asset_category,
                'pageStart': page_start,
                'pageSize': page_size
            }
        )

        assets = response.json().get('dataSet', [])

        if not assets:
            break

        unids = [asset['unid'] for asset in assets]

        print("Deleting:")
        for unid in unids:
            print(f"{asset_counter}. {unid}")
            asset_counter += 1

        make_request(
            request_type=RequestType.POST,
            url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/delete",
            auth=(topdesk_username, topdesk_password),
            headers={
                'Content-Type': 'application/json'
            },
            json={
                'unids': unids
            }
        )

        page_start += page_size
