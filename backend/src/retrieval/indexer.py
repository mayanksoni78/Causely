import uuid
import hashlib
from collections import defaultdict
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session
from src.models.domain import DocumentChunk
from src.connectors.base import EvidenceChunk
from src.retrieval.embeddings import embed_texts, embed_query

class HierarchicalIndexer:
    
    def _hash_content(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def index_chunks(self, db: Session, tenant_id: str, project_id: str, source_id: str, connector_type: str, chunks: list[dict]) -> int:
        if not chunks:
            return 0
            
        texts_to_embed = [c["content"] for c in chunks]
        embeddings = embed_texts(texts_to_embed)
        
        count = 0
        for i, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            db_chunk = DocumentChunk(
                id=chunk_id,
                source_id=source_id,
                tenant_id=tenant_id,
                project_id=project_id,
                connector_type=connector_type,
                content=chunk["content"],
                metadata_json=chunk.get("metadata", {}),
                embedding=embeddings[i],
                layer_level=chunk.get("layer_level", 0)
            )
            db.add(db_chunk)
            count += 1
            
        db.commit()
        return count

    def retrieve(self, db: Session, tenant_id: str, project_id: str, query: str, source_ids: list[str] | None = None, top_k: int = 5) -> list[EvidenceChunk]:
        # Vector search using pgvector
        query_emb = embed_query(query)
        
        q_vec = db.query(DocumentChunk).filter(DocumentChunk.project_id == project_id)
        if source_ids:
            q_vec = q_vec.filter(DocumentChunk.source_id.in_(source_ids))
            
        # Get top 40 vector results
        vec_chunks = q_vec.order_by(DocumentChunk.embedding.cosine_distance(query_emb)).limit(top_k * 2).all()
        
        # Get all chunks for BM25
        q_all = db.query(DocumentChunk).filter(DocumentChunk.project_id == project_id)
        if source_ids:
            q_all = q_all.filter(DocumentChunk.source_id.in_(source_ids))
        all_chunks = q_all.limit(1000).all()
        
        if not all_chunks:
            return []
            
        # BM25 setup
        corpus = [chunk.content.split(" ") for chunk in all_chunks]
        bm25_index = BM25Okapi(corpus)
        tokenized = query.split(" ")
        scores = bm25_index.get_scores(tokenized)
        
        bm25_scores = {chunk.id: score for chunk, score in zip(all_chunks, scores)}
        
        # RRF (Reciprocal Rank Fusion)
        fused_scores = defaultdict(float)
        
        # Add vector ranks
        for rank, chunk in enumerate(vec_chunks):
            fused_scores[chunk.id] += 1.0 / (rank + 60)
            
        # Add bm25 ranks
        scored_bm25 = [(score, chunk) for chunk, score in zip(all_chunks, scores) if score > 0]
        scored_bm25.sort(key=lambda x: x[0], reverse=True)
        for rank, (score, chunk) in enumerate(scored_bm25[:top_k * 2]):
            fused_scores[chunk.id] += 1.0 / (rank + 60)
            
        # Sort combined
        chunk_map = {c.id: c for c in all_chunks}
        final_sorted = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for chunk_id, _ in final_sorted[:top_k]:
            db_chunk = chunk_map[chunk_id]
            results.append(EvidenceChunk(
                id=db_chunk.id,
                source_id=str(db_chunk.source_id),
                connector_type=db_chunk.connector_type,
                content=db_chunk.content,
                metadata=db_chunk.metadata_json,
                relevance_score=fused_scores[chunk_id]
            ))
            
        return results

indexer = HierarchicalIndexer()
