import re

with open("backend/src/pipeline/nodes.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace evidence_verification_node
old_ev = """async def evidence_verification_node(state: InvestigationState) -> InvestigationState:
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
    return state"""

new_ev = """async def evidence_verification_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    verified = []
    chunk_map = {str(c.id).strip(): c for c in state.get("reranked_chunks", [])}
    
    for hyp in state.get("hypotheses", []):
        raw_evidence_ids = [str(eid).strip() for eid in hyp.get("evidence_ids", [])]
        raw_contradiction_ids = [str(eid).strip() for eid in hyp.get("contradiction_ids", [])]
        
        valid_evidence = [eid for eid in raw_evidence_ids if eid in chunk_map]
        invalid_evidence = [eid for eid in raw_evidence_ids if eid not in chunk_map]
        contradictions = [eid for eid in raw_contradiction_ids if eid in chunk_map]
        
        sources = set()
        for eid in valid_evidence:
            sources.add(chunk_map[eid].connector_type)
            
        corroboration_count = len(sources)
        
        is_verified = bool(len(valid_evidence) > 0 and len(valid_evidence) > len(contradictions))
        
        hyp["verified"] = is_verified
        hyp["corroboration_count"] = corroboration_count
        hyp["contradiction_ids"] = contradictions
        hyp["valid_evidence_ids"] = valid_evidence
        hyp["invalid_evidence_ids"] = invalid_evidence
        verified.append(hyp)
        
    state["verified_hypotheses"] = verified
    state["trace"].append(StepTrace("evidence_verification", start, get_now(), {}, {"verified_count": sum(1 for h in verified if h["verified"])}).to_dict()[0])
    return state"""

if old_ev in code:
    code = code.replace(old_ev, new_ev)
else:
    print("WARNING: Old evidence verification code not found")

# Replace confidence_scoring_node
old_conf = """async def confidence_scoring_node(state: InvestigationState) -> InvestigationState:
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
    return state"""

new_conf = """import math
def normalize_score(score):
    return 1.0 / (1.0 + math.exp(-score))

async def confidence_scoring_node(state: InvestigationState) -> InvestigationState:
    start = get_now()
    
    verified_hyps = [h for h in state.get("verified_hypotheses", []) if h.get("verified")]
    if not verified_hyps:
        state["confidence"] = {"score": 0.0, "bucket": "Insufficient", "breakdown": {}}
        state["trace"].append(StepTrace("confidence_scoring", start, get_now(), {}, state["confidence"]).to_dict()[0])
        return state
        
    best_hyp = max(verified_hyps, key=lambda h: (h.get("corroboration_count", 0), len(h.get("valid_evidence_ids", []))))
    chunk_map = {str(c.id).strip(): c for c in state.get("reranked_chunks", [])}
    
    valid_ev = [chunk_map[eid] for eid in best_hyp.get("valid_evidence_ids", []) if eid in chunk_map]
    if valid_ev:
        raw_retrieval_score = sum(c.relevance_score for c in valid_ev) / len(valid_ev)
        retrieval_score = normalize_score(raw_retrieval_score)
    else:
        retrieval_score = 0.0
    
    corroboration_score = min(1.0, best_hyp.get("corroboration_count", 0) / 2.0)
    
    # Coverage calculation (exclude indexer)
    avail_ext = [cid for cid in state["source_plan"].get("available", []) if cid != "indexer"]
    queried_ext = [cid for cid in state["source_plan"].get("queried", []) if cid != "indexer"]
    coverage_score = len(queried_ext) / len(avail_ext) if len(avail_ext) > 0 else 1.0
    
    recency_score = 1.0
    contradiction_penalty = -0.3 if best_hyp.get("contradiction_ids") else 0.0
    
    final_score = (retrieval_score * 0.4 + corroboration_score * 0.3 + coverage_score * 0.2 + recency_score * 0.1) + contradiction_penalty
    final_score = max(0.0, min(1.0, final_score))
    
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
    
    state["confidence"] = {"score": round(final_score, 2), "bucket": bucket, "breakdown": breakdown}
    state["trace"].append(StepTrace("confidence_scoring", start, get_now(), {}, state["confidence"]).to_dict()[0])
    return state"""

if old_conf in code:
    code = code.replace(old_conf, new_conf)
else:
    print("WARNING: Old confidence scoring code not found")

with open("backend/src/pipeline/nodes.py", "w", encoding="utf-8") as f:
    f.write(code)
