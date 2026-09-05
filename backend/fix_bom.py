with open("src/api/incidents.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("\ufeff", "")

with open("src/api/incidents.py", "w", encoding="utf-8") as f:
    f.write(content)
