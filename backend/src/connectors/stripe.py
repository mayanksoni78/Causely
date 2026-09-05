import logging
logger = logging.getLogger(__name__)
import uuid
import requests
from src.connectors.base import SourceConnector, PermissionReport, ConnectorStatus, EvidenceQuery, EvidenceChunk

class StripeConnector(SourceConnector):
    def __init__(self, connector_id: str, tenant_id: str, config: dict):
        self.connector_id = connector_id
        self.tenant_id = tenant_id
        self.api_key = config.get("api_key", "")

    def check_permissions(self) -> PermissionReport:
        return PermissionReport(self.connector_id, True, ["read_events", "read_charges"], [])

    def list_capabilities(self) -> list[str]:
        return ["payment_events", "customer_data"]

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:
        # Prototype: using requests to call Stripe API
        chunks = []
        try:
            # We would typically use the stripe python SDK or direct HTTP API
            # For this prototype, we'll hit the /v1/events endpoint directly if query mentions it
            if "stripe" in query.query_text.lower() or "payment" in query.query_text.lower():
                headers = {"Authorization": f"Bearer {self.api_key}"}
                resp = requests.get("https://api.stripe.com/v1/events?limit=10", headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    for evt in data:
                        chunks.append(EvidenceChunk(
                            id=str(uuid.uuid4()),
                            source_id=self.connector_id,
                            connector_type="stripe",
                            content=f"Stripe Event: {evt.get('type')} - {evt.get('id')}\nData: {str(evt.get('data', {}))}",
                            metadata={"event_id": evt.get('id'), "layer_level": 2}
                        ))
        except Exception as e:
            logger.exception(f"Stripe fetch error: ")
        return chunks

    def health_check(self) -> ConnectorStatus:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            resp = requests.get("https://api.stripe.com/v1/balance", headers=headers, timeout=5)
            if resp.status_code == 200:
                return ConnectorStatus(True, "Connected to Stripe")
            return ConnectorStatus(False, f"Stripe returned {resp.status_code}")
        except Exception as e:
            return ConnectorStatus(False, str(e))
