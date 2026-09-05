import re

with open("backend/src/main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add logging
if "import logging" not in content:
    content = content.replace("import os", "import os\nimport logging\nlogger = logging.getLogger(__name__)")

# Fix print statements in lifespan
content = content.replace('print("Initializing backend...")', 'logger.info("Initializing backend...")')
content = content.replace('print("Database ready.")', 'logger.info("Database ready.")')
content = content.replace('print("Shutting down...")', 'logger.info("Shutting down...")')

# Fix traceback.print_exc in /health
old_health = """@app.get("/health")
def health_check():
    from src.core.database import SessionLocal
    from sqlalchemy import text
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "degraded", "database": "unavailable"}"""

new_health = """@app.get("/health")
def health_check():
    from src.core.database import SessionLocal
    from sqlalchemy import text
    from fastapi import Response
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "database": "connected"}
    except Exception:
        logger.exception("Database connection failed during health check")
        return JSONResponse(status_code=503, content={"status": "degraded", "database": "unavailable"})"""

content = content.replace(old_health, new_health)

with open("backend/src/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py")
