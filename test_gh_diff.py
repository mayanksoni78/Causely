import requests
import os
from github import Github

token = os.getenv("GITHUB_TOKEN", "") # If we have one, otherwise unauth
g = Github()
repo = g.get_repo("mayanksoni78/Car_Rental")
commits = repo.get_commits()
commit = commits[0]
print("SHA:", commit.sha)

headers = {"Accept": "application/vnd.github.v3.diff"}
if token: headers["Authorization"] = f"token {token}"
resp = requests.get(commit.url, headers=headers)
print("Status:", resp.status_code)
print("Diff preview:")
print(resp.text[:500])
