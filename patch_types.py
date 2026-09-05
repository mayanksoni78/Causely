import re

with open("frontend/src/lib/types.ts", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("metadata: Record<string, any>;", "metadata: Record<string, unknown>;")
content = content.replace("final_report?: any;", "final_report?: Record<string, unknown>;")
content = content.replace("confidence?: any;", "confidence?: ConfidenceScore;")
content = content.replace("config?: Record<string, any>;", "config?: Record<string, unknown>;")

with open("frontend/src/lib/types.ts", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated frontend types.ts")
