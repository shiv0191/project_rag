import hnswlib
import numpy as np

from config.settings import (
    EMBEDDING_DIMENSION,
    DISTANCE_METRIC,
    EMBEDDINGS_FILE,
    INDEX_FILE,
)

from data.embedding_loader import EmbeddingLoader


def validate_search():

    print("=" * 60)
    print("HNSW SEARCH VALIDATION")
    print("=" * 60)

    # ---------------------------------------------
    # Load original embeddings
    # ---------------------------------------------
    vectors, ids, payloads = EmbeddingLoader.load_embeddings(
        EMBEDDINGS_FILE
    )

    print(f"Loaded {len(vectors)} embeddings")

    # ---------------------------------------------
    # Load index
    # ---------------------------------------------
    index = hnswlib.Index(
        space=DISTANCE_METRIC,
        dim=EMBEDDING_DIMENSION,
    )

    index.load_index(str(INDEX_FILE))

    print("Index loaded successfully.\n")

    # ---------------------------------------------
    # Select one vector as query
    # ---------------------------------------------
    query_id = 10

    query_vector = vectors[query_id]

    # HNSW expects shape (1, dimension)
    query_vector = np.expand_dims(query_vector, axis=0)

    # ---------------------------------------------
    # Search
    # ---------------------------------------------
    labels, distances = index.knn_query(
        query_vector,
        k=5,
    )

    print(f"Query Vector ID : {query_id}")
    print()

    print("Top-5 Results")
    print("-" * 60)

    print(
        f"{'Rank':<6}"
        f"{'ID':<8}"
        f"{'Distance'}"
    )

    print("-" * 60)

    for rank, (label, distance) in enumerate(
        zip(labels[0], distances[0]),
        start=1,
    ):
        print(
            f"{rank:<6}"
            f"{label:<8}"
            f"{distance:.6f}"
        )

    print()

    # ---------------------------------------------
    # Validation
    # ---------------------------------------------
    if labels[0][0] == query_id:
        print("[PASS] Query vector retrieved itself.")
    else:
        print("[FAIL] Query vector did not retrieve itself.")

    print("=" * 60)


if __name__ == "__main__":
    validate_search()