import requests
from env_variables import *

def assign_user_to_asset(person_card_id, asset_id):
    response = requests.put(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json={
            "linkToId": person_card_id,
            "linkType": "person"
        }
    )

    if 200 <= response.status_code < 300:
        print("Successfully assigned user to asset")
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
            print(response.json())

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

def search_for_topdesk_asset_by_asset_name(asset_name):
    response = requests.get(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets?nameFragment={asset_name}",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        }
    )

    if 200 <= response.status_code < 300:
        data_set = response.json().get('dataSet')
        if len(data_set) == 0:
            return None
        else:
            return data_set[0].get('id')
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)