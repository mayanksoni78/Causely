import re

with open("frontend/src/pages/ConnectSources.tsx", "r", encoding="utf-8") as f:
    code = f.read()

# Replace refreshData to return the Promise
code = re.sub(
    r'const refreshData = \(\) => {\n\s*setLoading\(true\);\n\s*setPageError\(null\);\n\s*Promise\.all\(\[getSources\(\), getReadiness\(\)\]\)',
    r'const refreshData = async () => {\n    setLoading(true);\n    setPageError(null);\n    return Promise.all([getSources(), getReadiness()])',
    code
)

with open("frontend/src/pages/ConnectSources.tsx", "w", encoding="utf-8") as f:
    f.write(code)
