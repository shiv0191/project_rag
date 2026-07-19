from typing import List

from src.config import (
    CHUNK_SEPARATOR,
    CONTEXT_SEPARATOR,
    PAGE_TEMPLATE,
)
from src.models import RetrievedChunk


class Formatter:
    def __init__(self):
        pass

    def format_chunk(self, chunk: RetrievedChunk) -> str:
        return PAGE_TEMPLATE.format(
            source=chunk.source,
            page=chunk.page,
            text=chunk.text.strip()
        )

    def format_context(self, chunks: List[RetrievedChunk]) -> str:
        formatted_chunks = [
            self.format_chunk(chunk)
            for chunk in chunks
        ]

        return CONTEXT_SEPARATOR.join(formatted_chunks)

    def format_chunks(self, chunks: List[RetrievedChunk]) -> str:
        formatted_chunks = [
            self.format_chunk(chunk)
            for chunk in chunks
        ]

        return CHUNK_SEPARATOR.join(formatted_chunks)