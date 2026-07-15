import hnswlib
import numpy as np


class HNSWBuilder:

    def __init__(
        self,
        dimension: int,
        metric: str,
        m: int,
        ef_construction: int,
        ef_search: int,
    ):
        self.dimension = dimension
        self.metric = metric
        self.m = m
        self.ef_construction = ef_construction
        self.ef_search = ef_search

    def build(
        self,
        vectors: np.ndarray,
        ids: list[int],
    ):

        if len(vectors) == 0:
            raise ValueError("No vectors found.")

        if len(vectors) != len(ids):
            raise ValueError(
                "Number of vectors and ids do not match."
            )

        index = hnswlib.Index(
            space=self.metric,
            dim=self.dimension,
        )

        index.init_index(
            max_elements=len(ids),
            ef_construction=self.ef_construction,
            M=self.m,
        )

        index.add_items(vectors, ids)

        index.set_ef(self.ef_search)

        return index