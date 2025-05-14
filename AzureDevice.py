from typing import Optional, List, Dict
from Device import Device

class AzureDevice(Device):
    def __init__(self, data: dict):
        super().__init__()

        # extract relevant data
        self.device_id: Optional[str] = data.get("deviceId")  # part of the TOPdesk ID

        self.id = data.get("id")

        self.approximate_last_sign_in: Optional[str] = data.get("approximateLastSignInDateTime")
        self.compliance_expiration: Optional[str] = data.get("complianceExpirationDateTime")
        self.display_name: Optional[str] = data.get("displayName")
        self.is_compliant: Optional[bool] = data.get("isCompliant")
        self.is_managed: Optional[bool] = data.get("isManaged")
        self.manufacturer: Optional[str] = data.get("manufacturer")
        self.model: Optional[str] = data.get("model")
        self.operating_system: Optional[str] = data.get("operatingSystem")
        self.operating_system_version: Optional[str] = data.get("operatingSystemVersion")
        self.registration_date_time: Optional[str] = data.get("registrationDateTime")

        # self.user_id: Optional[str] = microsoft_methods.get_user_id_of_azure_device(entra_id)