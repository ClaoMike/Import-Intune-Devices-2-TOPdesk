import requests
from env_variables import *
from TOPdeskAsset import TOPdeskAsset

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
        "Accept": "application/x.topdesk-am-assets-v2+json",
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
        assets_as_json = data.get("dataSet")
        assets = [TOPdeskAsset(asset) for asset in assets_as_json]
        all_assets.extend(assets)
        print(f"[{template_id}] Fetched {len(assets)} assets (total so far: {len(all_assets)})")

        has_more = response.status_code == 206
        page_start += page_size

    return all_assets

def create_assets(devices):
    if len(devices) != 0:
        print(f"Creating assets for {len(devices)} devices")

        for device in devices:
            device.create_in_TOPdesk()
            device.assign_user()

def delete_assets(assets):
    if len(assets) != 0:
        print(f"Deleting {len(assets)} assets")

        asset_ids_to_delete = [asset.id for asset in assets if asset.id is not None]

        response = requests.post(
            url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/delete",
            auth=(topdesk_username, topdesk_password),
            headers={
                'Content-Type': 'application/json'
            },
            json={
                'unids': asset_ids_to_delete
            }
        )

        if 200 <= response.status_code < 300:
            return
        else:
            error_message = f"Error {response.status_code}: {response.text}"
            raise ValueError(error_message)

# def search_for_topdesk_asset_by_asset_name(asset_name):
#     response = requests.get(
#         url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets?nameFragment={asset_name}",
#         auth=(topdesk_username, topdesk_password),
#         headers={
#             'Content-Type': 'application/json'
#         }
#     )
#
#     if 200 <= response.status_code < 300:
#         data_set = response.json().get('dataSet')
#         if len(data_set) == 0:
#             return None
#         else:
#             return data_set[0].get('id')
#     else:
#         error_message = f"Error {response.status_code}: {response.text}"
#         raise ValueError(error_message)
#
#
# def get_asset_data(asset_id):
#     response = requests.get(
#         url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}",
#         auth=(topdesk_username, topdesk_password),
#         headers={
#             'Content-Type': 'application/json'
#         },
#     )
#
#     if 200 <= response.status_code < 300:
#         data = response.json().get('data')
#         # print(f"Successfully retrieve the asset's data: {data}")
#
#         return data
#     else:
#         error_message = f"Error {response.status_code}: {response.text}"
#         raise ValueError(error_message)
#
# def get_asset_assignment_link(asset_id):
#     response = requests.get(
#         url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments",
#         auth=(topdesk_username, topdesk_password),
#         headers={
#             'Content-Type': 'application/json'
#         },
#     )
#
#     if 200 <= response.status_code < 300:
#         try:
#             return response.json().get('persons')[0].get('linkId')
#         except:
#             return None
#     else:
#         error_message = f"Error {response.status_code}: {response.text}"
#         raise ValueError(error_message)
#
# def remove_asset_assignment_person(asset_id, link_id):
#     response = requests.delete(
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
#
# def update_asset_data(asset_id, data):
#     response = requests.post(
#         url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}",
#         auth=(topdesk_username, topdesk_password),
#         headers={
#             'Content-Type': 'application/json'
#         },
#         json=data
#     )
#
#     if 200 <= response.status_code < 300:
#         print(f"Successfully updated the asset with ID:{asset_id}")
#     else:
#         error_message = f"Error {response.status_code}: {response.text}"
#         raise ValueError(error_message)