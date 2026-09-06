import re
import datetime

# Test string
logs = [
    "2026-09-05T17:46:40.268Z database.connected",
    "2026-09-05T17:57:59.293Z server.started",
    "2026-09-05T17:58:00.815Z database.connection_failed"
]

pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?'
timestamps = []
for log in logs:
    matches = re.findall(pattern, log)
    for m in matches:
        try:
            # strip Z and parse
            clean = m.replace('Z', '+00:00')
            if clean.endswith('Z'): clean = clean[:-1] + '+00:00'
            dt = datetime.datetime.fromisoformat(clean)
            timestamps.append(dt)
        except Exception:
            pass

print(timestamps)
if timestamps:
    t_min = min(timestamps)
    t_max = max(timestamps)
    print(t_min, t_max)
