import uuid
from rank_bm25 import BM25Okapi
from src.connectors.base import SourceConnector, PermissionReport, ConnectorStatus, EvidenceQuery, EvidenceChunk

class StaticLogConnector(SourceConnector):
    def __init__(self, log_text: str):
        self.log_text = log_text
        self.lines = log_text.split("\n")
        tokenized_corpus = [line.split(" ") for line in self.lines]
        self.bm25 = BM25Okapi(tokenized_corpus) if tokenized_corpus else None
        self.connector_id = f"static_log_{uuid.uuid4().hex[:8]}"

    def check_permissions(self) -> PermissionReport:
        return PermissionReport(
            connector_id=self.connector_id,
            is_read_only=True,
            granted_scopes=["log_search"],
            warnings=[]
        )

    def list_capabilities(self) -> list[str]:
        return ["log_search"]

    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]:
        if not self.bm25:
            return []
            
        tokenized_query = query.query_text.split(" ")
        scores = self.bm25.get_scores(tokenized_query)
        
        results = []
        for i, score in enumerate(scores):
            if score > 0:
                results.append((score, i))
                
        results.sort(key=lambda x: x[0], reverse=True)
        
        chunks = []
        for score, idx in results[:query.max_results]:
            chunks.append(EvidenceChunk(
                id=str(uuid.uuid4()),
                source_id=self.connector_id,
                connector_type="static_log",
                content=self.lines[idx],
                metadata={"log_line": idx + 1, "layer_level": 2},
                relevance_score=score
            ))
            
        return chunks

    def health_check(self) -> ConnectorStatus:
        if len(self.log_text) > 0:
            return ConnectorStatus(healthy=True, message="Log loaded")
        return ConnectorStatus(healthy=False, message="Empty log")
