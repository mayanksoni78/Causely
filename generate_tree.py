import os

def generate_tree(dir_path, prefix=""):
    ignore = {'.git', 'node_modules', '.venv', '__pycache__', 'dist', 'build', '.DS_Store'}
    try:
        entries = sorted(os.listdir(dir_path))
    except PermissionError:
        return ""
    
    entries = [e for e in entries if e not in ignore]
    
    tree_str = ""
    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        tree_str += f"{prefix}{connector}{entry}\n"
        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            tree_str += generate_tree(path, prefix=prefix+extension)
    return tree_str

with open("project_tree.txt", "w", encoding="utf-8") as f:
    f.write("ai-incident-investigator-v2/\n")
    f.write(generate_tree("."))
    
print("Tree generated successfully!")
