import uuid
import requests
from src.connectors.base import SourceConnector, PermissionReport, ConnectorStatus, EvidenceQuery, EvidenceChunk

class GitHubActionsConnector(SourceConnector):
    def __init__(self, connector_id: str, tenant_id: str, config: dict):
        self.connector_id = connector_id
        self.tenant_id = tenant_id
        self.repo_url = config.get("repo_url", "")
        self.token = config.get("token", "")
        self.repo_name = self.repo_url.replace("https://github.com/", "").strip("/")
        if self.repo_name.endswith(".git"):
            self.repo_name = self.repo_name[:-4]

    def check_permissions(self) -> PermissionReport:
        return PermissionReport(self.connector_id, True, ["actions:read"], [])

    def list_capabilities(self) -> list[str]:
        return ["workflow_runs", "build_logs"]

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:
        chunks = []
        try:
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            resp = requests.get(f"https://api.github.com/repos/{self.repo_name}/actions/runs?per_page=5", headers=headers, timeout=5)
            if resp.status_code == 200:
                runs = resp.json().get("workflow_runs", [])
                for run in runs:
                    chunks.append(EvidenceChunk(
                        id=str(uuid.uuid4()),
                        source_id=self.connector_id,
                        connector_type="github_actions",
                        content=f"Workflow Run: {run.get('name')} - Status: {run.get('status')} - Conclusion: {run.get('conclusion')}",
                        metadata={"run_id": run.get("id"), "layer_level": 1}
                    ))
        except Exception as e:
            print(f"GitHub Actions fetch error: {e}")
        return chunks

    def health_check(self) -> ConnectorStatus:
        try:
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            resp = requests.get(f"https://api.github.com/repos/{self.repo_name}/actions/runs?per_page=1", headers=headers, timeout=5)
            if resp.status_code == 200:
                return ConnectorStatus(True, f"Connected to {self.repo_name} Actions")
            return ConnectorStatus(False, f"Failed to access repo actions: {resp.status_code}")
        except Exception as e:
            return ConnectorStatus(False, str(e))
