import re

with open("backend/src/connectors/github.py", "r", encoding="utf-8") as f:
    code = f.read()

new_method = """    def get_commits_in_window(self, since, until) -> list[EvidenceChunk]:
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
                
                content = f"GITHUB COMMIT: {commit.sha}\\nTime: {commit.commit.author.date}\\nMessage: {msg}\\nDiff:\\n{diff[:3000]}"
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

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:"""

code = code.replace("    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:", new_method)

with open("backend/src/connectors/github.py", "w", encoding="utf-8") as f:
    f.write(code)
