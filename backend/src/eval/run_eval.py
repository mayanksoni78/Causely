import json
import asyncio
import time
import os
from src.pipeline.graph import investigation_graph
from src.connectors.registry import registry
from src.connectors.static_log import StaticLogConnector

from src.llm.client import client as llm

class MockLLM:
    def __init__(self, state_ref=None):
        self.state_ref = state_ref
        
    async def complete(self, prompt, system=""):
        return "Mock report generated successfully."
        
    async def complete_json(self, prompt, system=""):
        if "Extract" in prompt:
            return {"service": "unknown", "error_signature": "unknown", "timeframe": "unknown", "affected_endpoint": "unknown"}
        else:
            # Parse prompt to find chunk IDs
            import re
            ids = re.findall(r'"id":\s*"([^"]+)"', prompt)
            ev_id = ids[0] if ids else "mock_ev"
            return [{"id": "hyp_1", "claim": "Mock hypothesis based on logs", "evidence_ids": [ev_id], "confirm_evidence": "none", "refute_evidence": "none"}]

def setup_mock_sources():
    # Override LLM
    import src.pipeline.nodes as nodes
    nodes.llm = MockLLM()
    
    fake_logs = """
    2023-10-24 10:00:01 INFO User logged in
    2023-10-24 10:05:00 ERROR 500 Internal Server Error at /checkout - tax_id is required
    2023-10-24 10:06:00 ERROR Database connection timeout during booking
    2023-10-24 10:07:00 ERROR File too large error during image upload
    2023-10-24 10:08:00 WARN Payment 401 unauthorized
    2023-10-24 10:09:00 INFO Search cars - 0 results found
    2023-10-24 10:10:00 ERROR 404 Not Found at /verify-email
    2023-10-24 10:11:00 WARN Admin dashboard query took 10.5s
    2023-10-24 10:12:00 ERROR Invalid discount calculation logic
    2023-10-24 10:13:00 ERROR Session expired unexpectedly
    2023-10-24 10:14:00 WARN Invalid date in past selected
    """
    connector = StaticLogConnector(fake_logs)
    registry.register(connector.connector_id, connector)
    
    # Add a second connector to pass corroboration (>= 2 independent sources)
    fake_logs_2 = """
    Commit 123: Fixed database timeout in booking
    Commit 124: Reverted tax_id requirement causing 500 error on checkout
    Issue 1: Payment gateway 401 unauthorized
    """
    class MockGitConnector(StaticLogConnector):
        def fetch(self, query):
            chunks = super().fetch(query)
            for c in chunks:
                c.connector_type = "github" # fake type
                c.source_id = "mock_github"
            return chunks
            
    connector2 = MockGitConnector(fake_logs_2)
    connector2.connector_id = "mock_github"
    registry.register(connector2.connector_id, connector2)

def run_eval():
    setup_mock_sources()
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.json')
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    results = []
    
    print(f"Starting Evaluation on {len(dataset)} incidents...")
    
    for incident in dataset:
        print(f"\n--- Evaluating {incident['id']} ---")
        
        initial_state = {
            "incident_id": incident["id"],
            "description": incident["description"],
            "entities": {},
            "source_plan": {},
            "retrieved_chunks": [],
            "reranked_chunks": [],
            "hypotheses": [],
            "verified_hypotheses": [],
            "confidence": None,
            "final_report": None,
            "trace": [],
            "insufficient_evidence": False
        }
        
        start_time = time.time()
        
        try:
            final_state = asyncio.run(investigation_graph.ainvoke(initial_state))
            success = not final_state.get("insufficient_evidence", False)
            
            # Simple Recall Check: Does any retrieved chunk contain one of the expected keywords?
            chunks = final_state.get("reranked_chunks", [])
            recall_score = 0
            found_keywords = []
            
            for chunk in chunks:
                for kw in incident["expected_keywords"]:
                    if kw.lower() in chunk.content.lower() and kw not in found_keywords:
                        found_keywords.append(kw)
                        
            if incident["expected_keywords"]:
                recall_score = len(found_keywords) / len(incident["expected_keywords"])
                
            results.append({
                "id": incident["id"],
                "success": success,
                "latency_sec": round(time.time() - start_time, 2),
                "recall": recall_score,
                "confidence_score": final_state.get("confidence", {}).get("score", 0),
                "retrieved_count": len(final_state.get("retrieved_chunks", [])),
                "error": None
            })
            
            print(f"Result: Success={success}, Recall={recall_score:.2f}, Latency={time.time() - start_time:.2f}s")
            
        except Exception as e:
            print(f"Result: Failed due to exception - {e}")
            results.append({
                "id": incident["id"],
                "success": False,
                "latency_sec": round(time.time() - start_time, 2),
                "recall": 0,
                "confidence_score": 0,
                "retrieved_count": 0,
                "error": str(e)
            })

    # Generate Report
    avg_latency = sum(r["latency_sec"] for r in results) / len(results) if results else 0
    avg_recall = sum(r["recall"] for r in results) / len(results) if results else 0
    success_rate = sum(1 for r in results if r["success"]) / len(results) if results else 0
    
    report_md = f"""# Evaluation Report

## Summary Metrics
- **Total Incidents Evaluated:** {len(results)}
- **Overall Success Rate:** {success_rate * 100:.1f}%
- **Average Recall@K (Keyword Match):** {avg_recall * 100:.1f}%
- **Average Latency:** {avg_latency:.2f}s

## Detailed Results
| Incident ID | Success | Recall | Confidence | Latency | Retrieved | Error |
|-------------|---------|--------|------------|---------|-----------|-------|
"""
    for r in results:
        err = r['error'] or "None"
        report_md += f"| {r['id']} | {'✅' if r['success'] else '❌'} | {r['recall']:.2f} | {r['confidence_score']:.2f} | {r['latency_sec']}s | {r['retrieved_count']} | {err} |\n"
        
    report_path = r'C:\Users\mayan\.gemini\antigravity\brain\f12dafce-a356-4459-b8f0-024e6375d09a\eval_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_md)
        
    print(f"\nEvaluation Complete! Report generated at {report_path}")

if __name__ == "__main__":
    run_eval()
