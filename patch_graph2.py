import re

with open("backend/src/pipeline/graph.py", "r", encoding="utf-8") as f:
    code = f.read()

if "temporal_correlation_node" not in code:
    code = code.replace("from src.pipeline.nodes import (", "from src.pipeline.nodes import (\n    temporal_correlation_node,")
    code = code.replace("graph.add_node(\"reranking\", reranking_node)", "graph.add_node(\"temporal_correlation\", temporal_correlation_node)\n    graph.add_node(\"reranking\", reranking_node)")
    code = code.replace("graph.add_edge(\"retrieval\", \"reranking\")", "graph.add_edge(\"retrieval\", \"temporal_correlation\")\n    graph.add_edge(\"temporal_correlation\", \"reranking\")")

    with open("backend/src/pipeline/graph.py", "w", encoding="utf-8") as f:
        f.write(code)
