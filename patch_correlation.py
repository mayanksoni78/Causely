import re

with open("backend/src/pipeline/nodes.py", "r", encoding="utf-8") as f:
    code = f.read()

correlation_node = """
async def temporal_correlation_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    import re
    import datetime
    
    # Extract timestamps from retrieved chunks
    pattern = r'\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?Z?'
    timestamps = []
    
    for chunk in state.get("retrieved_chunks", []):
        matches = re.findall(pattern, chunk.content)
        for m in matches:
            try:
                clean = m.replace('Z', '+00:00')
                if clean.endswith('Z'): clean = clean[:-1] + '+00:00'
                dt = datetime.datetime.fromisoformat(clean)
                timestamps.append(dt)
            except Exception:
                pass
                
    if timestamps:
        t_min = min(timestamps)
        t_max = max(timestamps)
        
        # Extend window back by 1 hour to catch preceding commits
        window_start = t_min - datetime.timedelta(hours=1)
        window_end = t_max + datetime.timedelta(minutes=5)
        
        # Look for a Github connector in available sources
        gh_connector = None
        from src.connectors.registry import get_connector
        from src.core.database import SessionLocal
        from src.models.domain import ConnectorSource
        
        db = SessionLocal()
        try:
            for cid in state["source_plan"].get("available", []):
                source = db.query(ConnectorSource).filter(ConnectorSource.id == cid).first()
                if source and source.connector_type == "github":
                    gh_connector = get_connector(source)
                    gh_connector.connector_id = cid
                    break
        finally:
            db.close()
            
        if gh_connector and hasattr(gh_connector, "get_commits_in_window"):
            commit_chunks = gh_connector.get_commits_in_window(window_start, window_end)
            if commit_chunks:
                # Add to retrieved chunks
                state["retrieved_chunks"].extend(commit_chunks)
                state["trace"].append(StepTrace("temporal_correlation", start, get_now(), {"window": f"{window_start} to {window_end}"}, {"commits_found": len(commit_chunks)}).to_dict()[0])
                return state

    state["trace"].append(StepTrace("temporal_correlation", start, get_now(), {}, {"commits_found": 0}).to_dict()[0])
    return state

"""

if "async def temporal_correlation_node" not in code:
    code = code.replace("async def reranking_node(state: InvestigationState) -> InvestigationState:", correlation_node + "async def reranking_node(state: InvestigationState) -> InvestigationState:")
    
with open("backend/src/pipeline/nodes.py", "w", encoding="utf-8") as f:
    f.write(code)
