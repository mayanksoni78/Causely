import re

with open("frontend/src/pages/ConnectSources.tsx", "r", encoding="utf-8") as f:
    content = f.read()

if "useProject" not in content:
    content = content.replace("import React, { useState, useEffect, useRef } from 'react';", "import React, { useState, useEffect, useRef } from 'react';\nimport { useProject } from '../contexts/ProjectContext';")

if "const { currentProject } = useProject();" not in content:
    content = content.replace("const ConnectSources = () => {", "const ConnectSources = () => {\n  const { currentProject } = useProject();")

content = content.replace("useEffect(() => {\n    refreshData();\n  }, []);", "useEffect(() => {\n    if (currentProject?.id) refreshData();\n  }, [currentProject?.id]);")

with open("frontend/src/pages/ConnectSources.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated ConnectSources.tsx")
