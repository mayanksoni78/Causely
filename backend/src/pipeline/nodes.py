from datetime import datetime
import json
from src.pipeline.state import InvestigationState
from src.core.database import SessionLocal
from src.models.domain import Source as DBSource
from src.connectors.github import GitHubConnector
from src.connectors.static_log import StaticLogConnector
from src.connectors.postgres import PostgresConnector
from src.connectors.mongodb import MongoDBConnector
from src.connectors.loki import LokiConnector
from src.connectors.generic_rest import GenericRESTConnector
from src.connectors.external.razorpay import RazorpayConnector
from src.connectors.base import EvidenceQuery
from src.retrieval.reranker import rerank
from src.retrieval.indexer import indexer
from src.llm.client import client as llm
from src.observability.tracer import StepTrace

def get_now():
    return datetime.now()

from src.core.security import decrypt_dict

def _get_connector(source: DBSource):
    # Decrypt config if it is encrypted
    config = source.config
    if "encrypted_data" in config:
        config = decrypt_dict(config["encrypted_data"])

    if source.type == "github":
        return GitHubConnector(config.get("repo_url"), config.get("token"))
    elif source.type == "static_log":
        # We don't fetch from static_log directly anymore, it's indexed in DB
        return None
    elif source.type == "postgres":
        return PostgresConnector(config.get("connection_string"))
    elif source.type == "mongodb":
        from src.connectors.mongodb import MongoDBConnector
        return MongoDBConnector(config.get("connection_string"))
    elif source.type == "loki":
        return LokiConnector(config.get("url"))
    elif source.type == "generic_rest":
        return GenericRESTConnector(str(source.id), str(source.tenant_id), config)
    elif source.type == "razorpay":
        return RazorpayConnector(str(source.id), str(source.tenant_id), config)
    elif source.type == "stripe":
        from src.connectors.stripe import StripeConnector
        return StripeConnector(str(source.id), str(source.tenant_id), config)
    elif source.type == "auth0":
        from src.connectors.auth0 import Auth0Connector
        return Auth0Connector(str(source.id), str(source.tenant_id), config)
    elif source.type == "github_actions":
        from src.connectors.github_actions import GitHubActionsConnector
        return GitHubActionsConnector(str(source.id), str(source.tenant_id), config)
    return None

async def intake_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    prompt = f"Extract service name, error_signature, timeframe, and affected_endpoint from this incident description as JSON: {state['description']}"
    
    try:
        entities = await llm.complete_json(prompt, tenant_id=state["tenant_id"])
    except Exception:
        entities = {"service": "unknown", "error_signature": "unknown", "timeframe": "unknown", "affected_endpoint": "unknown"}
        
    state["entities"] = entities
    state["trace"].append(StepTrace("intake", start, get_now(), {"description": state["description"]}, entities).to_dict()[0])
    return state

async def source_planning_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    plan = {"available": [], "queried": [], "skipped": []}
    
    db = SessionLocal()
    try:
        sources = db.query(DBSource).filter(DBSource.tenant_id == state["tenant_id"]).all()
        for source in sources:
            cid = str(source.id)
            if source.type == "static_log":
                plan["available"].append(cid)
                continue
                
            connector = _get_connector(source)
            if not connector:
                plan["skipped"].append({"id": cid, "reason": "Unknown connector type"})
                continue
                
            status = connector.health_check()
            if status.healthy:
                plan["available"].append(cid)
            else:
                plan["skipped"].append({"id": cid, "reason": status.message})
    finally:
        db.close()
            
    state["source_plan"] = plan
    state["trace"].append(StepTrace("source_planning", start, get_now(), {}, plan).to_dict()[0])
    return state

