with open("frontend/src/lib/auth.tsx", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("signup: (data: any)", "signup: (data: Record<string, unknown>)")
content = content.replace("const signup = async (data: any)", "const signup = async (data: Record<string, unknown>)")

with open("frontend/src/lib/auth.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated auth.tsx")
