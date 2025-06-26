import requests
from env_variables import *
import auth_state  # Import the global state module

def get_access_token(scope: str):
    response = requests.post(
        url=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={
            'client_id': client_id,
            'scope':  scope,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
        }
    )

    if 200 <= response.status_code < 300:
        print("Successfully obtained access token")
        return response.json()['access_token']
    else:
        raise ValueError(f"Error {response.status_code}: {response.text}")

def get_azure_access_token():
    auth_state.access_token = get_access_token(scope='https://graph.microsoft.com/.default')

def get_microsoft_defender_access_token():
    return get_access_token(scope='https://api.securitycenter.microsoft.com/.default')