from Device import *

class IntuneDevice(Device):
    def __init__(self, data: dict):
        super().__init__()

        # extract relevant data
        self.azure_ad_device_id: Optional[str] = data.get("azureADDeviceId")  # this will be part of the TOPdesk ID

        self.azure_ad_registered: Optional[bool] = data.get("azureADRegistered")
        self.compliance_state: Optional[str] = data.get("complianceState")
        self.enrolled_date_time: Optional[str] = data.get("enrolledDateTime")
        self.free_storage_space_in_bytes: Optional[int] = data.get("freeStorageSpaceInBytes")
        self.device_name: Optional[str] = data.get("deviceName")
        self.id: Optional[str] = data.get("id")
        self.imei: Optional[str] = data.get("imei")
        self.is_encrypted: Optional[bool] = data.get("isEncrypted")
        self.is_supervised: Optional[bool] = data.get("isSupervised")
        self.last_sync_date_time: Optional[str] = data.get("lastSyncDateTime")
        self.managed_device_owner_type: Optional[str] = data.get("managedDeviceOwnerType")
        self.management_certificate_expiration_date: Optional[str] = data.get("managementCertificateExpirationDate")
        self.manufacturer: Optional[str] = data.get("manufacturer")
        self.model: Optional[str] = data.get("model")
        self.operating_system: Optional[str] = data.get("operatingSystem")
        self.os_version: Optional[str] = data.get("osVersion")
        self.serial_number: Optional[str] = data.get("serialNumber")
        self.subscriber_carrier: Optional[str] = data.get("subscriberCarrier")
        self.total_storage_space_in_bytes: Optional[int] = data.get("totalStorageSpaceInBytes")

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
            "enrollment-date": self.enrolled_date_time,
            "storage": self.free_storage_space_in_bytes,
            "name-1": self.device_name,
            "intune-id": self.id,
            "imei": self.imei,
            "encrypted": self.is_encrypted,
            "ismanaged": self.is_supervised,
            "last-check-in": self.last_sync_date_time,
            "ownership": self.managed_device_owner_type,
            "management-certificate-expiration-date": self.management_certificate_expiration_date,
            "manufacturer-1": self.manufacturer,
            "model-1": self.model,
            "operating-system": self.operating_system,
            "os-version": self.os_version,
            "serial-number": self.serial_number,
            "subscriber-carrier": self.subscriber_carrier,
            "total-storage": self.total_storage_space_in_bytes,
            "user-id": self.user_id,
        }