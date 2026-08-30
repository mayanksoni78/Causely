import uuid
import requests
from src.connectors.base import SourceConnector, PermissionReport, ConnectorStatus, EvidenceQuery, EvidenceChunk

class Auth0Connector(SourceConnector):
    def __init__(self, connector_id: str, tenant_id: str, config: dict):
        self.connector_id = connector_id
        self.tenant_id = tenant_id
        self.domain = config.get("domain", "").strip("/")
        if not self.domain.startswith("http"):
            self.domain = f"https://{self.domain}"
        self.client_id = config.get("client_id", "")
        self.client_secret = config.get("client_secret", "")

    def check_permissions(self) -> PermissionReport:
        return PermissionReport(self.connector_id, True, ["read_logs", "read_users"], [])

    def list_capabilities(self) -> list[str]:
        return ["auth_logs", "user_metadata"]

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:
        return [] # Placeholder

    def health_check(self) -> ConnectorStatus:
        try:
            resp = requests.post(
                f"{self.domain}/oauth/token",
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "audience": f"{self.domain}/api/v2/",
                    "grant_type": "client_credentials"
                },
                timeout=5
            )
            if resp.status_code == 200:
                return ConnectorStatus(True, "Connected to Auth0")
            return ConnectorStatus(False, f"Auth0 Auth Failed: {resp.status_code}")
        except Exception as e:
            return ConnectorStatus(False, str(e))
