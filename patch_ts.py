import re

with open("frontend/src/pages/ConnectSources.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: endpoints in SourceFormData
content = re.sub(
    r'interface SourceFormData \{',
    'interface SourceFormData {\n  endpoints?: string;\n  file?: any;\n  base_url?: string;\n  headers?: string;',
    content
)

# Fix 2: availableIntegrations type error
content = content.replace(
    '{availableIntegrations.find(i => i.type === showModal)?.name}',
    '{(availableIntegrations.find(i => i.type === showModal) as any)?.name}'
)

with open("frontend/src/pages/ConnectSources.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Patched TS issues in ConnectSources.tsx")
