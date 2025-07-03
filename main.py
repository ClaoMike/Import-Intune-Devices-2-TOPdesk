#!/usr/bin/env python3
import time
import requests
import os
import json

from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from enum import Enum
from dotenv import load_dotenv

# Load variables from .env into environment
load_dotenv()

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

topdesk_username = os.getenv("TOPDESK_USERNAME")
topdesk_password = os.getenv("TOPDESK_PASSWORD")

topdesk_computer_category_id = os.getenv("TOPDESK_COMPUTER_CATEGORY_ID")
topdesk_mobile_category_id = os.getenv("TOPDESK_MOBILE_CATEGORY_ID")
topdesk_device_category_id = os.getenv("TOPDESK_DEVICE_CATEGORY_ID")

lenovo_client_id = os.getenv("LENOVO_CLIENT_ID")

access_token = None

device_os = {
    'Unknown',
    'AndroidForWork',
    'AndroidAOSP',
    '',
}

computer_os = {
    'Windows',
    'MacMDM',
    'macOS',
    'MacOS'
}

mobile_os = {
    'Android',
    'iOS',
    'AndroidEnterprise',
}

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

        self.last_ip_address: Optional[str] = data.get("last-ip-address")
        self.exposure_level: Optional[str] = data.get("exposure-level")
        self.last_external_ip_address: Optional[str] = data.get("last-external-ip-address")

        self.is_in_warranty = data.get("is-in-warranty")
        self.country = data.get("country-warranty")
        self.product_name = data.get("model-provided-by-the-manufacturer")
        self.warranty_expiration_date = data.get("warranty-expiration-date")
        self.number_of_days_left_until_the_warranty_expires = data.get("number-of-days-until-the-warranty-expires")

    def toString(self):
        return f"{self.id}, {self.name}, {self.intune_id}, {self.azure_ad_registered}, {self.azure_id}, {self.serial_number}, {self.name_1}, {self.manufacturer_1}, {self.model_1}, {self.operating_system}, {self.os_version}, {self.enrollment_date}, {self.last_check_in}, {self.management_certificate_expiration_date}, {self.is_managed}, {self.imei}, {self.encrypted}, {self.subscriber_carrier}, {self.total_storage}, {self.storage}, {self.compliance_status}, {self.ownership}, {self.user_id}"

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
        if self.user_id is not None and self.user_id != "":
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
            print(f"New OS detected: {operating_system} - please take action")
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
        self.operating_system_version: Optional[str] = data.get("osVersion")
        self.serial_number: Optional[str] = data.get("serialNumber")
        self.subscriber_carrier: Optional[str] = data.get("subscriberCarrier")
        self.total_storage_space_in_bytes: Optional[int] = int(data.get("totalStorageSpaceInBytes")) if data.get("totalStorageSpaceInBytes") else None

        self.last_ip_address: Optional[str] = None # "last-ip-address"
        self.exposure_level: Optional[str] = None # "exposure-level"
        self.last_external_ip_address: Optional[str] = None # "last-external-ip-address"

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

        # Warranty fields (for Lenovo devices only)
        self.is_in_warranty: Optional[bool] = None
        self.country: Optional[str] = None
        self.lenovo_product_webpage_url: Optional[str] = None
        self.product_name: Optional[str] = None
        self.warranty_expiration_date: Optional[datetime] = None
        self.number_of_days_left_until_the_warranty_expires: Optional[int] = None

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
            "os-version": self.operating_system_version,
            "serial-number": self.serial_number,
            "subscriber-carrier": self.subscriber_carrier,
            "total-storage": self.total_storage_space_in_bytes,
            "user-id": self.user_id,
            "last-ip-address": self.last_ip_address,
            "exposure-level": self.exposure_level,
            "last-external-ip-address": self.last_external_ip_address,
            # Warranty fields (for Lenovo devices only)
            "is-in-warranty": self.is_in_warranty,
            "country-warranty": self.country,
            "model-provided-by-the-manufacturer": self.product_name,
            "warranty-expiration-date": self.warranty_expiration_date.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.warranty_expiration_date else None,
            "number-of-days-until-the-warranty-expires": self.number_of_days_left_until_the_warranty_expires,
            # "": self.lenovo_product_webpage_url,
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

        if self.device_name != asset.name_1:
            new_data["name-1"] = self.device_name

        if self.imei != asset.imei:
            new_data["imei"] = self.imei

        if self.is_encrypted != asset.encrypted:
            new_data["encrypted"] = self.is_encrypted

        if self.is_supervised != asset.is_managed:
            new_data["ismanaged"] = self.is_supervised

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

        if self.operating_system_version != asset.os_version:
            new_data["os-version"] = self.operating_system_version

        if self.serial_number != asset.serial_number:
            new_data["serial-number"] = self.serial_number

        if self.subscriber_carrier != asset.subscriber_carrier:
            new_data["subscriber-carrier"] = self.subscriber_carrier

        if self.total_storage_space_in_bytes != asset.total_storage:
            new_data["total-storage"] = self.total_storage_space_in_bytes

        if self.exposure_level != asset.exposure_level:
            new_data["exposure-level"] = self.exposure_level

        if self.last_ip_address != asset.last_ip_address:
            new_data["last-ip-address"] = self.last_ip_address

        if self.last_external_ip_address != asset.last_external_ip_address:
            new_data["last-external-ip-address"] = self.last_external_ip_address

        if self.is_in_warranty != asset.is_in_warranty:
            new_data["is-in-warranty"] = self.is_in_warranty

        if self.country != asset.country:
            new_data["country-warranty"] = self.country

        if self.product_name != asset.product_name:
            new_data["model-provided-by-the-manufacturer"] = self.product_name

        if self.warranty_expiration_date != asset.warranty_expiration_date:
            new_data["warranty-expiration-date"] = self.warranty_expiration_date.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.warranty_expiration_date else None

        if self.number_of_days_left_until_the_warranty_expires != asset.number_of_days_left_until_the_warranty_expires:
            new_data["number-of-days-until-the-warranty-expires"] = self.number_of_days_left_until_the_warranty_expires

        return must_update_user, new_data if new_data else None

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
        self.is_managed: Optional[bool] = bool(data.get("isManaged"))
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

        self.last_ip_address: Optional[str] = None  # "last-ip-address"
        self.exposure_level: Optional[str] = None  # "exposure-level"
        self.last_external_ip_address: Optional[str] = None  # "last-external-ip-address"

    def to_JSON(self):
        return {
            "name": self.topdesk_asset_name,  # asset id
            "type_id": Device.get_device_template(self.device_type),  # asset template

            "azure-id": self.device_id,
            "last-check-in": self.approximate_last_sign_in.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.approximate_last_sign_in else None,
            "name-1": self.display_name,
            "ismanaged": self.is_managed,
            "manufacturer-1": self.manufacturer,
            "model-1": self.model,
            "operating-system": self.operating_system,
            "os-version": self.operating_system_version,
            "enrollment-date": self.registration_date_time.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.registration_date_time else None,
            "user-id": self.user_id,
            "last-ip-address": self.last_ip_address,
            "exposure-level": self.exposure_level,
            "last-external-ip-address": self.last_external_ip_address,
        }

    def compare_to_asset(self, asset: TOPdeskAsset):
        must_update_user = False
        new_data = {}

        if self.user_id != asset.user_id:
            must_update_user = True
            new_data["user-id"] = self.user_id

        if self.registration_date_time != asset.enrollment_date:
            new_data["enrollment-date"] = self.registration_date_time.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.registration_date_time else None

        if self.display_name != asset.name_1:
            new_data["name-1"] = self.display_name

        if self.is_managed != asset.is_managed:
            new_data["ismanaged"] = self.is_managed

        if self.approximate_last_sign_in != asset.last_check_in:
            new_data["last-check-in"] = self.approximate_last_sign_in.strftime("%Y-%m-%dT%H:%M:%S.000Z") if self.approximate_last_sign_in else None

        if self.manufacturer != asset.manufacturer_1:
            new_data["manufacturer-1"] = self.manufacturer

        if self.model != asset.model_1:
            new_data["model-1"] = self.model

        if self.operating_system != asset.operating_system:
            new_data["operating-system"] = self.operating_system

        if self.operating_system_version != asset.os_version:
            new_data["os-version"] = self.operating_system_version

        if self.exposure_level != asset.exposure_level:
            new_data["exposure-level"] = self.exposure_level

        if self.last_ip_address != asset.last_ip_address:
            new_data["last-ip-address"] = self.last_ip_address

        if self.last_external_ip_address != asset.last_external_ip_address:
            new_data["last-external-ip-address"] = self.last_external_ip_address

        return must_update_user, new_data if new_data else None

