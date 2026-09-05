import sys
import traceback
from src.core.database import SessionLocal
from sqlalchemy import text
try:
    print("Testing DB connection...")
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    db.close()
    print("Connection OK!")
except Exception as e:
    print("Connection Failed!")
    traceback.print_exc()
