import json

from src.models import RetrievalResult


class Retriever:
    def __init__(self, index, id_mapping_file, payload_loader):
        self.index = index
        self.payload_loader = payload_loader

        with open(id_mapping_file, "r", encoding="utf-8") as file:
            self.id_mapping = json.load(file)

    def search(self, query_vector, top_k):
        """
        Perform ANN search using HNSW.

        Args:
            query_vector: Query embedding
            top_k: Number of nearest neighbours

        Returns:
            list[RetrievalResult]
        """

        labels, distances = self.index.knn_query(
            query_vector,
            k=top_k
        )

        results = []

        for rank, (label, distance) in enumerate(
            zip(labels[0], distances[0]),
            start=1
        ):

            chunk_id = self.id_mapping[str(label)]
            print(f"Label      : {label}")
            print(f"Chunk ID   : {chunk_id}")
            print(f"Type       : {type(chunk_id)}")
            payload = self.payload_loader.get(chunk_id)

            if payload is None:
                print(f"Payload for chunk ID {chunk_id} not found.")
                continue

            # result = RetrievalResult(
            #     rank=rank,
            #     chunk_id=chunk_id,
            #     score=1.0 - float(distance),
            #     page=payload["page"],
            #     text=payload["text"],
            #     source=payload["source"],
            #     metadata=payload["metadata"],
            # )

            result = RetrievalResult(
                rank=rank,
                chunk_id=chunk_id,
                score=1.0 - float(distance),
                page=payload["page"],
                text=payload["text"],
                source=payload["metadata"]["source"],
                metadata=payload["metadata"],
            )


            results.append(result)

        return results
    