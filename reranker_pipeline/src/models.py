from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class RetrievedChunk:
    """
    Represents a single chunk returned by the retriever.
    """
    chunk_id: str
    text: str
    retriever_score: float
    metadata: Dict[str, Any]


@dataclass
class RetrievedQuery:
    """
    Represents a query and its retrieved chunks.
    """
    query: str
    results: List[RetrievedChunk]


@dataclass
class RerankedChunk:
    """
    Represents a chunk after reranking.
    """
    chunk_id: str
    text: str
    retriever_score: float
    reranker_score: float
    metadata: Dict[str, Any]


@dataclass
class RerankedQuery:
    """
    Represents a query and its reranked chunks.
    """
    query: str
    results: List[RerankedChunk]