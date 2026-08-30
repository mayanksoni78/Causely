from typing import TypedDict
from src.connectors.base import EvidenceChunk

class InvestigationState(TypedDict):
    incident_id: str
    tenant_id: str
    project_id: str
    description: str
    entities: dict
    source_plan: dict
    retrieved_chunks: list[EvidenceChunk]
    reranked_chunks: list[EvidenceChunk]
    timeline: list[dict]
    hypotheses: list[dict]
    verified_hypotheses: list[dict]
    confidence: dict | None
    final_report: dict | None
    trace: list[dict]
    insufficient_evidence: bool