class MicrosoftDefenderDevice:
    def __init__(self, data: dict):

        # extract relevant data
        self.id: Optional[str] = data.get("aadDeviceId") # this is the Azure ID

        self.os_platform: Optional[str] = data.get("osPlatform")
        self.version: Optional[str] = data.get("version")
        self.last_ip_address: Optional[str] = data.get("lastIpAddress")
        self.last_external_ip_address: Optional[str] = data.get("lastExternalIpAddress")
        self.exposure_level: Optional[str] = data.get("exposureLevel")

class LenovoDevice:
    def __init__(self, data: dict):
        self.serial_number: Optional[str] = data.get("Serial")
        self.is_in_warranty: Optional[bool] = data.get("InWarranty")
        self.country: Optional[str] = data.get("Country")

        product = data.get("Product")
        if product is not None:
            self.lenovo_product_webpage_url: Optional[str] = f"https://pcsupport.lenovo.com/us/en/products/{product}/warranty"
            tokens = product.split("/")
            if len(tokens) > 2:
                self.product_name: Optional[str] = tokens[2]
            else:
                self.product_name: Optional[str] = tokens[-1]
        else:
            self.lenovo_product_webpage_url = None
            self.product_name = None

        self.warranty_expiration_date: Optional[datetime] = None
        latest_warranty_date = datetime.min.replace(tzinfo=timezone.utc)
        warranties = data.get("Warranty")
        if warranties is not None:
            for warranty in warranties:
                end_date = datetime.strptime(warranty["End"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if end_date > latest_warranty_date:
                    latest_warranty_date = end_date
            self.warranty_expiration_date = latest_warranty_date

        current_date = datetime.now(timezone.utc)
        self.number_of_days_left_until_the_warranty_expires: Optional[int] = (self.warranty_expiration_date - current_date).days + 1 if self.is_in_warranty else 0

        # remove this
        # self.warranty_expiration_date = None

def get_access_token(scope: str):
    response = requests.post(
        url=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={
            'client_id': client_id,
            'scope':  scope,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
        }
    )

    if 200 <= response.status_code < 300:
        print("Successfully obtained access token")
        return response.json()['access_token']
    else:
        raise ValueError(f"Error {response.status_code}: {response.text}")

def get_azure_access_token():
    global access_token
    access_token = get_access_token(scope='https://graph.microsoft.com/.default')

def get_microsoft_defender_access_token():
    return get_access_token(scope='https://api.securitycenter.microsoft.com/.default')


def fetch_all_assets(template_id, page_size=1000):
    all_assets = []
    page_start = 0
    has_more = True

    fields = [
        "name", "intune-id", "azure-ad-registered", "azure-id", "serial-number",
        "name-1", "manufacturer-1", "model-1", "operating-system", "os-version",
        "enrollment-date", "last-check-in", "management-certificate-expiration-date",
        "ismanaged", "imei", "encrypted", "subscriber-carrier", "total-storage",
        "storage", "compliance-status", "ownership", "user-id"
    ]

    base_url = "https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets"
    auth = (topdesk_username, topdesk_password)
    headers = {
        "Accept": "application/x.topdesk-am-assets-v2+json",
        "Content-Type": "application/json"
    }

    fields_param = ",".join(fields)

    while has_more:
        params = {
            "templateId": template_id,
            "fields": fields_param,
            "pageStart": page_start,
            "pageSize": page_size
        }

        response = requests.get(base_url, headers=headers, params=params, auth=auth)
        if response.status_code not in [200, 206]:
            raise Exception(f"Error {response.status_code}: {response.text}")

        data = response.json()
        assets_as_json = data.get("dataSet")
        assets = [TOPdeskAsset(asset) for asset in assets_as_json]
        all_assets.extend(assets)
        print(f"[{template_id}] Fetched {len(assets)} assets (total so far: {len(all_assets)})")

        has_more = response.status_code == 206
        page_start += page_size

    return all_assets

def create_assets(devices):
    if not devices:
        return

    print(f"Creating assets for {len(devices)} devices")

    def create_and_assign(device):
        device.create_in_TOPdesk()
        device.assign_user()
        return device.topdesk_asset_name

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(create_and_assign, device): device for device in devices}

        for future in as_completed(futures):
            device = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"[✗] Failed to create asset for device: {device.topdesk_asset_name} → {e}")

