from Device import *
from datetime import datetime
from typing import Optional

class AzureDevice(Device):
    def __init__(self, data: dict):
        super().__init__()

        # extract relevant data
        self.device_id: Optional[str] = data.get("deviceId")  # part of the TOPdesk ID
        self.id = data.get("id") # needed to fetch the user ID !!

        self.approximate_last_sign_in: Optional[datetime] = (
            datetime.strptime(
                data.get("approximateLastSignInDateTime"),
                "%Y-%m-%dT%H:%M:%SZ") if data.get("approximateLastSignInDateTime") else None
        )
        self.display_name: Optional[str] = data.get("displayName")
        self.is_compliant: Optional[bool] = data.get("isCompliant")
        self.is_managed: Optional[bool] = data.get("isManaged")
        self.manufacturer: Optional[str] = data.get("manufacturer")
        self.model: Optional[str] = data.get("model")
        self.operating_system: Optional[str] = data.get("operatingSystem")
        self.operating_system_version: Optional[str] = data.get("operatingSystemVersion")
        self.registration_date_time: Optional[datetime] = (
            datetime.strptime(
                data.get("registrationDateTime"),
                "%Y-%m-%dT%H:%M:%SZ") if data.get("registrationDateTime") else None
        )

        self.device_type: Optional[Device.Type] = Device.get_device_type(
            operating_system=self.operating_system
        )

        # compute the topdesk asset name
        self.topdesk_asset_name = Device.compute_topdesk_asset_name(
            os=self.operating_system,
            device_id=self.device_id
        )

    def to_JSON(self):
        return {
            "name": self.topdesk_asset_name,  # asset id
            "type_id": Device.get_device_template(self.device_type),  # asset template

            "azure-id": self.device_id,
            "last-check-in": self.approximate_last_sign_in.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.approximate_last_sign_in else None,
            "name-1": self.display_name,
            "compliance-status": self.is_compliant,
            "ismanaged": self.is_managed,
            "manufacturer-1": self.manufacturer,
            "model-1": self.model,
            "operating-system": self.operating_system,
            "os-version": self.operating_system_version,
            "enrollment-date": self.registration_date_time.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.registration_date_time else None,
            "user-id": self.user_id,
        }