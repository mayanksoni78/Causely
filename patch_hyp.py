prompt = """You are an AI Incident Investigator generating root-cause hypotheses based on evidence.

INCIDENT DESCRIPTION:
{incident_description}

ENTITIES:
{entities}

EVIDENCE CHUNKS (Logs, Stack Traces, and GitHub Commit Diffs):
{evidence_chunks}

TIMELINE:
{timeline}

TASK:
Generate a list of exactly 1 to 3 distinct hypotheses for the root cause of the incident based ONLY on the evidence provided above.

CRITICAL CAUSALITY RULES:
1. When evaluating a GITHUB COMMIT / CODE CHANGE, you MUST technically evaluate if the diff explains the runtime log.
2. Example 1: Changing a frontend CORS port (e.g. 5173 to 5174) DOES NOT technically cause a MongoDB "bad auth" error on the backend. If you see this, DO NOT claim the port change caused the DB failure. State it is temporally correlated but unrelated.
3. Example 2: Changing DATABASE_URL or DB credentials directly explains a MongoDB "bad auth" error. If you see this, identify it as the high-confidence root cause.
4. Do not invent commits, timestamps, or mechanisms. Only use exact evidence.
5. Every hypothesis must have a direct causal mechanism.

FORMAT:
Return ONLY a valid JSON array of objects. Do not use markdown blocks. Each object must have:
- "id": A unique string ID (e.g. "hyp_1")
- "claim": A 1-sentence statement of the root cause.
- "reasoning": A detailed explanation of WHY this caused the incident and HOW the code change mechanically led to the failure.
- "evidence_ids": An array of exact chunk IDs that support this hypothesis (must be strings, exactly as provided).
- "contradiction_ids": An array of exact chunk IDs that contradict this hypothesis.
"""
with open("backend/src/llm/prompts/hypothesis_generation.txt", "w", encoding="utf-8") as f:
    f.write(prompt)