def delete_assets(assets):
    if len(assets) != 0:
        print(f"Deleting {len(assets)} assets")

        asset_ids_to_delete = [asset.id for asset in assets if asset.id is not None]

        response = requests.post(
            url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/delete",
            auth=(topdesk_username, topdesk_password),
            headers={
                'Content-Type': 'application/json'
            },
            json={
                'unids': asset_ids_to_delete
            }
        )

        if 200 <= response.status_code < 300:
            return
        else:
            error_message = f"Error {response.status_code}: {response.text}"
            raise ValueError(error_message)

from concurrent.futures import ThreadPoolExecutor, as_completed

def update_assets(assets):
    print(f"Updating {len(assets)} assets...")

    def process_update(asset_id, must_update_user, new_data):
        try:
            if new_data is not None:
                update_asset(asset_id, new_data)

            if must_update_user:
                # unlink current person card, if any
                link = get_asset_assignment_link(asset_id)
                if link is not None:
                    remove_asset_assignment_person(asset_id, link)

                # link new user
                new_user_id = new_data.get("user-id")
                if new_user_id is not None and new_user_id != "":
                    topdesk_person_card_id = get_topdesk_user_id_by_mainframe(new_user_id)
                    assign_user(topdesk_person_card_id, asset_id)

            return f"[✓] Updated asset {asset_id}"
        except Exception as e:
            return f"[✗] Failed to update {asset_id}: {e} \n {new_data}"

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(process_update, asset_id, must_update_user, new_data): asset_id
            for asset_id, (must_update_user, new_data) in assets.items()
        }

        for future in as_completed(futures):
            print(future.result())


