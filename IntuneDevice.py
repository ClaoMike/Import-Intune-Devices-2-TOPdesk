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

        # compute the topdesk asset name
        self.topdesk_asset_name = Device.compute_topdesk_asset_name(
            os=self.operating_system,
            device_id=self.azure_ad_device_id
        )