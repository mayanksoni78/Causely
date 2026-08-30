import sys

with open("frontend/src/pages/Dashboard.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# Replace Causely with Dashboard
old_header = """      <header className="page-header">
        <h1 className="page-title">Causely</h1>
        <p className="page-subtitle">Evidence-driven root cause analysis — every conclusion backed by verified, cited evidence</p>
      </header>"""

# Actually, the file uses a weird character because of unicode issues:
# <p className="page-subtitle">Evidence-driven root cause analysis ?" every conclusion backed by verified, cited evidence</p>