def filter_assets_and_devices(devices, assets):
    device_keys = set(devices.keys())
    asset_keys = set(assets.keys())

    # assets that need to be created
    devices_to_create = device_keys - asset_keys
    devices_to_create_list = [devices[key] for key in devices_to_create]

    # assets that must be deleted
    assets_to_delete = asset_keys - device_keys
    assets_to_delete_list = [assets[key] for key in assets_to_delete]

    matching_keys = device_keys & asset_keys

    print(f"Assets to be created: {len(devices_to_create_list)}")
    print(f"Assets to be deleted: {len(assets_to_delete_list)}")
    print(f"Assets to be compared: {len(matching_keys)}")

    assets_to_be_updated = {}
    for key in matching_keys:
        device = devices[key]
        asset = assets[key]
        must_update_user, new_data = device.compare_to_asset(asset)

        if must_update_user == True or new_data is not None:
            assets_to_be_updated[asset.id] = (must_update_user, new_data) # NEEDS THE TOPDESK ASSET ID, NOT ITS NAME

    print(f"Assets to be updated: {len(assets_to_be_updated)}")

    return devices_to_create_list, assets_to_delete_list, assets_to_be_updated

def update_asset(asset_id, new_data):
    response = requests.post(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json=new_data
    )

    if 200 <= response.status_code < 300:
        return
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        print(error_message)
        raise ValueError(error_message)

def get_asset_assignment_link(asset_id):
    response = requests.get(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
    )

    if 200 <= response.status_code < 300:
        try:
            return response.json().get('persons')[0].get('linkId')
        except:
            return None
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def remove_asset_assignment_person(asset_id, link_id):
    response = requests.delete(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments/{link_id}",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
    )

    if 200 <= response.status_code < 300:
        print("Successfully deleted the assignment link!")
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def get_topdesk_user_id_by_mainframe(user_id):
    response = requests.get(
        url=f"https://dlfseeds.topdesk.net/tas/api/persons?query=mainframeLoginName=={user_id}",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        }
    )

    if 200 <= response.status_code < 300:
        if response.text != '':
            if len(response.json()) == 0:
                return None
            person_card = response.json()[0]
            if person_card.get('status') != 'personArchived':
                return person_card.get('id')
            else:
                return None
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def assign_user(topdesk_person_card_id, asset_id):
    response = requests.put(
        url=f"https://dlfseeds.topdesk.net/tas/api/assetmgmt/assets/{asset_id}/assignments",
        auth=(topdesk_username, topdesk_password),
        headers={
            'Content-Type': 'application/json'
        },
        json={
            "linkToId": topdesk_person_card_id,
            "linkType": "person"
        }
    )

    if 200 <= response.status_code < 300:
        return
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

def get_devices_from_curren_page(url):
    response = requests.get(
        url=url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
    )
    if 200 <= response.status_code < 300:
        return response.json().get('value'), response.json().get('@odata.nextLink')
    else:
        raise ValueError(f"Error {response.status_code}: {response.text}")

