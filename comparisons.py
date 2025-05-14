# from datetime import datetime, timezone
#
# def compare_device_with_intune(device, asset):
#     if device.get("azureADRegistered") is None and asset.get("azure-ad-registered") == False:
#         pass
#     elif asset.get("azure-ad-registered") != device.get("azureADRegistered"):
#         debug_comparison("azure-ad-registered", device.get("azureADRegistered"), asset.get("azure-ad-registered"))
#         return False
#
#     if asset.get("name-1") != device.get("deviceName"):
#         debug_comparison("name-1", device.get("deviceName"), asset.get("name-1"))
#         return False
#
#     if asset.get("operating-system") != device.get('operatingSystem'):
#         debug_comparison("operating-system", device.get('operatingSystem'), asset.get("operating-system"))
#         return False
#
#     if asset.get("os-version") != device.get("osVersion"):
#         debug_comparison("os-version", device.get("osVersion"), asset.get("os-version"))
#         return False
#
#     if not compare_device_and_asset_dates(
#             device.get("enrolledDateTime"),
#             asset.get("enrollment-date")
#     ):
#         debug_comparison("enrolledDateTime", device.get("enrolledDateTime"), asset.get("enrollment-date"))
#         return False
#
#     if not compare_device_and_asset_dates(
#             device.get("lastSyncDateTime"),
#             asset.get("last-check-in")
#     ):
#         debug_comparison("lastSyncDateTime", device.get("lastSyncDateTime"), asset.get("last-check-in"))
#         return False
#
#     if not compare_device_and_asset_dates(
#             device.get("managementCertificateExpirationDate"),
#             asset.get("management-certificate-expiration-date")
#     ):
#         debug_comparison("managementCertificateExpirationDate", device.get("managementCertificateExpirationDate"), asset.get("management-certificate-expiration-date"))
#         return False
#
#     if asset.get("ismanaged") != device.get("isSupervised"):
#         debug_comparison("ismanaged", device.get("isSupervised"), asset.get("ismanaged"))
#         return False
#
#     if asset.get("encrypted") != device.get("isEncrypted"):
#         debug_comparison("encrypted", device.get("isEncrypted"), asset.get("encrypted"))
#         return False
#
#     if asset.get("subscriber-carrier") != device.get("subscriberCarrier"):
#         debug_comparison("subscriber-carrier", device.get("subscriberCarrier"), asset.get("subscriber-carrier"))
#         return False
#
#     if int(asset.get("total-storage")) != int(device.get("totalStorageSpaceInBytes")):
#         debug_comparison("total-storage", int(device.get("totalStorageSpaceInBytes")), int(asset.get("total-storage")))
#         return False
#
#     if int(asset.get("storage")) != int(device.get("freeStorageSpaceInBytes")):
#         debug_comparison("storage", int(device.get("freeStorageSpaceInBytes")), int(asset.get("storage")))
#         return False
#
#     if asset.get("compliance-status") != device.get("complianceState"):
#         debug_comparison("compliance-status", device.get("complianceState"), asset.get("compliance-status"))
#         return False
#
#     if asset.get("ownership") != device.get("managedDeviceOwnerType"):
#         debug_comparison("ownership", device.get("managedDeviceOwnerType"), asset.get("ownership"))
#         return False
#
#     return True
#
# def compare_device_with_azure(device, asset):
#     if asset.get("name-1") != device.get("displayName"):
#         debug_comparison("displayName", device, asset)
#         return False
#
#     if asset.get("operating-system") != device.get('operatingSystem'):
#         debug_comparison('operatingSystem', device, asset)
#         return False
#
#     if asset.get("os-version") != device.get("operatingSystemVersion"):
#         debug_comparison("operatingSystemVersion", device, asset)
#         return False
#
#     debug_comparison("registrationDateTime", device, asset)
#     if not compare_device_and_asset_dates(
#             device.get("registrationDateTime"),
#             asset.get("enrollment-date")
#     ):
#
#         return False
#
#     debug_comparison("approximateLastSignInDateTime", device, asset)
#     if not compare_device_and_asset_dates(
#             device.get("approximateLastSignInDateTime"),
#             asset.get("last-check-in")
#     ):
#
#         return False
#
#     if asset.get("ismanaged") != device.get("isManaged"):
#         debug_comparison("isManaged", device, asset)
#         return False
#
#     if asset.get("compliance-status") != device.get("isCompliant"):
#         debug_comparison("isCompliant", device, asset)
#         return False
#
#     return True
#
# def compare_device_and_asset_dates(device_date, asset_date):
#     if device_date is None or asset_date is None:
#         return device_date == asset_date
#
#     t1 = datetime.fromisoformat(asset_date)
#     t1 = t1.replace(tzinfo=timezone.utc)
#
#     t2 = datetime.strptime(device_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
#
#     return t1 == t2
#
# def debug_comparison(section, device, asset):
#     print(f"{section}\n{device}\n{asset}")