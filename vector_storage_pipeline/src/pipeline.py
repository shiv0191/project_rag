import logging

from src.config import settings
from src.qdrant_store import QdrantStore
from src.reader import StorageReader
from src.validator import StorageValidator

logger = logging.getLogger(__name__)


class StoragePipeline:
    """
    Storage Pipeline

    Responsibilities:
    1. Read embedding records
    2. Validate records
    3. Create Qdrant collection
    4. Upload vectors
    5. Verify upload
    """

    def run(self) -> None:

        logger.info("=" * 80)
        logger.info("Starting Vector Storage Pipeline")
        logger.info("=" * 80)

        #
        # Step 1
        # Read embeddings
        #

        embedding_records = StorageReader.read_embeddings()

        logger.info(
            "Loaded %d embedding records.",
            len(embedding_records)
        )

        #
        # Step 2
        # Validate embeddings
        #

        StorageValidator.validate_embeddings(
            embedding_records
        )

        logger.info(
            "Validation completed successfully."
        )

        #
        # Step 3
        # Determine vector dimension
        #

        vector_dimension = len(
            embedding_records[0]["embedding"]
        )

        logger.info(
            "Embedding dimension : %d",
            vector_dimension
        )

        #
        # Step 4
        # Connect to Qdrant
        #

        store = QdrantStore(
            database_path=str(
                settings.QDRANT_DB_PATH
            ),
            collection_name=settings.COLLECTION_NAME,
            vector_dimension=vector_dimension,
        )

        try:

            #
            # Step 5
            # Create collection
            #
            if settings.RESET_COLLECTION:
                store.delete_collection()
            store.create_collection()

            #
            # Step 6
            # Upload vectors
            #

            store.upload(
                embedding_records
            )

            #
            # Step 7
            # Verify upload
            #

            total_vectors = store.count()

            logger.info(
                "Total vectors stored : %d",
                total_vectors
            )

            if total_vectors != len(
                embedding_records
            ):
                raise RuntimeError(
                    "Upload verification failed."
                )

            logger.info(
                "Upload verification successful."
            )

        finally:

            store.close()

            logger.info(
                "Qdrant connection closed."
            )

        logger.info("=" * 80)
        logger.info(
            "Vector Storage Pipeline Completed Successfully"
        )
        logger.info("=" * 80)