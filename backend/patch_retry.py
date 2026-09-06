import re

with open("backend/src/llm/client.py", "r", encoding="utf-8") as f:
    code = f.read()

new_complete = """    async def complete(self, prompt: str, system: str = "", tenant_id: str = None) -> str:
        import asyncio
        import logging
        logger = logging.getLogger(__name__)
        
        if not tenant_id:
            tenant_id = "00000000-0000-0000-0000-000000000000"
        
        llm = self._get_llm(tenant_id)
        messages = []
        if system:
            messages.append(SystemMessage(content=system))
        messages.append(HumanMessage(content=prompt))
        
        max_attempts = 3
        base_delay = 2.0
        
        for attempt in range(max_attempts):
            try:
                res = await llm.ainvoke(messages)
                content = res.content
                if isinstance(content, list):
                    return content[0].get("text", "") if isinstance(content[0], dict) else str(content)
                return content
            except Exception as e:
                err_str = str(e).lower()
                is_retryable = any(x in err_str for x in ["503", "504", "unavailable", "timeout", "too many requests", "429", "overloaded"])
                
                if is_retryable and attempt < max_attempts - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"LLM request failed (attempt {attempt+1}/{max_attempts}). Retrying in {delay}s. Error: {e}")
                    await asyncio.sleep(delay)
                    continue
                
                logger.error(f"LLM request failed permanently after {attempt+1} attempts. Error: {e}")
                raise e"""

old_complete = """    async def complete(self, prompt: str, system: str = "", tenant_id: str = None) -> str:
        if not tenant_id:
            # Fallback for generic test
            tenant_id = "00000000-0000-0000-0000-000000000000"
        
        llm = self._get_llm(tenant_id)
        messages = []
        if system:
            messages.append(SystemMessage(content=system))
        messages.append(HumanMessage(content=prompt))
        
        res = await llm.ainvoke(messages)
        content = res.content
        if isinstance(content, list):
            return content[0].get("text", "") if isinstance(content[0], dict) else str(content)
        return content"""

code = code.replace(old_complete, new_complete)

with open("backend/src/llm/client.py", "w", encoding="utf-8") as f:
    f.write(code)
