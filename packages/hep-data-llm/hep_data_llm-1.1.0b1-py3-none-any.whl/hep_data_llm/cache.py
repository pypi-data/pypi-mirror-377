from enum import Enum


class CacheType(str, Enum):
    """Enumeration of caches that can be selectively ignored."""

    HINTS = "hints"
    LLM = "llm"
    CODE = "code"
