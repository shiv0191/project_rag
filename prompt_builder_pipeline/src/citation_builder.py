from typing import List

from src.models import RetrievedChunk


class CitationBuilder:
    def __init__(self):
        pass

    def build(self, chunks: List[RetrievedChunk]) -> str:
        """
        Build a citation section from the selected chunks.
        """

        citations = []

        seen = set()

        for chunk in chunks:
            citation = f"{chunk.source} (Page {chunk.page})"

            if citation not in seen:
                seen.add(citation)
                citations.append(citation)

        return "\n".join(citations)