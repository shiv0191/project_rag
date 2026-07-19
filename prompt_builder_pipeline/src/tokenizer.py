from typing import List

from src.models import RetrievedChunk


class Tokenizer:
    def __init__(self):
        pass

    def count_text_tokens(self, text: str) -> int:
        """
        Approximate token count.
        Replace with the model-specific tokenizer later.
        """
        return max(1, len(text.split()))

    def count_chunk_tokens(self, chunk: RetrievedChunk) -> int:
        return self.count_text_tokens(chunk.text)

    def count_chunks_tokens(self, chunks: List[RetrievedChunk]) -> int:
        total = 0

        for chunk in chunks:
            total += self.count_chunk_tokens(chunk)

        return total

    def count_prompt_tokens(self, prompt: str) -> int:
        return self.count_text_tokens(prompt)