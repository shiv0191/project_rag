import json
import numpy as np

from src.embedder import Embedder


class Retriever:

    def __init__(self, embedding_file):

        self.embedding_file = embedding_file

        self.embedder = Embedder()

        self.records = self.load_embeddings()

    def load_embeddings(self):

        records = []

        with open(
            self.embedding_file,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:
                records.append(json.loads(line))

        return records

    def search(
        self,
        query,
        top_k=5,
    ):

        print(f"\nQuery : {query}")

        query_embedding = self.embedder.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        scores = []

        for record in self.records:

            chunk_embedding = np.array(
                record["embedding"]
            )

            similarity = np.dot(
                query_embedding,
                chunk_embedding,
            )

            scores.append(
                (
                    similarity,
                    record,
                )
            )

        scores.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        return scores[:top_k]
