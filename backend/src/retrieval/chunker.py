import ast

def chunk_code(content: str, file_path: str) -> list[dict]:
    chunks = []
    if file_path.endswith('.py'):
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    start_line = node.lineno
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                    
                    lines = content.splitlines()[start_line-1:end_line]
                    chunk_content = "\n".join(lines)
                    chunk_type = 'class' if isinstance(node, ast.ClassDef) else 'function'
                    
                    chunks.append({
                        "content": chunk_content,
                        "start_line": start_line,
                        "end_line": end_line,
                        "chunk_type": chunk_type
                    })
            if chunks:
                return chunks
        except SyntaxError:
            pass
            
    # Fallback to text chunking
    return chunk_text(content)

def chunk_text(content: str, chunk_size: int = 512, overlap: int = 128) -> list[dict]:
    chunks = []
    start = 0
    content_len = len(content)
    
    # Very basic character chunking for now
    while start < content_len:
        end = start + chunk_size
        chunk_str = content[start:end]
        chunks.append({
            "content": chunk_str,
            "start_line": start, # Just using start char index as rough line for now
            "end_line": end,
            "chunk_type": "segment"
        })
        start += chunk_size - overlap
        
    return chunks
