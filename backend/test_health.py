from src.core.database import SessionLocal
from sqlalchemy import text
try:
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    db.close()
    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