async def retrieval_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    chunks = []
    seen = set()
    
    entities = state.get("entities", {})
    query_str = f"{entities.get('service', '')} {entities.get('error_signature', '')}".strip()
    if not query_str or query_str == "unknown unknown" or "unknown" in query_str.lower():
        # Fallback to a short keyword string if entities are poorly extracted
        words = state["description"].split()
        query_str = " ".join(words[:15]) if len(words) > 15 else state["description"]
        
    query = EvidenceQuery(query_text=query_str, entity_filters=entities)
    
    db = SessionLocal()
    try:
        sources = db.query(DBSource).filter(DBSource.tenant_id == state["tenant_id"]).all()
        source_map = {str(s.id): s for s in sources}
        
        for cid in state["source_plan"]["available"]:
            source = source_map.get(cid)
            if not source:
                continue
            connector = _get_connector(source)
            if connector is None:
                # E.g. static_log which is only available via indexer
                continue
                  
            try:
                fetched = connector.fetch(query)
                state["source_plan"]["queried"].append(cid)
                for c in fetched:
                    c.source_id = cid # Override the ID so we have the DB UUID
                    if c.id not in seen:
                        seen.add(c.id)
                        chunks.append(c)
            except Exception as e:
                print(f"Error fetching from connector {cid}: {e}")
                pass
                
        # Also query indexer (for previously ingested knowledge, e.g. static logs)
        indexed_chunks = indexer.retrieve(db, state["tenant_id"], state["project_id"], state["description"], source_ids=state["source_plan"]["available"])
        
        state["source_plan"]["queried"].append("indexer")
        
        for c in indexed_chunks:
            if c.id not in seen:
                seen.add(c.id)
                chunks.append(c)
        
        state["evidence"] = chunks
    finally:
        db.close()
            
    state["retrieved_chunks"] = chunks
    state["trace"].append(StepTrace("retrieval", start, get_now(), {"query": query.__dict__}, {"chunk_count": len(chunks)}).to_dict()[0])
    return state

async def reranking_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    reranked = rerank(state["description"], state["retrieved_chunks"])
    state["reranked_chunks"] = reranked
    state["trace"].append(StepTrace("reranking", start, get_now(), {"input_count": len(state["retrieved_chunks"])}, {"output_count": len(reranked)}).to_dict()[0])
    return state

async def timeline_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    import os
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "llm", "prompts", "timeline.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            prompt_template = f.read()
    else:
        prompt_template = "Extract a timeline of events from these chunks as JSON array with 'timestamp', 'event', 'evidence_id': {evidence_chunks}"
        
    chunks_str = json.dumps([{"id": c.id, "content": c.content} for c in state["reranked_chunks"]], indent=2)
    prompt = prompt_template.replace("{evidence_chunks}", chunks_str)
    
    try:
        timeline = await llm.complete_json(prompt, tenant_id=state["tenant_id"])
        if not isinstance(timeline, list):
            timeline = [timeline]
    except Exception:
        timeline = []
        
    state["timeline"] = timeline
    state["trace"].append(StepTrace("timeline_reconstruction", start, get_now(), {}, {"count": len(timeline)}).to_dict()[0])
    return state

async def hypothesis_generation_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    import os
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "llm", "prompts", "hypothesis_generation.txt")
    with open(prompt_path, "r") as f:
        prompt_template = f.read()
        
    chunks_str = json.dumps([{"id": c.id, "source": c.source_id, "content": c.content} for c in state["reranked_chunks"]], indent=2)
    prompt = prompt_template.replace("{incident_description}", state["description"]).replace("{entities}", json.dumps(state["entities"])).replace("{evidence_chunks}", chunks_str).replace("{timeline}", json.dumps(state.get("timeline", [])))
    
    try:
        hypotheses = await llm.complete_json(prompt, tenant_id=state["tenant_id"])
        if not isinstance(hypotheses, list):
            hypotheses = [hypotheses]
    except Exception:
        hypotheses = []
        
    state["hypotheses"] = hypotheses
    state["trace"].append(StepTrace("hypothesis_generation", start, get_now(), {}, {"count": len(hypotheses)}).to_dict()[0])
    return state

