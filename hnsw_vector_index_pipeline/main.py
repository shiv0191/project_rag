from config.settings import (
    EMBEDDING_DIMENSION,
    DISTANCE_METRIC,
    M,
    EF_CONSTRUCTION,
    EF_SEARCH,
    INPUT_DIR,
    EMBEDDINGS_FILE,
    OUTPUT_DIR,
    INDEX_FILE,
    ID_MAPPING_FILE,
)

from data.embedding_loader import EmbeddingLoader
from index.builder import HNSWBuilder
from index.index_manager import IndexManager


def main():

    print("=" * 60)
    print("Loading embeddings...")
    print("=" * 60)


    INPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not EMBEDDINGS_FILE.exists():
        raise FileNotFoundError(
            f"Embeddings file not found:\n{EMBEDDINGS_FILE}"
        )

    vectors, ids, payloads = EmbeddingLoader.load_embeddings(
        EMBEDDINGS_FILE
    )

    if len(vectors) == 0:
        raise ValueError("No embeddings found in the input file.")
    
    print(f"Loaded {len(vectors)} embeddings")

    actual_dimension = vectors.shape[1]

    print(f"Embedding dimension : {actual_dimension}")

    if actual_dimension != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected embedding dimension "
            f"{EMBEDDING_DIMENSION}, "
            f"got {actual_dimension}"
        )


    print("\nBuilding HNSW index...")

    builder = HNSWBuilder(
        dimension=actual_dimension,
        metric=DISTANCE_METRIC,
        m=M,
        ef_construction=EF_CONSTRUCTION,
        ef_search=EF_SEARCH,
    )

    index = builder.build(
        vectors,
        ids,
    )

    print("Saving index...")

    IndexManager.save(
        index,
        INDEX_FILE,
    )

    IndexManager.save_mapping(
        payloads,
        ID_MAPPING_FILE,
    )

    print("\nDone!")

    print(f"Index saved to : {INDEX_FILE}")
    print(f"Mapping saved to : {ID_MAPPING_FILE}")


if __name__ == "__main__":
    main()