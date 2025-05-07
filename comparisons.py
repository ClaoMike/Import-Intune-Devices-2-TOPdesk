from datetime import datetime, timezone

def compare_device_with_intune(device, asset):
    if asset.get("azure-ad-registered") != device.get("azureADRegistered"):
        return False

    if asset.get("name-1") != device.get("deviceName"):
        return False

    if asset.get("operating-system") != device.get('operatingSystem'):
        return False

    if asset.get("os-version") != device.get("osVersion"):
        return False

    if not compare_device_and_asset_dates(
            device.get("enrolledDateTime"),
            asset.get("enrollment-date")
    ):
        return False

    if not compare_device_and_asset_dates(
            device.get("lastSyncDateTime"),
            asset.get("last-check-in")
    ):
        return False

    if not compare_device_and_asset_dates(
            device.get("managementCertificateExpirationDate"),
            asset.get("management-certificate-expiration-date")
    ):
        return False

    if asset.get("ismanaged") != device.get("isSupervised"):
        return False

    if asset.get("encrypted") != device.get("isEncrypted"):
        return False

    if asset.get("subscriber-carrier") != device.get("subscriberCarrier"):
        return False

    if int(asset.get("total-storage")) != int(device.get("totalStorageSpaceInBytes")):
        return False

    if int(asset.get("storage")) != int(device.get("freeStorageSpaceInBytes")):
        return False

    if asset.get("compliance-status") != device.get("complianceState"):
        return False

    if asset.get("ownership") != device.get("managedDeviceOwnerType"):
        return False

    # if asset.get("user-id") != device.get("userId"):
        # return False

    return True

def compare_device_with_azure(user_id, device, asset):
    if asset.get("name-1") != device.get("displayName"):
        return False

    if asset.get("operating-system") != device.get('operatingSystem'):
        return False

    if asset.get("os-version") != device.get("operatingSystemVersion"):
        return False

    if not compare_device_and_asset_dates(
            device.get("registrationDateTime"),
            asset.get("enrollment-date")
    ):
        return False

    if not compare_device_and_asset_dates(
            device.get("approximateLastSignInDateTime"),
            asset.get("last-check-in")
    ):
        return False

    if asset.get("ismanaged") != device.get("isManaged"):
        return False

    if asset.get("compliance-status") != device.get("isCompliant"):
        return False

    if asset.get("user-id") != device.get(user_id):
        return False

    return True

def compare_device_and_asset_dates(device_date, asset_date):
    t1 = datetime.fromisoformat(asset_date)
    t1 = t1.replace(tzinfo=timezone.utc)

    t2 = datetime.strptime(device_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

    return t1 == t2