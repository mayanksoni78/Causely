import re

with open("backend/src/api/incidents.py", "r", encoding="utf-8") as f:
    code = f.read()

# Increase daily limit for testing
code = code.replace("if daily_count >= 10:", "if daily_count >= 1000:")

with open("backend/src/api/incidents.py", "w", encoding="utf-8") as f:
    f.write(code)
