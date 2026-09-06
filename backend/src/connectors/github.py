import logging
logger = logging.getLogger(__name__)
import requests
import uuid
import base64
from datetime import datetime
from github import Github
from github.GithubException import GithubException
from src.connectors.base import SourceConnector, PermissionReport, ConnectorStatus, EvidenceQuery, EvidenceChunk, RateLimiter

class GitHubConnector(SourceConnector):
    def __init__(self, repo_url: str, token: str):
        self.repo_url = repo_url
        self.token = token
        self.gh = Github(token)
        repo_name = repo_url.replace("https://github.com/", "").strip("/")
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        self.repo = self.gh.get_repo(repo_name)
        self.repo_name = repo_name
        self.rate_limiter = RateLimiter(calls_per_minute=30)
        self.connector_id = f"github_{repo_name.replace('/', '_')}"

    def check_permissions(self) -> PermissionReport:
        try:
            user = self.gh.get_user()
            user.login
            return PermissionReport(
                connector_id=self.connector_id,
                is_read_only=True,
                granted_scopes=["repo:read"],
                warnings=[]
            )
        except Exception as e:
            return PermissionReport(
                connector_id=self.connector_id,
                is_read_only=True,
                granted_scopes=[],
                warnings=[f"Failed to check permissions: {str(e)}"]
            )

    def list_capabilities(self) -> list[str]:
        return ["commit_history", "pull_requests", "issues", "file_contents", "stack_detection", "workflow_runs", "build_logs"]

    def _detect_stack(self) -> list[EvidenceChunk]:
        chunks = []
        stack_info = []
        try:
            contents = self.repo.get_contents("")
            files = [c.name for c in contents]
            if "package.json" in files:
                stack_info.append("Node.js/NPM (package.json found)")
            if "requirements.txt" in files or "pyproject.toml" in files:
                stack_info.append("Python (requirements.txt or pyproject.toml found)")
            if "pom.xml" in files or "build.gradle" in files:
                stack_info.append("Java/JVM (pom.xml or build.gradle found)")
            if "go.mod" in files:
                stack_info.append("Go (go.mod found)")
                
            if stack_info:
                chunks.append(EvidenceChunk(
                    id=str(uuid.uuid4()),
                    source_id=self.connector_id,
                    connector_type="github",
                    content=f"Detected Technology Stack for repository:\n" + "\n".join(stack_info),
                    metadata={"layer_level": 2, "type": "stack_detection"}
                ))
        except GithubException as e:
            logger.exception(f"Failed to detect stack: ")
        return chunks

    def get_commits_in_window(self, since, until) -> list[EvidenceChunk]:
        chunks = []
        try:
            commits = self.repo.get_commits(since=since, until=until)
            count = 0
            for commit in commits:
                if count >= 5: break  # limit to 5 commits to avoid bloating context
                msg = commit.commit.message
                headers = {
                    "Accept": "application/vnd.github.v3.diff"
                }
                if hasattr(self, "token") and self.token:
                    headers["Authorization"] = f"token {self.token}"
                
                resp = requests.get(commit.url, headers=headers, timeout=5)
                diff = resp.text if resp.status_code == 200 else "Diff unavailable"
                
                content = f"GITHUB COMMIT: {commit.sha}\nTime: {commit.commit.author.date}\nMessage: {msg}\nDiff:\n{diff[:3000]}"
                chunks.append(EvidenceChunk(
                    id=str(uuid.uuid4()),
                    source_id=self.connector_id,
                    connector_type="github",
                    content=content,
                    metadata={"commit_sha": commit.sha, "type": "commit_diff", "layer_level": 1}
                ))
                count += 1
        except Exception as e:
            logger.exception("Failed to get commits in window")
        return chunks

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:
        chunks = []
        try:
            # Stack Detection
            chunks.extend(self._detect_stack())

            # GitHub Actions Workflow Runs
            try:
                headers = {
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                resp = requests.get(f"https://api.github.com/repos/{self.repo_name}/actions/runs?per_page=10", headers=headers, timeout=5)
                if resp.status_code == 200:
                    runs = resp.json().get("workflow_runs", [])
                    count = 0
                    for run in runs:
                        if count >= query.max_results: break
                        workflow_name = run.get('name', 'Unknown Workflow')
                        status = run.get('status', 'unknown')
                        conclusion = run.get('conclusion', 'unknown')
                        content = f"Workflow Run: {workflow_name} - Status: {status} - Conclusion: {conclusion}"
                        if query.query_text.lower() in content.lower() or query.query_text.lower() in workflow_name.lower() or status == 'completed':
                             chunks.append(EvidenceChunk(
                                 id=str(uuid.uuid4()),
                                 source_id=self.connector_id,
                                 connector_type="github",
                                 content=content,
                                 metadata={"run_id": run.get("id"), "workflow_name": workflow_name, "workflow_status": status, "layer_level": 1}
                             ))
                             count += 1
            except Exception as e:
                logger.exception(f"Error fetching workflow runs: ")

            # Search commits
            try:
                commits = self.repo.get_commits()
                count = 0
                for commit in commits:
                    if count >= query.max_results: break
                    msg = commit.commit.message
                    if query.query_text.lower() in msg.lower():
                        chunks.append(EvidenceChunk(
                            id=str(uuid.uuid4()),
                            source_id=self.connector_id,
                            connector_type="github",
                            content=msg,
                            metadata={"commit_sha": commit.sha, "layer_level": 1}
                        ))
                        count += 1
            except GithubException as e:
                logger.exception(f"Error fetching commits: ")

            # Search issues and PRs (GitHub treats PRs as issues in this API)
            try:
                issues = self.repo.get_issues(state='all')
                count = 0
                for issue in issues:
                    if count >= query.max_results: break
                    title_body = f"{issue.title}\n{issue.body or ''}"
                    if query.query_text.lower() in title_body.lower():
                        md = {"issue_number": issue.number, "layer_level": 1}
                        if issue.pull_request:
                            md["pr_number"] = issue.number
                        chunks.append(EvidenceChunk(
                            id=str(uuid.uuid4()),
                            source_id=self.connector_id,
                            connector_type="github",
                            content=title_body,
                            metadata=md
                        ))
                        count += 1
            except GithubException as e:
                logger.exception(f"Error fetching issues/PRs: ")
                
            # Search file contents (basic keyword search in repo if supported, or via GitHub Search API)
            try:
                # We use the GitHub Search API for code search
                query_str = f"{query.query_text} repo:{self.repo.full_name}"
                code_results = self.gh.search_code(query=query_str)
                count = 0
                for file in code_results:
                    if count >= query.max_results // 2: break
                    try:
                        content_b64 = self.repo.get_contents(file.path).content
                        if content_b64:
                            decoded = base64.b64decode(content_b64).decode('utf-8', errors='ignore')
                            chunks.append(EvidenceChunk(
                                id=str(uuid.uuid4()),
                                source_id=self.connector_id,
                                connector_type="github",
                                content=f"File: {file.path}\n\n{decoded[:1000]}...", # Truncate for now
                                metadata={"file_path": file.path, "layer_level": 3}
                            ))
                            count += 1
                    except Exception as inner_e:
                        logger.exception(f"Failed to decode file {file.path}")
            except GithubException as e:
                logger.exception("Error searching code")

        except Exception as e:
            logger.exception(f"General failure in GitHubConnector fetch: ")
            
        return chunks

    def health_check(self) -> ConnectorStatus:
        try:
            name = self.repo.name
            return ConnectorStatus(healthy=True, message=f"Connected to {name}")
        except Exception as e:
            return ConnectorStatus(healthy=False, message=str(e))
