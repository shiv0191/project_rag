import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class StorageValidator:
    """
    Validates embedding records before storing them in Qdrant.
    """

    @staticmethod
    def validate_embeddings(records: List[Dict]) -> None:
        """
        Validate embedding records.

        Args:
            records: List of embedding records.

        Raises:
            ValueError: If validation fails.
        """

        if not records:
            raise ValueError("Embedding file is empty.")

        logger.info("Validating embedding records...")

        chunk_ids = set()

        embedding_dimension = None

        for index, record in enumerate(records, start=1):

            #
            # Required fields
            #

            required_fields = [
                "chunk_id",
                "page",
                "text",
                "embedding_dimension",
                "embedding",
                "metadata",
            ]

            for field in required_fields:

                if field not in record:
                    raise ValueError(
                        f"Record {index}: Missing '{field}'."
                    )

            #
            # Duplicate chunk ids
            #

            chunk_id = record["chunk_id"]

            if chunk_id in chunk_ids:

                raise ValueError(
                    f"Duplicate chunk_id: {chunk_id}"
                )

            chunk_ids.add(chunk_id)

            #
            # Validate text
            #

            text = record["text"]

            if not isinstance(text, str):

                raise ValueError(
                    f"{chunk_id}: text must be string."
                )

            if not text.strip():

                raise ValueError(
                    f"{chunk_id}: Empty text."
                )

            #
            # Validate embedding
            #

            embedding = record["embedding"]

            if not isinstance(embedding, list):

                raise ValueError(
                    f"{chunk_id}: embedding must be list."
                )

            if len(embedding) == 0:

                raise ValueError(
                    f"{chunk_id}: Empty embedding."
                )

            if embedding_dimension is None:

                embedding_dimension = len(
                    embedding
                )

            elif len(embedding) != embedding_dimension:

                raise ValueError(
                    f"{chunk_id}: Inconsistent embedding dimension."
                )

            #
            # Validate declared dimension
            #

            if record["embedding_dimension"] != len(embedding):

                raise ValueError(
                    f"{chunk_id}: embedding_dimension "
                    "does not match actual vector size."
                )

            #
            # Validate metadata
            #

            metadata = record["metadata"]

            if not isinstance(metadata, dict):

                raise ValueError(
                    f"{chunk_id}: metadata must be dictionary."
                )

        logger.info(
            "Embedding validation completed successfully."
        )
