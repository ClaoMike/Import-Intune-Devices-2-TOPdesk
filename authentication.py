import requests
import json
from env_variables import *

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
        return response.json()['access_token']
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)