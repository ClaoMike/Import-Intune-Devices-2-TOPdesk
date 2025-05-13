import requests
from env_variables import *
import auth_state  # Import the global state module

def get_access_token():
    response = requests.post(
        url=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={
            'client_id': client_id,
            'scope': 'https://graph.microsoft.com/.default',
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
        }
    )

    if 200 <= response.status_code < 300:
        print("Successfully obtained access token")
        auth_state.access_token = response.json()['access_token']
    else:
        raise ValueError(f"Error {response.status_code}: {response.text}")
