import re

with open("backend/src/retrieval/indexer.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("def retrieve(self, db: Session, tenant_id: str, project_id: str, query: str, source_ids: list[str] | None = None, top_k: int = 5)", "def retrieve(self, db: Session, tenant_id: str, project_id: str, query: str, source_ids: list[str] | None = None, top_k: int = 20)")

with open("backend/src/retrieval/indexer.py", "w", encoding="utf-8") as f:
    f.write(code)
