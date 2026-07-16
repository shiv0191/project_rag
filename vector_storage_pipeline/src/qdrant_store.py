import logging
from typing import Dict, List

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

logger = logging.getLogger(__name__)


class QdrantStore:
    """
    Handles all Qdrant database operations.
    """

    def __init__(
        self,
        database_path: str,
        collection_name: str,
        vector_dimension: int,
    ):

        self.client = QdrantClient(path=database_path)

        self.collection_name = collection_name

        self.vector_dimension = vector_dimension

    def create_collection(self) -> None:
        """
        Create the collection if it does not already exist.
        """

        collections = self.client.get_collections()

        existing_collections = [
            collection.name
            for collection in collections.collections
        ]

        if self.collection_name in existing_collections:

            logger.info(
                "Collection '%s' already exists.",
                self.collection_name,
            )

            return

        logger.info(
            "Creating collection '%s'...",
            self.collection_name,
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_dimension,
                distance=Distance.COSINE,
            ),
        )

        logger.info("Collection created successfully.")

    def upload(
        self,
        records: List[Dict],
        batch_size: int = 100,
    ) -> None:

        logger.info(
            "Uploading %d vectors...",
            len(records),
        )

        total = len(records)

        for start in range(0, total, batch_size):

            end = min(start + batch_size, total)

            batch = records[start:end]

            points = []

            for index, record in enumerate(batch, start=start):

                metadata = record["metadata"]

                payload = {

                    # Primary fields
                    "chunk_id": record["chunk_id"],
                    "page": record["page"],
                    "text": record["text"],

                    # Frequently queried metadata
                    "source": metadata.get("source"),
                    "source_name": metadata.get("source_name"),
                    "page_number": metadata.get("page_number"),
                    "token_count": metadata.get("token_count"),
                    "content_type": metadata.get("content_type"),

                    # Keep the original metadata
                    "metadata": metadata,
                }

                points.append(

                    PointStruct(

                        id=index,

                        vector=record["embedding"],

                        payload=payload,
                    )

                )

            self.client.upsert(

                collection_name=self.collection_name,

                points=points,

                wait=True,
            )

            logger.info(
                "Uploaded %d/%d vectors.",
                end,
                total,
            )

        logger.info("Upload completed successfully.")

    def count(self) -> int:
        """
        Return number of stored vectors.
        """

        response = self.client.count(
            collection_name=self.collection_name,
            exact=True,
        )

        return response.count

    def collection_exists(self) -> bool:
        """
        Check if the collection exists.
        """

        collections = self.client.get_collections()

        return any(
            collection.name == self.collection_name
            for collection in collections.collections
        )

    def delete_collection(self) -> None:
        """
        Delete the collection if it exists.
        """

        if self.collection_exists():

            logger.info(
                "Deleting collection '%s'.",
                self.collection_name,
            )

            self.client.delete_collection(
                self.collection_name
            )

            logger.info(
                "Collection deleted."
            )

    def close(self) -> None:
        """
        Close the Qdrant client.
        """

        self.client.close()
