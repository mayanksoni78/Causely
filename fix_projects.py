import re

with open("backend/src/api/projects.py", "r", encoding="utf-8") as f:
    content = f.read()

import_log = "import logging\nlogger = logging.getLogger(__name__)\n\nrouter = APIRouter(prefix=\"/projects\", tags=[\"projects\"])"
content = content.replace("router = APIRouter(prefix=\"/projects\", tags=[\"projects\"])", import_log)

content = content.replace('print(f"==================================================")', 'logger.info("==================================================")')
content = content.replace('print(f"DEV ONLY INVITATION EMAIL TO: {req.email}")', 'logger.info(f"DEV ONLY INVITATION EMAIL TO: {req.email}")')
content = content.replace('print(f"Role: {req.role}")', 'logger.info(f"Role: {req.role}")')
content = content.replace('print(f"Accept link: {FRONTEND_URL}/invites/{token}")', 'logger.info(f"Accept link: {FRONTEND_URL}/invites/{token}")')

with open("backend/src/api/projects.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated projects.py")
