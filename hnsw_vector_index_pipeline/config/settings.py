from pathlib import Path

# ==========================================================
# HNSW Configuration
# ==========================================================

# Expected embedding dimension
EMBEDDING_DIMENSION = 768

# Distance metric
DISTANCE_METRIC = "cosine"

# HNSW Parameters
M = 16
EF_CONSTRUCTION = 200
EF_SEARCH = 50

# ==========================================================
# Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

EMBEDDINGS_FILE = INPUT_DIR / "embeddings.jsonl"


INDEX_FILE = OUTPUT_DIR / "hnsw_index.bin"
ID_MAPPING_FILE = OUTPUT_DIR / "id_mapping.json"