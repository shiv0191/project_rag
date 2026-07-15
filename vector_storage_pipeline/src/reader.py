import json
import logging
from pathlib import Path
from typing import Dict, List

from src.config import settings

logger = logging.getLogger(__name__)


class StorageReader:
    """
    Reads input artifacts required by the storage pipeline.
    """

    @staticmethod
    def read_embeddings() -> List[Dict]:
        """
        Read embeddings from the JSONL file.

        Returns:
            List of embedding records.
        """

        file_path = settings.EMBEDDINGS_FILE

        if not file_path.exists():
            raise FileNotFoundError(
                f"Embeddings file not found: {file_path}"
            )

        logger.info("Reading embeddings from %s", file_path)

        records = []

        with open(file_path, "r", encoding="utf-8") as file:

            for line_number, line in enumerate(file, start=1):

                if not line.strip():
                    continue

                try:
                    records.append(json.loads(line))

                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid JSON at line {line_number}: {e}"
                    )

        logger.info("Loaded %d embedding records.", len(records))

        return records

    @staticmethod
    def read_id_mapping() -> Dict:
        """
        Read HNSW ID mapping.

        Returns:
            Dictionary containing HNSW index mapping.
        """

        file_path = settings.ID_MAPPING_FILE

        if not file_path.exists():
            raise FileNotFoundError(
                f"ID mapping file not found: {file_path}"
            )

        logger.info("Reading ID mapping from %s", file_path)

        with open(file_path, "r", encoding="utf-8") as file:
            mapping = json.load(file)

        logger.info("Loaded %d mapping entries.", len(mapping))

        return mapping

    @staticmethod
    def get_hnsw_index_path() -> Path:
        """
        Return the HNSW index path.

        Returns:
            Path to HNSW index.
        """

        file_path = settings.HNSW_INDEX_FILE

        if not file_path.exists():
            raise FileNotFoundError(
                f"HNSW index not found: {file_path}"
            )

        logger.info("HNSW index found.")

        return file_path