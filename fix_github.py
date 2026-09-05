with open("backend/src/connectors/github.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('print(f"Failed to decode file {file.path}: {inner_e}")', 'logger.exception(f"Failed to decode file {file.path}")')
content = content.replace('logger.exception(f"Error searching code: ")', 'logger.exception("Error searching code")')

with open("backend/src/connectors/github.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated github.py")
