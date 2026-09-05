import re

with open("frontend/src/pages/ConnectSources.tsx", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("let payload = { ...formData };", "let payload: any = { ...formData };")

with open("frontend/src/pages/ConnectSources.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Patched payload any")
