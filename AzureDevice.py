from typing import Optional, List, Dict

class AzureDevice:
    def __init__(self, data: dict):
        self.id: Optional[str] = data.get("id")
        self.deleted_date_time: Optional[str] = data.get("deletedDateTime")
        self.account_enabled: Optional[bool] = data.get("accountEnabled")
        self.approximate_last_sign_in: Optional[str] = data.get("approximateLastSignInDateTime")
        self.compliance_expiration: Optional[str] = data.get("complianceExpirationDateTime")
        self.created_date_time: Optional[str] = data.get("createdDateTime")
        self.device_category: Optional[str] = data.get("deviceCategory")
        self.device_id: Optional[str] = data.get("deviceId")
        self.device_metadata: Optional[str] = data.get("deviceMetadata")
        self.device_ownership: Optional[str] = data.get("deviceOwnership")
        self.device_version: Optional[int] = data.get("deviceVersion")
        self.display_name: Optional[str] = data.get("displayName")
        self.domain_name: Optional[str] = data.get("domainName")
        self.enrollment_profile_name: Optional[str] = data.get("enrollmentProfileName")
        self.enrollment_type: Optional[str] = data.get("enrollmentType")
        self.external_source_name: Optional[str] = data.get("externalSourceName")
        self.is_compliant: Optional[bool] = data.get("isCompliant")
        self.is_managed: Optional[bool] = data.get("isManaged")
        self.is_rooted: Optional[bool] = data.get("isRooted")
        self.management_type: Optional[str] = data.get("managementType")
        self.manufacturer: Optional[str] = data.get("manufacturer")
        self.mdm_app_id: Optional[str] = data.get("mdmAppId")
        self.model: Optional[str] = data.get("model")
        self.on_prem_last_sync: Optional[str] = data.get("onPremisesLastSyncDateTime")
        self.on_prem_sync_enabled: Optional[bool] = data.get("onPremisesSyncEnabled")
        self.operating_system: Optional[str] = data.get("operatingSystem")
        self.operating_system_version: Optional[str] = data.get("operatingSystemVersion")
        self.physical_ids: List[str] = data.get("physicalIds", [])
        self.profile_type: Optional[str] = data.get("profileType")
        self.registration_date_time: Optional[str] = data.get("registrationDateTime")
        self.source_type: Optional[str] = data.get("sourceType")
        self.system_labels: List[str] = data.get("systemLabels", [])
        self.trust_type: Optional[str] = data.get("trustType")

        # Handle extensionAttributes
        self.extension_attributes: Dict[str, Optional[str]] = data.get("extensionAttributes", {})

        # Handle alternativeSecurityIds list
        self.alternative_security_ids: List[Dict[str, Optional[str]]] = data.get("alternativeSecurityIds", [])
