import json

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import hnswlib

from config.settings import (
    EMBEDDING_DIMENSION,
    DISTANCE_METRIC,
    INDEX_FILE,
    ID_MAPPING_FILE,
)


def validate():

    print("=" * 60)
    print("HNSW INDEX VALIDATION")
    print("=" * 60)

    # --------------------------------------------------
    # Check files
    # --------------------------------------------------

    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            f"Index file not found:\n{INDEX_FILE}"
        )

    print(f"[PASS] Index file exists")

    if not ID_MAPPING_FILE.exists():
        raise FileNotFoundError(
            f"Mapping file not found:\n{ID_MAPPING_FILE}"
        )

    print(f"[PASS] Mapping file exists")

    # --------------------------------------------------
    # Load mapping
    # --------------------------------------------------

    with open(ID_MAPPING_FILE, "r", encoding="utf-8") as file:
        mapping = json.load(file)

    print(f"[PASS] Mapping loaded")

    # --------------------------------------------------
    # Load index
    # --------------------------------------------------

    index = hnswlib.Index(
        space=DISTANCE_METRIC,
        dim=EMBEDDING_DIMENSION,
    )

    index.load_index(str(INDEX_FILE))

    print(f"[PASS] Index loaded")

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    current_count = index.get_current_count()
    max_elements = index.get_max_elements()

    print()
    print("Index Statistics")
    print("-" * 60)

    print(f"Vectors indexed      : {current_count}")
    print(f"Maximum capacity     : {max_elements}")
    print(f"Embedding dimension  : {EMBEDDING_DIMENSION}")
    print(f"Distance metric      : {DISTANCE_METRIC}")
    print(f"Mapping entries      : {len(mapping)}")

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    print()
    print("Validation")
    print("-" * 60)

    if current_count != len(mapping):
        print("[FAIL] Mapping count does not match indexed vectors")
    else:
        print("[PASS] Mapping count matches indexed vectors")

    print()

    if current_count == len(mapping):
        print("Overall Status : SUCCESS")
    else:
        print("Overall Status : FAILED")

    print("=" * 60)


if __name__ == "__main__":
    validate()
