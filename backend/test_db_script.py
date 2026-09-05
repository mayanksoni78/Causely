import sys
import uuid
import logging
from sqlalchemy import text
sys.path.append('.')

from src.core.database import SessionLocal
from src.models.user import Tenant

def test_db():
    print("--- Starting DB Test ---")
    db = SessionLocal()
    try:
        # 1. Test SELECT 1
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            print("SELECT 1: PASS")
        else:
            print("SELECT 1: FAIL (Unexpected result)")
            
        # 2. Test Persistence (Insert, Query, Clean)
        temp_id = uuid.uuid4()
        temp_tenant = Tenant(id=temp_id, name="Test Temporary Tenant")
        db.add(temp_tenant)
        db.commit()
        
        fetched = db.query(Tenant).filter(Tenant.id == temp_id).first()
        if fetched and fetched.name == "Test Temporary Tenant":
            print("PERSISTENCE: PASS")
        else:
            print("PERSISTENCE: FAIL (Could not fetch inserted record)")
            
        # Cleanup
        db.delete(fetched)
        db.commit()
        print("CLEANUP: PASS")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_db()
