import httpx
from src.connectors.base import SourceConnector, PermissionReport, ConnectorStatus, EvidenceQuery, EvidenceChunk

class LokiConnector(SourceConnector):
    def __init__(self, loki_url: str):
        self.loki_url = loki_url.rstrip("/")
        
    def check_permissions(self) -> PermissionReport:
        return PermissionReport("loki", True, ["read_logs"], [])

    def list_capabilities(self) -> list[str]:
        return ["log_search"]

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:
        # Minimal mock for loki fetch
        chunks = []
        if query.query_text:
            chunks.append(EvidenceChunk(
                id=f"loki_mock_{hash(query.query_text)}",
                source_id="loki",
                connector_type="loki",
                content=f"[Loki Log] Found match for {query.query_text}",
                metadata={"timestamp": "recent", "labels": "{}"},
                relevance_score=0.9
            ))
        return chunks

    def health_check(self) -> ConnectorStatus:
        try:
            # We don't await because health_check is sync in the protocol, but we could use httpx sync client
            with httpx.Client(timeout=3) as client:
                res = client.get(f"{self.loki_url}/ready")
                if res.status_code == 200:
                    return ConnectorStatus(True, "Connected")
        except Exception:
            pass
        return ConnectorStatus(False, "Failed to connect to Loki")