async def evidence_verification_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    verified = []
    chunk_map = {c.id: c for c in state["reranked_chunks"]}
    
    for hyp in state["hypotheses"]:
        valid_evidence = [eid for eid in hyp.get("evidence_ids", []) if eid in chunk_map]
        contradictions = [eid for eid in hyp.get("contradiction_ids", []) if eid in chunk_map]
        
        # Count independent sources
        sources = set()
        for eid in valid_evidence:
            c = chunk_map[eid]
            sources.add(c.connector_type)
            
        corroboration_count = len(sources)
        
        # Temporal check logic (basic heuristic: if we have timeline, is the hypothesis strictly after the first error?)
        # For a true strict check we'd parse timestamps, but we rely on LLM reasoning and contradiction evidence here
        is_verified = corroboration_count >= 1 and len(valid_evidence) > len(contradictions)
        
        hyp["verified"] = is_verified
        hyp["corroboration_count"] = corroboration_count
        hyp["contradiction_ids"] = contradictions
        hyp["valid_evidence_ids"] = valid_evidence
        verified.append(hyp)
        
    state["verified_hypotheses"] = verified
    state["trace"].append(StepTrace("evidence_verification", start, get_now(), {}, {"verified_count": len([h for h in verified if h["verified"]])}).to_dict()[0])
    return state

async def confidence_scoring_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    if not state["verified_hypotheses"]:
        state["confidence"] = {"score": 0, "bucket": "Insufficient", "breakdown": {}}
        return state
        
    best_hyp = max(state["verified_hypotheses"], key=lambda h: h["corroboration_count"])
    chunk_map = {c.id: c for c in state["reranked_chunks"]}
    
    valid_ev = [chunk_map[eid] for eid in best_hyp.get("valid_evidence_ids", [])]
    retrieval_score = sum(c.relevance_score for c in valid_ev) / len(valid_ev) if valid_ev else 0.0
    
    corroboration_score = min(1.0, best_hyp["corroboration_count"] / 3.0)
    
    avail = len(state["source_plan"]["available"])
    coverage_score = len(state["source_plan"]["queried"]) / avail if avail > 0 else 0.0
    
    recency_score = 1.0 # Simplified for now
    contradiction_penalty = -0.3 if best_hyp["contradiction_ids"] else 0.0
    
    final_score = (retrieval_score * 0.3 + corroboration_score * 0.35 + coverage_score * 0.2 + recency_score * 0.15) + contradiction_penalty
    final_score = max(0.0, min(1.0, final_score)) # Clamp between 0 and 1
    
    if final_score >= 0.85: bucket = "High"
    elif final_score >= 0.60: bucket = "Medium"
    elif final_score >= 0.2: bucket = "Low"
    else: bucket = "Insufficient"
    
    breakdown = {
        "retrieval_relevance": retrieval_score,
        "corroboration": corroboration_score,
        "source_coverage": coverage_score,
        "temporal_recency": recency_score,
        "contradiction_penalty": contradiction_penalty
    }
    
    state["confidence"] = {"score": final_score, "bucket": bucket, "breakdown": breakdown}
    state["trace"].append(StepTrace("confidence_scoring", start, get_now(), {}, state["confidence"]).to_dict()[0])
    return state

async def insufficient_evidence_gate_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    state["insufficient_evidence"] = True
    state["final_report"] = {
        "report": "Insufficient evidence to determine root cause.",
        "checked": state["source_plan"]["queried"],
        "needed": "More logs or code context."
    }
    state["trace"].append(StepTrace("insufficient_evidence", start, get_now(), {}, {}).to_dict()[0])
    return state

async def synthesis_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    import os
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "llm", "prompts", "synthesis.txt")
    with open(prompt_path, "r") as f:
        prompt_template = f.read()
        
    valid_hyps = [h for h in state["verified_hypotheses"] if h["verified"]]
    ev_ids = set()
    for h in valid_hyps:
        ev_ids.update(h.get("evidence_ids", []))
        
    chunks = [c for c in state["reranked_chunks"] if c.id in ev_ids]
    chunks_str = json.dumps([{"id": c.id, "content": c.content} for c in chunks], indent=2)
    
    prompt = prompt_template.replace("{incident_description}", state["description"]).replace("{verified_hypotheses}", json.dumps(valid_hyps)).replace("{evidence_chunks}", chunks_str)
    
    try:
        report = await llm.complete(prompt, tenant_id=state["tenant_id"])
    except Exception as e:
        report = f"Failed to synthesize report: {e}"
        
    state["final_report"] = {"report": report}
    state["trace"].append(StepTrace("synthesis", start, get_now(), {}, {}).to_dict()[0])
    return state
