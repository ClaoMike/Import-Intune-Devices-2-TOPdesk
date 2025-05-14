from typing import Optional
from datetime import datetime

class TOPdeskAsset:
    def __init__(self, data: dict):
        self.id: Optional[str] = data.get("unid")
        self.name: Optional[str] = data.get("name")
        self.intune_id: Optional[str] = data.get("intune-id")
        self.azure_ad_registered: Optional[bool] = bool(data.get("azure-ad-registered"))
        self.azure_id: Optional[str] = data.get("azure-id")
        self.serial_number: Optional[str] = data.get("serial-number")
        self.name_1: Optional[str] = data.get("name-1")
        self.manufacturer_1: Optional[str] = data.get("manufacturer-1")
        self.model_1: Optional[str] = data.get("model-1")
        self.operating_system: Optional[str] = data.get("operating-system")
        self.os_version: Optional[str] = data.get("os-version")
        self.enrollment_date: Optional[datetime] = datetime.strptime(data.get("enrollment-date"), "%Y-%m-%dT%H:%M:%S.%f") if data.get("enrollment-date") else None
        self.last_check_in: Optional[datetime] = datetime.strptime(data.get("last-check-in"), "%Y-%m-%dT%H:%M:%S.%f") if data.get("last-check-in") else None
        self.management_certificate_expiration_date: Optional[datetime] = datetime.strptime(data.get("management-certificate-expiration-date"), "%Y-%m-%dT%H:%M:%S.%f") if data.get("management-certificate-expiration-date") else None
        self.is_managed: Optional[bool] = bool(data.get("ismanaged"))
        self.imei: Optional[str] = data.get("imei")
        self.encrypted: Optional[bool] = bool(data.get("encrypted"))
        self.subscriber_carrier: Optional[str] = data.get("subscriber-carrier")
        self.total_storage: Optional[int] = int(data.get("total-storage")) if data.get("total-storage") else None
        self.storage: Optional[int] = int(data.get("storage")) if data.get("storage") else None
        self.compliance_status: Optional[str] = data.get("compliance-status")
        self.ownership: Optional[str] = data.get("ownership")
        self.user_id: Optional[str] = data.get("user-id")

    def toString(self):
        return f"{self.id}, {self.name}, {self.intune_id}, {self.azure_ad_registered}, {self.azure_id}, {self.serial_number}, {self.name_1}, {self.manufacturer_1}, {self.model_1}, {self.operating_system}, {self.os_version}, {self.enrollment_date}, {self.last_check_in}, {self.management_certificate_expiration_date}, {self.is_managed}, {self.imei}, {self.encrypted}, {self.subscriber_carrier}, {self.total_storage}, {self.storage}, {self.compliance_status}, {self.ownership}, {self.user_id}"

