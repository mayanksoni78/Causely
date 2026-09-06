import re

with open("backend/src/pipeline/nodes.py", "r", encoding="utf-8") as f:
    code = f.read()

# Force a 503 error in synthesis_node for testing
code = code.replace("report = await llm.complete(prompt, tenant_id=state[\"tenant_id\"])", "raise Exception('503 UNAVAILABLE: This model is currently experiencing high demand. Spikes in demand are usually temporary.')")

with open("backend/src/pipeline/nodes.py", "w", encoding="utf-8") as f:
    f.write(code)
