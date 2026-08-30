import httpx
import uuid
from typing import Dict, Any
from src.connectors.base import SourceConnector, PermissionReport, ConnectorStatus, EvidenceQuery, EvidenceChunk

class RazorpayConnector(SourceConnector):
    def __init__(self, source_id: str, tenant_id: str, config: Dict[str, Any]):
        self.source_id = source_id
        self.tenant_id = tenant_id
        self.api_key = config.get("api_key", "")
        self.api_secret = config.get("api_secret", "")
        self.base_url = "https://api.razorpay.com/v1"

    def check_permissions(self) -> PermissionReport:
        return PermissionReport(
            connector_id=self.source_id,
            is_read_only=True,
            granted_scopes=["payments.read", "refunds.read", "events.read"],
            warnings=[]
        )

    def list_capabilities(self) -> list[str]:
        return ["Payments", "Refunds", "Events"]

    def health_check(self) -> ConnectorStatus:
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(
                    f"{self.base_url}/payments", 
                    auth=(self.api_key, self.api_secret),
                    params={"count": 1}
                )
                if res.status_code in [200, 401]: 
                    # If 401, they are invalid keys but the API is reachable. 
                    # For a true health check we should fail on 401.
                    if res.status_code == 401:
                        return ConnectorStatus(healthy=False, message="Invalid API Key or Secret")
                    return ConnectorStatus(healthy=True, message="Connected")
                return ConnectorStatus(healthy=False, message=f"HTTP {res.status_code}")
        except Exception as e:
            return ConnectorStatus(healthy=False, message=str(e))

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:
        chunks = []
        try:
            # We strictly limit the pull
            with httpx.Client(timeout=10.0) as client:
                res = client.get(
                    f"{self.base_url}/payments", 
                    auth=(self.api_key, self.api_secret),
                    params={"count": 50}
                )
                if res.status_code == 200:
                    data = res.json()
                    for item in data.get("items", []):
                        # Focus on failed payments for incident investigation
                        if item.get("status") == "failed" or item.get("error_code"):
                            chunks.append(EvidenceChunk(
                                id=str(uuid.uuid4()),
                                source_id=self.source_id,
                                connector_type="razorpay",
                                content=f"Razorpay Payment {item.get('id')} failed. Error: {item.get('error_code')} - {item.get('error_description')}",
                                metadata={
                                    "tenant_id": self.tenant_id,
                                    "provider": "razorpay",
                                    "payment_id": item.get("id"),
                                    "error_code": item.get("error_code"),
                                    "layer_level": 2
                                }
                            ))
        except Exception as e:
            pass
        return chunks

