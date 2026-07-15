import logging
import shutil
from pathlib import Path
from typing import Dict

from src.config import settings

logger = logging.getLogger(__name__)

from dataclasses import dataclass

@dataclass
class StoragePackage:
    """
    Represents the packaged storage artifacts.
    """

    storage_dir: Path

    embeddings_file: Path

    index_file: Path

    mapping_file: Path

class StorageBuilder:
    """
    Builds the storage package by organizing validated
    artifacts into a deployable directory structure.
    """

    @staticmethod
    def build() -> StoragePackage:
        """
        Create the storage package.

        Returns:
            StoragePackage containing paths of packaged artifacts.
        """

        logger.info("Creating storage package...")

        # -------------------------------------------------
        # Create directory structure
        # -------------------------------------------------

        settings.EMBEDDINGS_STORAGE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        settings.INDEXES_STORAGE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        # -------------------------------------------------
        # Copy embedding file
        # -------------------------------------------------

        shutil.copy2(
            settings.EMBEDDINGS_FILE,
            settings.EMBEDDINGS_STORAGE_FILE
        )

        logger.info(
            "Copied embeddings -> %s",
            settings.EMBEDDINGS_STORAGE_FILE
        )

        # -------------------------------------------------
        # Copy HNSW index
        # -------------------------------------------------

        shutil.copy2(
            settings.HNSW_INDEX_FILE,
            settings.HNSW_INDEX_STORAGE_FILE
        )

        logger.info(
            "Copied HNSW index -> %s",
            settings.HNSW_INDEX_STORAGE_FILE
        )

        # -------------------------------------------------
        # Copy ID mapping
        # -------------------------------------------------

        shutil.copy2(
            settings.ID_MAPPING_FILE,
            settings.ID_MAPPING_STORAGE_FILE
        )

        logger.info(
            "Copied ID mapping -> %s",
            settings.ID_MAPPING_STORAGE_FILE
        )

        logger.info("Storage package created successfully.")

        return StoragePackage(
            storage_dir=settings.STORAGE_DIR,
            embeddings_file=settings.EMBEDDINGS_STORAGE_FILE,
            index_file=settings.HNSW_INDEX_STORAGE_FILE,
            mapping_file=settings.ID_MAPPING_STORAGE_FILE,
        )