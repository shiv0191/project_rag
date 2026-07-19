import json
import os

from src.models import RerankedQuery


class Writer:
    """
    Writes reranked results to a JSON file.
    """

    @staticmethod
    def write(
        output_file: str,
        reranked_queries: list[RerankedQuery]
    ) -> None:
        """
        Save reranked queries to a JSON file.
        """

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        data = []

        for query in reranked_queries:

            results = []

            for chunk in query.results:

                results.append({
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "retriever_score": chunk.retriever_score,
                    "reranker_score": chunk.reranker_score,
                    "metadata": chunk.metadata
                })

            data.append({
                "query": query.query,
                "results": results
            })

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )