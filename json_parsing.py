def generate_intune_asset_as_json(device, asset_name, template_id):
    print(f"Creating TOPdesk asset with name: {asset_name}")

    json = {
        "name": f"{asset_name}",  # asset id
        "type_id": template_id,  # asset template
        "intune-id": device.get("id"),  # Intune ID
        "azure-ad-registered": device.get("azureADRegistered"),
        "azure-id": device.get("azureADDeviceId"),  # azure ID
        "serial-number": device.get("serialNumber"),
        "name-1": device.get("deviceName"),
        "manufacturer-1": device.get("manufacturer"),
        "model-1": device.get("model"),
        "operating-system": device.get('operatingSystem'),
        "os-version": device.get("osVersion"),
        "enrollment-date": device.get("enrolledDateTime"),
        "last-check-in": device.get("lastSyncDateTime"),
        "management-certificate-expiration-date": device.get("managementCertificateExpirationDate"),
        "ismanaged": device.get("isSupervised"),
        "imei": device.get("imei"),
        "encrypted": device.get("isEncrypted"),
        "subscriber-carrier": device.get("subscriberCarrier"),
        "total-storage": device.get("totalStorageSpaceInBytes"),
        "storage": device.get("freeStorageSpaceInBytes"),
        "compliance-status": device.get("complianceState"),
        "ownership": device.get("managedDeviceOwnerType"),
        "user-id": device.get("userId"),
    }

    return json

def generate_azure_asset_as_json(device, asset_name, template_id, userId):
    print(f"Creating TOPdesk asset with name: {asset_name}")

    json = {
        "name": f"{asset_name}",  # asset id
        "type_id": template_id,  # asset template
        "azure-id": device.get("id"),  # azure ID
        "name-1": device.get("displayName"),
        "manufacturer-1": device.get("manufacturer"),
        "model-1": device.get("model"),
        "operating-system": device.get('operatingSystem'),
        "os-version": device.get("operatingSystemVersion"),
        "enrollment-date": device.get("registrationDateTime"),
        "last-check-in": device.get("approximateLastSignInDateTime"),
        "ismanaged": device.get("isManaged"),
        "compliance-status": device.get("isCompliant"),
        "user-id": userId,
    }

    return json