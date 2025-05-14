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

def filter_assets_and_devices(devices, assets):
    device_keys = set(devices.keys())
    asset_keys = set(assets.keys())

    # assets that need to be created
    devices_to_create = device_keys - asset_keys
    devices_to_create_list = [devices[key] for key in devices_to_create]

    # assets that must be deleted
    assets_to_delete = asset_keys - device_keys
    assets_to_delete_list = [assets[key] for key in assets_to_delete]

    matching_keys = device_keys & asset_keys

    print(f"Assets to be created: {len(devices_to_create_list)}")
    print(f"Assets to be deleted: {len(assets_to_delete_list)}")
    print(f"Assets to be compared: {len(matching_keys)}")

    assets_to_be_updated = {}
    for key in matching_keys:
        device = devices[key]
        asset = assets[key]
        must_update_user, new_data = device.compare_to_asset(asset)

        if must_update_user == True or new_data is not None:
            assets_to_be_updated[asset.id] = (must_update_user, new_data) # NEEDS THE TOPDESK ASSET ID, NOT ITS NAME

    print(f"Assets to be updated: {len(assets_to_be_updated)}")

    return devices_to_create_list, assets_to_delete_list, assets_to_be_updated

def update_assets(assets):
    for asset_id, (must_update_user, new_data) in assets.items():
        print(f"{asset_id} → {must_update_user} → {new_data}")

        if new_data is not None:
            update_asset(asset_id, new_data)

        # by this point, the asset has its user id update, see above
        if must_update_user == True:
            # unlink current person card, if any
            link = get_asset_assignment_link(asset_id)
            if link is not None:
                remove_asset_assignment_person(asset_id, link)

            # link new user
            topdesk_person_card_id = get_topdesk_user_id_by_mainframe(new_data.get("user-id"))
            assign_user(topdesk_person_card_id, asset_id)

def update_asset(asset_id, new_data):
    response = requests.post(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json=new_data
    )

    if 200 <= response.status_code < 300:
        return
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def get_asset_assignment_link(asset_id):
    response = requests.get(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
    )

    if 200 <= response.status_code < 300:
        try:
            return response.json().get('persons')[0].get('linkId')
        except:
            return None
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def remove_asset_assignment_person(asset_id, link_id):
    response = requests.delete(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments/{link_id}",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
    )

    if 200 <= response.status_code < 300:
        print("Successfully deleted the assignment link!")
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def get_topdesk_user_id_by_mainframe(user_id):
    response = requests.get(
        url=f"https://dlfseeds.topdesk.net/tas/api/persons?query=mainframeLoginName=={user_id}",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        }
    )

    if 200 <= response.status_code < 300:
        if response.text != '':
            if len(response.json()) == 0:
                return None
            person_card = response.json()[0]
            if person_card.get('status') != 'personArchived':
                return person_card.get('id')
            else:
                return None
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def assign_user(topdesk_person_card_id, asset_id):
    response = requests.put(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json={
            "linkToId": topdesk_person_card_id,
            "linkType": "person"
        }
    )

    if 200 <= response.status_code < 300:
        return
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)