def batch_get_registered_users(device_ids):
    url = "https://graph.microsoft.com/v1.0/$batch"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    requests_payload = [
        {
            "id": device_id,
            "method": "GET",
            "url": f"/devices/{device_id}/registeredUsers"
        }
        for device_id in device_ids
    ]

    all_results = {}
    for i in range(0, len(requests_payload), 20):
        chunk = requests_payload[i:i + 20]
        response = requests.post(url, headers=headers, json={"requests": chunk})
        data = response.json()

        for item in data.get("responses", []):
            dev_id = item.get("id")
            if item["status"] == 200:
                users = item["body"].get("value", [])
                user_id = users[0].get("id") if users else None
                all_results[dev_id] = user_id
            else:
                all_results[dev_id] = None
    return all_results

def fetch_all_devices_from_platform(platform, url, azure_queue=None, azure_devices=None, intune_devices=None):
    next_page = url
    start_time = time.time()

    while next_page:
        if time.time() - start_time > 3000:
            get_azure_access_token()
            start_time = time.time()

        current_page, next_page = get_devices_from_curren_page(next_page)

        for device in current_page:
            if platform == "azure":
                az_device = AzureDevice(device)
                azure_devices.append(az_device)
                azure_queue.put(device)
            elif platform == "intune":
                intune_devices.append(IntuneDevice(device))

    if platform == "azure":
        azure_queue.put(None)

def user_batch_worker(device_queue, result_dict):
    buffer = []
    while True:
        item = device_queue.get()
        if item is None:
            if buffer:
                ids = [d.get("id") for d in buffer if d.get("id")]
                result_dict.update(batch_get_registered_users(ids))
            break

        buffer.append(item)
        if len(buffer) == 20:
            ids = [d.get("id") for d in buffer if d.get("id")]
            result_dict.update(batch_get_registered_users(ids))
            buffer.clear()

def fetch_devices():
    get_azure_access_token()

    platforms = {
        "intune": "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices",
        "azure": "https://graph.microsoft.com/v1.0/devices"
    }

    azure_devices = []
    intune_devices = []
    azure_user_map = {}
    azure_queue = Queue()

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(
                fetch_all_devices_from_platform,
                platform,
                url,
                azure_queue if platform == "azure" else None,
                azure_devices if platform == "azure" else None,
                intune_devices if platform == "intune" else None
            ): platform
            for platform, url in platforms.items()
        }

        # Start user lookup thread
        user_thread = Thread(target=user_batch_worker, args=(azure_queue, azure_user_map))
        user_thread.start()

        # Wait for both fetch threads
        for future in as_completed(futures):
            platform = futures[future]
            try:
                future.result()
                print(f"[✓] Finished fetching {platform} devices.")
            except Exception as e:
                print(f"[✗] Error fetching {platform}: {e}")

        user_thread.join()

    print(f"\n[Summary]")
    print(f"Azure Devices: {len(azure_devices)}")
    print(f"Intune Devices: {len(intune_devices)}")
    print(f"Azure Devices with User IDs: {len(azure_user_map)}")

    # assigning users for azure devices
    for azure_device in azure_devices:
        azure_device.user_id = azure_user_map.get(azure_device.id)

    devices = {}

    # ORDER IS VERY IMPORTANT HERE< AZURE FIRST< INTUNE AFTER, INTUNE MUST OVERWRITE SOME OF AZURE
    # Add Azure devices
    for device in azure_devices:
        if device.topdesk_asset_name:
            devices[device.topdesk_asset_name] = device

    # Add Intune devices (overwrites if name matches)
    for device in intune_devices:
        if device.topdesk_asset_name:
            devices[device.topdesk_asset_name] = device

    return devices

def get_microsoft_defender_devices():
    response = requests.get(
        url=f"https://api.security.microsoft.com/api/machines",
        headers={
        'Authorization': f'Bearer {get_microsoft_defender_access_token()}',
        'Content-Type': 'application/json'
        },
    )

    if 200 <= response.status_code < 300:
        microsoft_defender_devices = response.json().get('value')
        microsoft_defender_devices_with_azure_id = [device for device in microsoft_defender_devices if device.get("aadDeviceId") is not None]
        microsoft_defender_devices_with_azure_id_as_dictionary = {}

        for data in microsoft_defender_devices_with_azure_id:
            new_device = MicrosoftDefenderDevice(data=data)
            if new_device.id in microsoft_defender_devices_with_azure_id_as_dictionary:
                print(f"Duplicate device: {new_device.id}")
            microsoft_defender_devices_with_azure_id_as_dictionary[new_device.id] = new_device

        return microsoft_defender_devices_with_azure_id_as_dictionary
    else:
        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)


