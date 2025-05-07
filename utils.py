import requests
import json
from json_parsing import *
from microsoft_methods import *
from device_methods import *
from comparisons import *

def create_asset_for(platform, device, tkn):
    # create_asset
    asset_name = generate_asset_name(platform, device)
    template_id = get_device_template(device)

    if platform == "intune":
        userId = device.get('userId')
        json = generate_intune_asset_as_json(device, asset_name, template_id)
    else:
        userId = get_user_id_of_azure_device(device, tkn)
        json = generate_azure_asset_as_json(device, asset_name, template_id, userId)

    response = requests.post(
        url="https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json=json
    )

    if 200 <= response.status_code < 300:
        asset_id = response.json().get('data').get('unid')
        print(f"Successfully created the asset with ID:{asset_id}")
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

    # assign_user
    if userId is None or userId == '':
        return

    topdesk_person_card_id = get_topdesk_user_id_by_mainframe(userId)

    if topdesk_person_card_id is None:
        return

    print(f"TOPdesk card ID: {topdesk_person_card_id}")

    assign_user_to_asset(topdesk_person_card_id, asset_id)

def update_asset(device, asset_id, platform):
    asset_data = get_asset_data(asset_id)

    is_asset_up_to_date = False

    if platform == "intune":
        is_asset_up_to_date = compare_device_with_intune(device, asset_data)
        print(f"Equal? {is_asset_up_to_date}")
        # compare users here
    else:
        pass