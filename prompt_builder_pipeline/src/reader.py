import json
from typing import List

from src.models import RetrievedChunk


class PromptReader:
    def __init__(self, input_file: str):
        self.input_file = input_file

    def read(self) -> List[RetrievedChunk]:
        with open(self.input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        chunks = []

        for query_result in data:
            for record in query_result["results"]:
                chunk = RetrievedChunk(
                    chunk_id=record["chunk_id"],
                    page=record["metadata"]["page"],
                    text=record["text"],
                    score=record["reranker_score"],
                    source=record["metadata"]["source"],
                    metadata=record["metadata"]
                )

                chunks.append(chunk)

        return chunks