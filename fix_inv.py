import re

with open("frontend/src/pages/InvestigationView.tsx", "r", encoding="utf-8") as f:
    content = f.read()

if "useProject" not in content:
    content = content.replace("import { useQuery } from '@tanstack/react-query';", "import { useQuery } from '@tanstack/react-query';\nimport { useProject } from '../contexts/ProjectContext';")

if "const { currentProject } = useProject();" not in content:
    content = content.replace("const InvestigationView = () => {", "const InvestigationView = () => {\n  const { currentProject } = useProject();")

content = re.sub(
    r"enabled: !!id,",
    r"enabled: !!id && !!currentProject?.id,",
    content
)

with open("frontend/src/pages/InvestigationView.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated InvestigationView.tsx")
