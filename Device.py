from typing import Optional, List, Dict
from enum import Enum
from operating_systems import *
from env_variables import *
import requests
from topdesk_methods import *

class Device:
    class Type(Enum):
        """
            Enum representing the types of devices.
        """
        COMPUTER = "COMPUTER"
        MOBILE = "MOBILE"
        DEVICE = "DEVICE"

    def __init__(self):
        # extract relevant data
        self.user_id: Optional[str] = None
        self.topdesk_asset_name: Optional[str] = None
        self.asset_id: Optional[str] = None
        self.topdesk_person_card_id: Optional[str] = None

    def to_JSON(self):
        return None

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

    def assign_user(self):
        self.topdesk_person_card_id = get_topdesk_user_id_by_mainframe(self.user_id)

        if self.topdesk_person_card_id is not None:
            assign_user(self.topdesk_person_card_id, self.asset_id)

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