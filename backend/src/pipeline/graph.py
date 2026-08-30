from langgraph.graph import StateGraph, END
from src.pipeline.state import InvestigationState
from src.pipeline.nodes import (
    intake_node,
    source_planning_node,
    retrieval_node,
    reranking_node,
    hypothesis_generation_node,
    evidence_verification_node,
    confidence_scoring_node,
    insufficient_evidence_gate_node,
    synthesis_node,
    timeline_node
)

def build_graph():
    graph = StateGraph(InvestigationState)
    
    graph.add_node("intake", intake_node)
    graph.add_node("source_planning", source_planning_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("reranking", reranking_node)
    graph.add_node("timeline", timeline_node)
    graph.add_node("hypothesis_generation", hypothesis_generation_node)
    graph.add_node("evidence_verification", evidence_verification_node)
    graph.add_node("confidence_scoring", confidence_scoring_node)
    graph.add_node("insufficient_evidence", insufficient_evidence_gate_node)
    graph.add_node("synthesis", synthesis_node)
    
    graph.set_entry_point("intake")
    graph.add_edge("intake", "source_planning")
    graph.add_edge("source_planning", "retrieval")
    graph.add_edge("retrieval", "reranking")
    graph.add_edge("reranking", "timeline")
    graph.add_edge("timeline", "hypothesis_generation")
    graph.add_edge("hypothesis_generation", "evidence_verification")
    graph.add_edge("evidence_verification", "confidence_scoring")
    
    def route_confidence(state: InvestigationState):
        conf = state.get("confidence", {})
        if conf.get("score", 0) < 0.2 or not any(h.get("verified") for h in state.get("verified_hypotheses", [])):
            return "insufficient_evidence"
        return "synthesis"
        
    graph.add_conditional_edges("confidence_scoring", route_confidence, {
        "insufficient_evidence": "insufficient_evidence",
        "synthesis": "synthesis"
    })
    
    graph.add_edge("insufficient_evidence", END)
    graph.add_edge("synthesis", END)
    
    return graph.compile()

investigation_graph = build_graph()
