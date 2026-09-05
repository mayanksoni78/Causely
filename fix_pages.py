import re
import os

def fix_page(filename):
    if not os.path.exists(filename):
        return
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    if "useQuery" not in content:
        return
        
    if "useProject" not in content:
        content = content.replace("import { useQuery } from '@tanstack/react-query';", "import { useQuery } from '@tanstack/react-query';\nimport { useProject } from '../contexts/ProjectContext';")

    # This is a bit brittle, but handles basic function component declarations
    if "const { currentProject } = useProject();" not in content:
        content = re.sub(r"const (\w+) = \(\) => {", r"const \1 = () => {\n  const { currentProject } = useProject();", content)

    # Add enabled flag for all useQuery calls that don't have it
    content = re.sub(
        r"queryKey: \['(.*?)'\],",
        r"queryKey: ['\1', currentProject?.id],\n      enabled: !!currentProject?.id,",
        content
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {filename}")

fix_page("frontend/src/pages/History.tsx")
fix_page("frontend/src/pages/ConnectSources.tsx")
