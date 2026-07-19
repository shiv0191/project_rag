from typing import List

from src.models import RetrievedChunk
from src.tokenizer import Tokenizer


class Truncator:
    def __init__(self, max_context_tokens: int):
        self.max_context_tokens = max_context_tokens
        self.tokenizer = Tokenizer()

    def truncate(self, chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """
        Select as many chunks as fit within the context token limit.
        """

        selected_chunks = []
        total_tokens = 0

        for chunk in chunks:
            chunk_tokens = self.tokenizer.count_chunk_tokens(chunk)

            if total_tokens + chunk_tokens > self.max_context_tokens:
                break

            selected_chunks.append(chunk)
            total_tokens += chunk_tokens

        return selected_chunks