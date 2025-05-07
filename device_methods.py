import json
from operating_systems import *
from topdesk_methods import *
from device_types import *

def get_device_type(operating_system: str):
    if operating_system in device_os:  # Skip these
        return DeviceType.DEVICE
    elif operating_system in computer_os:
        return DeviceType.COMPUTER
    elif operating_system in mobile_os:
        return DeviceType.MOBILE
    else:
        print("New OS detected - please take action")
        return None

def generate_asset_name(platform, device):
    if platform == "intune":
        id = device.get('azureADDeviceId')
    else:
        id = device.get('id')

    operating_system = device.get('operatingSystem')
    type = get_device_type(operating_system).value

    return f"{type}-{id}"

def get_device_template(device):
    operating_system = device.get('operatingSystem')
    type = get_device_type(operating_system)

    if type is DeviceType.DEVICE:  # Skip these
        return topdesk_device_category_id
    elif type is DeviceType.COMPUTER:
        return topdesk_computer_category_id
    elif type is DeviceType.MOBILE:
        return topdesk_mobile_category_id
    else:
        print("New OS detected - please take action")
        return None