def update_devices_with_microsoft_defender_data(devices: dict):
    microsoft_defender_devices = get_microsoft_defender_devices()
    for azure_id, md in microsoft_defender_devices.items():
        device_id = None

        for prefix in ["COMPUTER", "MOBILE", "DEVICE"]:
            try_device_id = f"{prefix}-{azure_id}"
            if try_device_id in devices:
                device_id = try_device_id
                break

        if device_id is not None:
            devices[device_id].operating_system = md.os_platform
            devices[device_id].operating_system_version = md.version
            devices[device_id].exposure_level = md.exposure_level
            devices[device_id].last_ip_address = md.last_ip_address
            devices[device_id].last_external_ip_address = md.last_external_ip_address

    return devices

def get_lenovo_warranties(params: str):
    url = f"https://supportapi.lenovo.com/v2.5/warranty?{params}"
    headers = {
        "ClientID": lenovo_client_id,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, headers=headers)

    if 200 <= response.status_code < 300:
        return [LenovoDevice(item) for item in response.json()]
    else:
        raise ValueError(f"Error {response.status_code}: {response.text}")

def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

def fetch_devices_and_assets_in_parallel():
    assets = []
    topdesk_categories = [
        topdesk_computer_category_id,
        topdesk_mobile_category_id,
        topdesk_device_category_id
    ]

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []

        # Start asset fetching for each category
        for category_id in topdesk_categories:
            futures.append(executor.submit(fetch_all_assets, category_id))

        # Start fetching Azure and Intune devices
        device_future = executor.submit(fetch_devices)

        # Wait for asset futures
        for future in as_completed(futures):
            try:
                result = future.result()
                assets.extend(result)
            except Exception as e:
                print(f"[✗] Error fetching assets: {e}")

        # Wait for devices
        devices = device_future.result()

    # sync with Microsoft Defender
    update_devices_with_microsoft_defender_data(devices)

    lenovo_warranties = []

    serial_to_device = {
        device.serial_number: key
        for key, device in devices.items()
        if hasattr(device, 'serial_number')
    }

    serials = [
        f"Serial={device.serial_number}"
        for _, device in devices.items()
        if hasattr(device, 'manufacturer') and device.manufacturer == "LENOVO"
           and hasattr(device, 'serial_number') and device.serial_number is not None
    ]

    for batch in chunked(serials, 100):
        params = "&".join(batch)
        lenovo_warranties.extend(get_lenovo_warranties(params))

    for warranty in lenovo_warranties:
        device = devices[serial_to_device[warranty.serial_number]]
        device.is_in_warranty = warranty.is_in_warranty
        device.country = warranty.country
        device.lenovo_product_webpage_url = warranty.lenovo_product_webpage_url
        device.product_name = warranty.product_name
        device.warranty_expiration_date = warranty.warranty_expiration_date
        device.number_of_days_left_until_the_warranty_expires = warranty.number_of_days_left_until_the_warranty_expires

    # Transforming the assets into dictionary as well
    all_assets_as_dict = {}
    for asset in assets:
        if asset.name:
            all_assets_as_dict[asset.name] = asset

    print(f"\n[✓] Total assets fetched: {len(assets)}")
    print(f"[✓] Total devices fetched: {len(devices)}")

    return devices, all_assets_as_dict

def update_TOPdesk(to_create_list, to_delete_list, to_update_list):
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_label = {
            executor.submit(create_assets, to_create_list): "Create",
            executor.submit(delete_assets, to_delete_list): "Delete",
            executor.submit(update_assets, to_update_list): "Update"
        }

        for future in as_completed(future_to_label):
            label = future_to_label[future]
            try:
                future.result()
                print(f"[✓] {label} task completed.")
            except Exception as e:
                print(f"[✗] {label} task failed: {e}")

start_time = time.time()

# Fetch devices and assets
all_devices, all_assets = fetch_devices_and_assets_in_parallel()

# Filter to-dos
devices_to_create_list, assets_to_delete_list, assets_to_be_updated = filter_assets_and_devices(
    all_devices,
    all_assets
)

# Update TOPdesk
update_TOPdesk(devices_to_create_list, assets_to_delete_list, assets_to_be_updated)

end_time = time.time()
elapsed = end_time - start_time

print(f"\n[✓] Total time: {elapsed:.2f} seconds")

