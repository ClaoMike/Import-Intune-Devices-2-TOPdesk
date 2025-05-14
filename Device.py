from typing import Optional, List, Dict
from enum import Enum
from operating_systems import *
from env_variables import *

class Device:
    class Type(Enum):
        """
            Enum representing the types of devices.
        """
        COMPUTER = "COMPUTER"
        MOBILE = "MOBILE"
        DEVICE = "DEVICE"

    def __init__(self, data):
        # extract relevant data
        self.user_id: Optional[str] = None
        self.topdesk_asset_name: Optional[str] = None

    @staticmethod
    def compute_topdesk_asset_name(os: str, device_id: str) -> str:
        return f"{Device.get_device_type(os).value}-{device_id}"

    @staticmethod
    def get_device_type(operating_system: str):
        if operating_system in device_os:  # Skip these
            return Device.Type.DEVICE
        elif operating_system in computer_os:
            return Device.Type.COMPUTER
        elif operating_system in mobile_os:
            return Device.Type.MOBILE
        else:
            print("New OS detected - please take action")
            return None

    @staticmethod
    def get_device_template(type: Type):
        if type is Device.Type.DEVICE:
            return topdesk_device_category_id
        elif type is Device.Type.COMPUTER:
            return topdesk_computer_category_id
        elif type is Device.Type.MOBILE:
            return topdesk_mobile_category_id
        else:
            print("New OS detected - please take action")
            return None