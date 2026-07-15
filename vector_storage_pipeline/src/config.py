from pathlib import Path


class Settings:
    """
    Configuration settings for the Vector Storage Pipeline.
    """

    # ==========================================================
    # Project Directories
    # ==========================================================

    BASE_DIR = Path(__file__).resolve().parent.parent

    INPUT_DIR = BASE_DIR / "input"

    OUTPUT_DIR = BASE_DIR / "output"

    LOG_DIR = BASE_DIR / "logs"

    # ==========================================================
    # Input Files
    # ==========================================================

    EMBEDDINGS_INPUT_DIR = (
        INPUT_DIR / "embeddings"
    )

    EMBEDDINGS_FILE = (
        EMBEDDINGS_INPUT_DIR /
        "sample_embeddings.jsonl"
    )

    # ==========================================================
    # Qdrant Configuration
    # ==========================================================

    QDRANT_DB_PATH = (
        BASE_DIR / "qdrant_data"
    )

    COLLECTION_NAME = (
        "manual_chunks"
    )

    DISTANCE_METRIC = "cosine"

    RESET_COLLECTION = True

    BATCH_SIZE = 100

    # ==========================================================
    # Logging
    # ==========================================================

    LOG_FILE = (
        LOG_DIR /
        "storage_pipeline.log"
    )


settings = Settings()
