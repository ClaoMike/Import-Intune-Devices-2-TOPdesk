from Device import *
from datetime import datetime
from typing import Optional
from TOPdeskAsset import *

class IntuneDevice(Device):
    def __init__(self, data: dict):
        super().__init__()

        # extract relevant data
        self.azure_ad_device_id: Optional[str] = data.get("azureADDeviceId")  # this will be part of the TOPdesk ID

        self.azure_ad_registered: Optional[bool] = bool(data.get("azureADRegistered"))
        self.compliance_state: Optional[str] = data.get("complianceState")
        self.enrolled_date_time: Optional[datetime] = (
            datetime.strptime(
                data.get("enrolledDateTime"),
                "%Y-%m-%dT%H:%M:%SZ") if data.get("enrolledDateTime") else None
        )
        self.free_storage_space_in_bytes: Optional[int] = int(data.get("freeStorageSpaceInBytes")) if data.get("freeStorageSpaceInBytes") else None
        self.device_name: Optional[str] = data.get("deviceName")
        self.id: Optional[str] = data.get("id")
        self.imei: Optional[str] = data.get("imei")
        self.is_encrypted: Optional[bool] = bool(data.get("isEncrypted"))
        self.is_supervised: Optional[bool] = bool(data.get("isSupervised"))
        self.last_sync_date_time: Optional[datetime] = (
            datetime.strptime(
                data.get("lastSyncDateTime"),
                "%Y-%m-%dT%H:%M:%SZ") if data.get("lastSyncDateTime") else None
        )
        self.managed_device_owner_type: Optional[str] = data.get("managedDeviceOwnerType")
        self.management_certificate_expiration_date: Optional[datetime] = (
            datetime.strptime(
                data.get("managementCertificateExpirationDate"),
                "%Y-%m-%dT%H:%M:%SZ") if data.get("managementCertificateExpirationDate") else None
        )
        self.manufacturer: Optional[str] = data.get("manufacturer")
        self.model: Optional[str] = data.get("model")
        self.operating_system: Optional[str] = data.get("operatingSystem")
        self.os_version: Optional[str] = data.get("osVersion")
        self.serial_number: Optional[str] = data.get("serialNumber")
        self.subscriber_carrier: Optional[str] = data.get("subscriberCarrier")
        self.total_storage_space_in_bytes: Optional[int] = int(data.get("totalStorageSpaceInBytes")) if data.get("totalStorageSpaceInBytes") else None

        # assigning user
        self.user_id = data.get("userId") if data.get("userId") != "" else None

        # device type
        self.device_type: Optional[Device.Type] = Device.get_device_type(
            operating_system=self.operating_system
        )

        # compute the topdesk asset name
        self.topdesk_asset_name = Device.compute_topdesk_asset_name(
            os=self.operating_system,
            device_id=self.azure_ad_device_id
        )

    def to_JSON(self):
        return {
            "name": self.topdesk_asset_name,  # asset id
            "type_id": Device.get_device_template(self.device_type),  # asset template

            "azure-ad-registered": self.azure_ad_registered,
            "azure-id": self.azure_ad_device_id,
            "compliance-status": self.compliance_state,
            "enrollment-date": self.enrolled_date_time.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.enrolled_date_time else None,
            "storage": self.free_storage_space_in_bytes,
            "name-1": self.device_name,
            "intune-id": self.id,
            "imei": self.imei,
            "encrypted": self.is_encrypted,
            "ismanaged": self.is_supervised,
            "last-check-in": self.last_sync_date_time.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.last_sync_date_time else None,
            "ownership": self.managed_device_owner_type,
            "management-certificate-expiration-date": self.management_certificate_expiration_date.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.management_certificate_expiration_date else None,
            "manufacturer-1": self.manufacturer,
            "model-1": self.model,
            "operating-system": self.operating_system,
            "os-version": self.os_version,
            "serial-number": self.serial_number,
            "subscriber-carrier": self.subscriber_carrier,
            "total-storage": self.total_storage_space_in_bytes,
            "user-id": self.user_id,
        }

    def compare_to_asset(self, asset: TOPdeskAsset):
        must_update_user = False
        new_data = {}

        if self.user_id != asset.user_id:
            must_update_user = True
            new_data["user-id"] = self.user_id

        if self.compliance_state != asset.compliance_status:
            new_data["compliance-status"] = self.compliance_state

        if self.enrolled_date_time != asset.enrollment_date:
            new_data["enrollment-date"] = self.enrolled_date_time.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.enrolled_date_time else None

        if self.free_storage_space_in_bytes != asset.storage:
            new_data["storage"] = self.free_storage_space_in_bytes
            print(f"{self.free_storage_space_in_bytes} != {asset.storage}")

        if self.device_name != asset.name_1:
            new_data["name-1"] = self.device_name

        if self.imei != asset.imei:
            new_data["imei"] = self.imei

        if self.is_encrypted != asset.encrypted:
            new_data["encrypted"] = self.is_encrypted

        if self.is_supervised != asset.is_managed:
            new_data["ismanaged"] = self.is_supervised
            print(f"{self.is_supervised} != {asset.is_managed}")

        if self.last_sync_date_time != asset.last_check_in:
            new_data["last-check-in"] = self.last_sync_date_time.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.last_sync_date_time else None

        if self.managed_device_owner_type != asset.ownership:
            new_data["ownership"] = self.managed_device_owner_type

        if self.management_certificate_expiration_date != asset.management_certificate_expiration_date:
            new_data["management-certificate-expiration-date"] = self.management_certificate_expiration_date.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.management_certificate_expiration_date else None

        if self.manufacturer != asset.manufacturer_1:
            new_data["manufacturer-1"] = self.manufacturer

        if self.model != asset.model_1:
            new_data["model-1"] = self.model

        if self.operating_system != asset.operating_system:
            new_data["operating-system"] = self.operating_system

        if self.os_version != asset.os_version:
            new_data["os-version"] = self.os_version

        if self.serial_number != asset.serial_number:
            new_data["serial-number"] = self.serial_number

        if self.subscriber_carrier != asset.subscriber_carrier:
            new_data["subscriber-carrier"] = self.subscriber_carrier

        if self.total_storage_space_in_bytes != asset.total_storage:
            new_data["total-storage"] = self.total_storage_space_in_bytes
            print(f"{self.total_storage_space_in_bytes} != {asset.total_storage}")

        return must_update_user, new_data if new_data else None