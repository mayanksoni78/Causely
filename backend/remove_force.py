import re

with open("backend/src/pipeline/nodes.py", "r", encoding="utf-8") as f:
    code = f.read()

# Remove the forced 503
code = code.replace("raise Exception('503 UNAVAILABLE: This model is currently experiencing high demand. Spikes in demand are usually temporary.')", "report = await llm.complete(prompt, tenant_id=state[\"tenant_id\"])")

with open("backend/src/pipeline/nodes.py", "w", encoding="utf-8") as f:
    f.write(code)
