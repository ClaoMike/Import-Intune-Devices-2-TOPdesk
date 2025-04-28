#!/usr/bin/env python3
from utils import make_request, RequestType
from env_variables import *

page_start = 0
page_size = 500

asset_counter = 1

while True:
    response = make_request(
        request_type=RequestType.GET,
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets?templateId={topdesk_devices_category_id}&fields=name",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        params={
            'templateId': topdesk_devices_category_id,
            'pageStart': page_start,
            'pageSize': page_size
        }
    )

    assets = response.get('dataSet', [])

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
