import asyncio
import time
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, Literal

Capability = Literal["commit_history", "pull_requests", "issues", "file_contents", "log_search"]

@dataclass
class PermissionReport:
    connector_id: str
    is_read_only: bool
    granted_scopes: list[str]
    warnings: list[str]

@dataclass
class ConnectorStatus:
    healthy: bool
    message: str

@dataclass
class EvidenceQuery:
    query_text: str
    entity_filters: dict
    timeframe_start: datetime | None = None
    timeframe_end: datetime | None = None
    max_results: int = 20

@dataclass
class EvidenceChunk:
    id: str
    source_id: str
    connector_type: str
    content: str
    metadata: dict
    relevance_score: float = 0.0

class SourceConnector(Protocol):
    def check_permissions(self) -> PermissionReport: ...
    def list_capabilities(self) -> list[str]: ...
    def fetch(self, query: EvidenceQuery) -> list[EvidenceChunk]: ...
    def health_check(self) -> ConnectorStatus: ...

class RateLimitError(Exception):
    pass

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.tokens = float(calls_per_minute)
        self.last_refill = time.monotonic()
        self.rate = calls_per_minute / 60.0

    async def acquire(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(float(self.calls_per_minute), self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens < 1.0:
            raise RateLimitError("Rate limit exceeded")
        
        self.tokens -= 1.0

def with_backoff(coro_func):
    async def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries + 1):
            try:
                return await coro_func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise e
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(sleep_time)
    return wrapper
