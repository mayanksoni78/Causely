import re

with open("frontend/src/pages/Dashboard.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# Add useProject import
if "useProject" not in content:
    content = content.replace("import { useQuery } from '@tanstack/react-query';", "import { useQuery } from '@tanstack/react-query';\nimport { useProject } from '../contexts/ProjectContext';")

# Add useProject hook inside Dashboard
if "const { currentProject } = useProject();" not in content:
    content = content.replace("const Dashboard = () => {", "const Dashboard = () => {\n  const { currentProject } = useProject();")

# Add enabled flag to dashboard-stats query
content = re.sub(
    r"queryKey: \['dashboard-stats'\],",
    r"queryKey: ['dashboard-stats', currentProject?.id],\n      enabled: !!currentProject?.id,",
    content
)

# Add enabled flag to incidents query
content = re.sub(
    r"queryKey: \['incidents'\],",
    r"queryKey: ['incidents', currentProject?.id],\n      enabled: !!currentProject?.id,",
    content
)

with open("frontend/src/pages/Dashboard.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Dashboard.tsx")
