import re

with open("backend/src/pipeline/nodes.py", "r", encoding="utf-8") as f:
    code = f.read()

old_synth_err = """    try:
        report = await llm.complete(prompt, tenant_id=state["tenant_id"])
    except Exception as e:
        report = f"Failed to synthesize report: {e}"
        
    state["final_report"] = {"report": report}"""

new_synth_err = """    try:
        report = await llm.complete(prompt, tenant_id=state["tenant_id"])
    except Exception as e:
        logger.exception("Synthesis failed due to LLM error")
        err_str = str(e).lower()
        if any(x in err_str for x in ["503", "504", "unavailable", "timeout", "too many requests", "429", "overloaded"]):
            report = "Temporarily unavailable — Gemini service is currently unavailable.\\n\\nThe investigation evidence and findings are still available."
        elif any(x in err_str for x in ["401", "403", "api_key", "unauthorized", "forbidden"]):
            report = "AI report unavailable: Invalid LLM configuration or Authentication Failed."
        elif "400" in err_str:
            report = "AI report unavailable: Invalid request format."
        else:
            report = "AI report temporarily unavailable due to a service error.\\n\\nThe investigation evidence and findings are still available."
            
    state["final_report"] = {"report": report}"""

code = code.replace(old_synth_err, new_synth_err)

with open("backend/src/pipeline/nodes.py", "w", encoding="utf-8") as f:
    f.write(code)
