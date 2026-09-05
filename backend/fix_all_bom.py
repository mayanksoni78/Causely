import os
import glob

files = glob.glob("src/**/*.py", recursive=True) + ["src/main.py"]

for file_path in files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "\ufeff" in content:
            print(f"Fixing BOM in {file_path}")
            content = content.replace("\ufeff", "")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
print("BOM sweep complete.")
