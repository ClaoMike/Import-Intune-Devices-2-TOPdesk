import requests
import auth_state

def get_devices_from_curren_page(url):
    response = requests.get(
        url=url,
        headers={
            'Authorization': f'Bearer {auth_state.access_token}',
            'Content-Type': 'application/json'
        },
    )

    if 200 <= response.status_code < 300:
        return response.json().get('value'), response.json().get('@odata.nextLink')
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def get_user_id_of_azure_device(device):
    response = requests.get(
        url=f"https://graph.microsoft.com/v1.0/devices/{device.get('id')}/registeredUsers",
        headers={
            'Authorization': f'Bearer {auth_state.access_token}',
            'Content-Type': 'application/json'
        },
    )

    if 200 <= response.status_code < 300:
        user = response.json().get('value')
        if len(user) == 0:
            print(f"No user for this device!")
            return ''
        else:
            user = user[0].get('id')
            print(f"User found: {user}")
        return user
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)