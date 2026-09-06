import os
import json
from langchain_core.messages import HumanMessage, SystemMessage
from src.core.database import SessionLocal
from src.models.domain import TenantSettings

class LLMClient:
    def _get_llm(self, tenant_id: str):
        db = SessionLocal()
        try:
            settings = db.query(TenantSettings).filter(TenantSettings.tenant_id == tenant_id).first()
            provider = settings.llm_provider if settings and settings.llm_provider else os.getenv("LLM_PROVIDER", "gemini")
            api_key = settings.llm_api_key if settings and settings.llm_api_key else os.getenv("GEMINI_API_KEY", "dummy")
            ollama_url = settings.ollama_base_url if settings and settings.ollama_base_url else os.getenv("OLLAMA_URL", "http://localhost:11434")
            
            gemini_model = settings.llm_model if settings and settings.llm_model else "gemini-3.7-flash"
            ollama_model = settings.ollama_model if settings and settings.ollama_model else "llama3"
            
            if provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(model=gemini_model, google_api_key=api_key, max_retries=1)
            else:
                from langchain_community.chat_models import ChatOllama
                return ChatOllama(model=ollama_model, base_url=ollama_url)
        finally:
            db.close()

    async def complete(self, prompt: str, system: str = "", tenant_id: str = None) -> str:
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
                raise e

    async def complete_json(self, prompt: str, system: str = "", tenant_id: str = None) -> dict:
        content = await self.complete(prompt + "\n\nReturn ONLY a valid JSON object or array. Do not include markdown code blocks.", system, tenant_id)
        
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from LLM: {e}\nContent: {content}")

client = LLMClient()
