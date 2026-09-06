import re

with open("backend/src/pipeline/nodes.py", "r", encoding="utf-8") as f:
    code = f.read()

# Add a simple timing logger
timing_helper = """
import time
def log_timing(step, start_time):
    dur = time.time() - start_time
    print(f"[INVESTIGATION] {step}: {dur:.2f}s", flush=True)

"""

if "def log_timing(" not in code:
    code = code.replace("import logging", "import logging\n" + timing_helper)

code = re.sub(
    r'(state\["trace"\].append\(StepTrace\("([^"]+)", [^\)]+\)\.to_dict\(\)\[0\]\))',
    r'\1\n    log_timing("\2", start.timestamp())',
    code
)

with open("backend/src/pipeline/nodes.py", "w", encoding="utf-8") as f:
    f.write(code)
