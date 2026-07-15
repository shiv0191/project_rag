import json
import logging
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from src.config import settings
from src.storage_builder import StoragePackage
from src.utils import calculate_sha256, file_size

logger = logging.getLogger(__name__)


@dataclass
class Manifest:
    """
    Represents metadata describing a packaged storage bundle.
    """

    storage_version: str

    created_at: str

    chunk_count: int

    embedding_dimension: int

    distance_metric: str

    embeddings_file: str

    embeddings_size: int

    embeddings_sha256: str

    index_file: str

    index_size: int

    index_sha256: str

    mapping_file: str

    mapping_size: int

    mapping_sha256: str


class ManifestBuilder:
    """
    Generates manifest.json for the packaged storage.
    """

    @staticmethod
    def build(
        package: StoragePackage,
        embedding_records: List[Dict],
    ) -> Path:

        logger.info("Generating storage manifest...")

        if not embedding_records:
            raise ValueError(
                "Embedding records are empty."
            )

        embedding_dimension = len(
            embedding_records[0]["vector"]
        )

        manifest = Manifest(

            storage_version=settings.STORAGE_VERSION,

            created_at=datetime.utcnow().isoformat() + "Z",

            chunk_count=len(embedding_records),

            embedding_dimension=embedding_dimension,

            distance_metric=settings.DISTANCE_METRIC,

            embeddings_file=str(
                package.embeddings_file.relative_to(
                    package.storage_dir
                )
            ),

            embeddings_size=file_size(
                package.embeddings_file
            ),

            embeddings_sha256=calculate_sha256(
                package.embeddings_file
            ),

            index_file=str(
                package.index_file.relative_to(
                    package.storage_dir
                )
            ),

            index_size=file_size(
                package.index_file
            ),

            index_sha256=calculate_sha256(
                package.index_file
            ),

            mapping_file=str(
                package.mapping_file.relative_to(
                    package.storage_dir
                )
            ),

            mapping_size=file_size(
                package.mapping_file
            ),

            mapping_sha256=calculate_sha256(
                package.mapping_file
            ),
        )

        settings.STORAGE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            settings.MANIFEST_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                asdict(manifest),
                file,
                indent=4
            )

        logger.info(
            "Manifest saved to %s",
            settings.MANIFEST_FILE
        )

        return settings.MANIFEST_FILE