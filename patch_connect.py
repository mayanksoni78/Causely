import re

with open("frontend/src/pages/ConnectSources.tsx", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("file?: any;", "file?: File;")
content = content.replace("let payload: any = { ...formData };", "let payload: Record<string, unknown> = { ...formData } as Record<string, unknown>;")
content = content.replace("const e = error as any;\n        alert('o- Connection failed: ' + (e?.response?.data?.detail || e.message));", "const e = error as {response?: {data?: {detail?: string}}, message?: string};\n        setSubmitError('Connection failed: ' + (e?.response?.data?.detail || e?.message || 'Unknown error'));")
content = content.replace("as any)?.name", "as {name?: string})?.name")

with open("frontend/src/pages/ConnectSources.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated ConnectSources.tsx")
