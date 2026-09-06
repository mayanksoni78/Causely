import json
import asyncio
from src.pipeline.nodes import hypothesis_generation_node
from src.llm.client import client as llm
from src.connectors.base import EvidenceChunk

class MockState(dict):
    pass

state = MockState({
    "tenant_id": "00000000-0000-0000-0000-000000000000",
    "description": "Database connection failed with bad auth",
    "entities": {},
    "timeline": [],
    "reranked_chunks": [
        EvidenceChunk(id="log1", source_id="s1", connector_type="static_log", content="2026-09-05T17:46:40.268Z database.connected", metadata={}),
        EvidenceChunk(id="log2", source_id="s1", connector_type="static_log", content="2026-09-05T17:57:59.293Z server.started", metadata={}),
        EvidenceChunk(id="log3", source_id="s1", connector_type="static_log", content="2026-09-05T17:58:00.815Z database.connection_failed bad auth : Authentication failed.", metadata={}),
        EvidenceChunk(id="commit1", source_id="s2", connector_type="github", content="GITHUB COMMIT: abcdef123\nTime: 2026-09-05T17:50:00Z\nMessage: Update port\nDiff:\n--- frontend/config.js\n+++ frontend/config.js\n- port: 5173\n+ port: 5174", metadata={})
    ],
    "trace": []
})

async def run():
    res = await hypothesis_generation_node(state)
    print(json.dumps(res["hypotheses"], indent=2))

asyncio.run(run())
