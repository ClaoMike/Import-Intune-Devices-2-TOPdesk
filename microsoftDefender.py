import requests



def create_in_TOPdesk(self):
    response = requests.post(
        url="https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json=self.to_JSON()
    )

    if 200 <= response.status_code < 300:
        self.asset_id = response.json().get('data').get('unid')
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)