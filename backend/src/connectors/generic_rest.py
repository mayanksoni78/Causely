import httpx
import uuid
from datetime import datetime
from typing import List, Dict, Any
from src.connectors.base import SourceConnector, PermissionReport, ConnectorStatus, EvidenceQuery, EvidenceChunk

class GenericRESTConnector(SourceConnector):
    def __init__(self, source_id: str, tenant_id: str, config: Dict[str, Any]):
        self.source_id = source_id
        self.tenant_id = tenant_id
        self.base_url = config.get("base_url", "").rstrip("/")
        self.auth_type = config.get("auth_type", "none")
        self.auth_token = config.get("auth_token", "")
        self.headers = config.get("headers", {})
        
        if self.auth_type == "bearer":
            self.headers["Authorization"] = f"Bearer {self.auth_token}"
        elif self.auth_type == "api_key":
            self.headers["x-api-key"] = self.auth_token
            
        self.endpoints = config.get("endpoints", [])

    def check_permissions(self) -> PermissionReport:
        return PermissionReport(
            connector_id=self.source_id,
            is_read_only=True,
            granted_scopes=["read"],
            warnings=[]
        )

    def list_capabilities(self) -> list[str]:
        return ["rest_api", "custom_endpoints"]

    def health_check(self) -> ConnectorStatus:
        try:
            if not self.base_url:
                return ConnectorStatus(healthy=False, message="Base URL not configured")
                
            endpoint = self.endpoints[0] if self.endpoints else ""
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            with httpx.Client(timeout=5.0) as client:
                res = client.head(url, headers=self.headers)
                if res.status_code < 500:
                    return ConnectorStatus(healthy=True, message="Connected")
                return ConnectorStatus(healthy=False, message=f"HTTP {res.status_code}")
        except Exception as e:
            return ConnectorStatus(healthy=False, message=str(e))

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:
        chunks = []
        try:
            with httpx.Client(timeout=10.0) as client:
                for endpoint in self.endpoints:
                    url = f"{self.base_url}/{endpoint.lstrip('/')}"
                    res = client.get(url, headers=self.headers)
                    if res.status_code == 200:
                        content = res.text
                        chunks.append(EvidenceChunk(
                            id=str(uuid.uuid4()),
                            source_id=self.source_id,
                            connector_type="generic_rest",
                            content=content,
                            metadata={
                                "tenant_id": self.tenant_id,
                                "url": url,
                                "endpoint": endpoint,
                                "layer_level": 2
                            }
                        ))
        except Exception as e:
            pass
        return chunks
