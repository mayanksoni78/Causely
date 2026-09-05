import sys
import json
import asyncio
import os
sys.path.append('.')

from src.llm.client import client

async def run_test():
    print("\n==================================================")
    print("1. LOADING PROMPT TEMPLATE")
    print("==================================================")
    prompt_path = os.path.join("src", "llm", "prompts", "hypothesis_generation.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()
    print("Prompt loaded successfully.")

    print("\n==================================================")
    print("2. REALISTIC CONTEXT / EVIDENCE GROUNDING TEST (Strong Evidence)")
    print("==================================================")
    incident_a = "Payment requests are failing with HTTP 500."
    chunks_a = json.dumps([
        {"id": "log_payment_db", "source": "loki", "content": "ERROR 2023-10-27 10:45:01 PaymentService: Database connection timeout after 5 seconds."},
        {"id": "code_payment_db", "source": "github", "content": "def connect_db():\n    db.connect(timeout=5) # Reduced timeout for performance"}
    ], indent=2)
    
    prompt_a = prompt_template.replace("{incident_description}", incident_a)\
                              .replace("{entities}", "{}")\
                              .replace("{timeline}", "[]")\
                              .replace("{evidence_chunks}", chunks_a)
                              
    try:
        res_a = await client.complete_json(prompt_a, tenant_id="00000000-0000-0000-0000-000000000000")
        print(f"Parsed JSON Type: {type(res_a)}")
        print(f"Result:\n{json.dumps(res_a, indent=2)}")
        
        # Check structure
        is_structured = isinstance(res_a, list) and all("claim" in h and "evidence_ids" in h for h in res_a)
        print(f"Structured output check: {'PASS' if is_structured else 'FAIL'}")
        
        # Check grounding
        grounded = any("log_payment_db" in h.get("evidence_ids", []) or "code_payment_db" in h.get("evidence_ids", []) for h in res_a)
        print(f"Evidence grounding check: {'PASS' if grounded else 'FAIL'}")
        
    except Exception as e:
        print(f"Test A Failed: {e}")


    print("\n==================================================")
    print("3. INSUFFICIENT EVIDENCE TEST")
    print("==================================================")
    incident_b = "Something is broken."
    chunks_b = json.dumps([
        {"id": "sys_1", "source": "system", "content": "No relevant logs or code evidence available."}
    ], indent=2)
    prompt_b = prompt_template.replace("{incident_description}", incident_b)\
                              .replace("{entities}", "{}")\
                              .replace("{timeline}", "[]")\
                              .replace("{evidence_chunks}", chunks_b)
    try:
        res_b = await client.complete_json(prompt_b, tenant_id="00000000-0000-0000-0000-000000000000")
        print(f"Result:\n{json.dumps(res_b, indent=2)}")
    except Exception as e:
        print(f"Test B Failed: {e}")


    print("\n==================================================")
    print("4. UNRELATED EVIDENCE TEST")
    print("==================================================")
    incident_c = "Payment API is failing."
    chunks_c = json.dumps([
        {"id": "css_1", "source": "github", "content": "button { color: red; } /* Updated frontend CSS */"}
    ], indent=2)
    prompt_c = prompt_template.replace("{incident_description}", incident_c)\
                              .replace("{entities}", "{}")\
                              .replace("{timeline}", "[]")\
                              .replace("{evidence_chunks}", chunks_c)
    try:
        res_c = await client.complete_json(prompt_c, tenant_id="00000000-0000-0000-0000-000000000000")
        print(f"Result:\n{json.dumps(res_c, indent=2)}")
    except Exception as e:
        print(f"Test C Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
