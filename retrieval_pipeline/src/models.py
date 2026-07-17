from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievalResult:
    rank: int
    chunk_id: str
    score: float
    page: int
    text: str
    source: str
    metadata: dict[str, Any]
    