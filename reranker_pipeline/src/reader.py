import json

from src.models import RetrievedChunk, RetrievedQuery


class Reader:
    """
    Reads retrieval results from a JSON file.
    """

    @staticmethod
    def read(input_file: str) -> list[RetrievedQuery]:
        """
        Reads retrieval results from a JSON file.

        Args:
            input_file: Path to the retriever output JSON file.

        Returns:
            List of RetrievedQuery objects.
        """

        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        queries = []

        for item in data:

            chunks = []

            for result in item["results"]:

                chunk = RetrievedChunk(
                    chunk_id=result["chunk_id"],
                    text=result["text"],
                    retriever_score=result["retriever_score"],
                    metadata=result.get("metadata", {})
                )

                chunks.append(chunk)

            query = RetrievedQuery(
                query=item["query"],
                results=chunks
            )

            queries.append(query)

        return queries