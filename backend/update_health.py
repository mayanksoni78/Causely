import re
with open("src/main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("except Exception:", "except Exception as e:\n        import traceback\n        traceback.print_exc()")
with open("src/main.py", "w", encoding="utf-8") as f:
    f.write(content)
