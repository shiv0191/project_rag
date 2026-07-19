from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class RetrievedChunk:
    """
    Represents one chunk selected by the reranker.
    """

    chunk_id: str
    page: int
    text: str
    score: float
    source: str
    metadata: Dict


@dataclass
class PromptContext:
    """
    Represents the collection of chunks that will be
    provided as context to the LLM.
    """

    question: str
    chunks: List[RetrievedChunk]


@dataclass
class PromptRequest:
    """
    Input required for building the final prompt.
    """

    system_prompt: str
    context: PromptContext


@dataclass
class PromptResponse:
    """
    Final prompt produced by the Prompt Builder.
    """

    prompt: str
    token_count: Optional[int] = None
