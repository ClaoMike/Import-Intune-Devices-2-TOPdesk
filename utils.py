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
    asset_name = generate_asset_name(platform, device)
    template_id = get_device_template(device)

    is_asset_up_to_date = True
    is_user_the_same = True

    if platform == "intune":
        # is_asset_up_to_date = compare_device_with_intune(device, asset_data)
        # print(f"Equal? {is_asset_up_to_date}")
        print()
        print(f"{asset_data.get('name')} vs. {asset_name}")
        print(f"{asset_data.get('user-id')} vs. {device.get('userId')}")

        if asset_data.get("user-id") != device.get("userId"):
            print("Not the same user!")
            print(f"{asset_data.get('user-id')} vs. {device.get('userId')}")
            is_user_the_same = False

        # if not is_asset_up_to_date:
        #     updated_asset = generate_intune_asset_as_json(device, asset_name, template_id)
        #     print(updated_asset)
        #     update_asset_data(asset_id, updated_asset)

        if not is_user_the_same:
            print("----------------------------------------------")
            print(asset_data)
            print(device)
            # get current link
            link_id = get_asset_assignment_link(asset_id)

            if link_id is not None:
                # remove link
                remove_asset_assignment_person(asset_id, link_id)
                print(f"Removing the link: {link_id}")

            # update asset with new user id (eventually empty)
            new_user_data = generate_new_user_asset_data_as_json(asset_name, template_id, device.get("userId"))
            print(new_user_data)
            update_asset_data(asset_id, new_user_data)

            if device.get("userId") != '':
                print("Adding the link")
                person_card_id = get_topdesk_user_id_by_mainframe(device.get("userId"))

                # link new user
                assign_user_to_asset(person_card_id, asset_id)
            print("===========================================")
    else:
        pass