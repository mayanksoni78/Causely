import re

with open("backend/src/api/sources.py", "r", encoding="utf-8") as f:
    content = f.read()

old_github = """@router.post("/github")
async def register_github(
    payload: GithubRegister,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    connector = GitHubConnector(payload.repo_url, payload.token)
    perms = connector.check_permissions()"""

new_github = """@router.post("/github")
async def register_github(
    payload: GithubRegister,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    try:
        connector = GitHubConnector(payload.repo_url, payload.token)
        perms = connector.check_permissions()
    except Exception as e:
        logger.exception("Failed to connect to GitHub repository")
        raise HTTPException(status_code=400, detail=f"Repository not found or private. Ensure URL is correct and provide a Personal Access Token if it is private. Error: {str(e)}")"""

content = content.replace(old_github, new_github)

with open("backend/src/api/sources.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated sources.py")
