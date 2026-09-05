import re

with open("frontend/src/pages/NewIncident.tsx", "r", encoding="utf-8") as f:
    content = f.read()

if "useProject" not in content:
    content = content.replace("import { useQuery } from '@tanstack/react-query';", "import { useQuery } from '@tanstack/react-query';\nimport { useProject } from '../contexts/ProjectContext';")

if "const { currentProject } = useProject();" not in content:
    content = content.replace("const NewIncident = () => {", "const NewIncident = () => {\n  const { currentProject } = useProject();")

content = re.sub(
    r"queryKey: \['readiness'\],",
    r"queryKey: ['readiness', currentProject?.id],\n    enabled: !!currentProject?.id,",
    content
)

with open("frontend/src/pages/NewIncident.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated NewIncident.tsx")
