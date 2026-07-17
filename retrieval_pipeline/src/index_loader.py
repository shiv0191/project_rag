import hnswlib

from src.config import (
    EMBEDDING_DIMENSION,
    DISTANCE_METRIC,
    EF_SEARCH,
    INDEX_FILE,
)


class IndexLoader:
    def __init__(self):
        self.index = None

    def load(self):
        """
        Load the HNSW index from disk.
        """
        index = hnswlib.Index(
            space=DISTANCE_METRIC,
            dim=EMBEDDING_DIMENSION,
        )

        index.load_index(INDEX_FILE)

        # Runtime search parameter
        index.set_ef(EF_SEARCH)

        self.index = index

        print(f"Loaded HNSW index: {INDEX_FILE}")
        print(f"Dimension: {EMBEDDING_DIMENSION}")
        print(f"Metric: {DISTANCE_METRIC}")
        print(f"ef_search: {EF_SEARCH}")

        return self.index
    