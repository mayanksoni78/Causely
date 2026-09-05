with open("frontend/src/lib/api.ts", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("export const createSource = async (type: string, data: Record<string, unknown> | FormData | {file?: File, onUploadProgress?: (progressEvent: unknown) => void}) => {", "export const createSource = async (type: string, data: any) => {")

with open("frontend/src/lib/api.ts", "w", encoding="utf-8") as f:
    f.write(content)
print("Reverted createSource type in api.ts to any to fix TS errors with FormData vs File.")
