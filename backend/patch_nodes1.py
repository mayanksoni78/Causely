import re

with open("backend/src/pipeline/nodes.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace hypothesis generation error handling
old_hyp = """    try:
        hypotheses = await llm.complete_json(prompt, tenant_id=state["tenant_id"])
        if not isinstance(hypotheses, list):
            hypotheses = [hypotheses]
    except Exception:
        hypotheses = []"""

new_hyp = """    try:
        hypotheses = await llm.complete_json(prompt, tenant_id=state["tenant_id"])
        if not isinstance(hypotheses, list):
            hypotheses = [hypotheses]
    except Exception as e:
        logger.exception("Hypothesis generation failed")
        state["hypothesis_error"] = str(e)
        hypotheses = []"""

code = code.replace(old_hyp, new_hyp)

# Replace timeline generation error handling
old_timeline = """    try:
        timeline = await llm.complete_json(prompt, tenant_id=state["tenant_id"])
        if not isinstance(timeline, list):
            timeline = [timeline]
    except Exception:
        timeline = []"""

new_timeline = """    try:
        timeline = await llm.complete_json(prompt, tenant_id=state["tenant_id"])
        if not isinstance(timeline, list):
            timeline = [timeline]
    except Exception as e:
        logger.exception("Timeline generation failed")
        state["timeline_error"] = str(e)
        timeline = []"""

code = code.replace(old_timeline, new_timeline)

with open("backend/src/pipeline/nodes.py", "w", encoding="utf-8") as f:
    f.write(code)
