import re

with open("backend/src/api/incidents.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('logger.exception(f"Server-side investigation error: ");', 'logger.exception("Server-side investigation error");')
content = content.replace('logger.exception(f"Background task error: ")', 'logger.exception("Background task error")')
content = content.replace('Incident.status.in_(["created", "investigating"])', 'Incident.status.in_(["queued", "investigating"])')

# Also fix the `datetime.utcnow()`
old_usage = """    today = datetime.utcnow().date()
    start_of_day = datetime(today.year, today.month, today.day)"""
new_usage = """    from datetime import timezone
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)"""
content = content.replace(old_usage, new_usage)

with open("backend/src/api/incidents.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated incidents.py")
