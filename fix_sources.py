import re
with open("backend/src/api/sources.py", "r", encoding="utf-8") as f:
    content = f.read()

import_log = "import logging\nlogger = logging.getLogger(__name__)\n\nrouter = APIRouter(prefix=\"/sources\", tags=[\"sources\"])"
content = content.replace("router = APIRouter(prefix=\"/sources\", tags=[\"sources\"])", import_log)

old_except = """    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")"""
new_except = """    except Exception:
        logger.exception("Failed to process static log file")
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to process file")"""

content = content.replace(old_except, new_except)

with open("backend/src/api/sources.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated sources.py")
