import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "models/bge-base-en-v1.5"
)

TOP_K = int(os.getenv("TOP_K", 5))

EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 768))

DISTANCE_METRIC = os.getenv("DISTANCE_METRIC", "cosine")

EF_SEARCH = int(os.getenv("EF_SEARCH", 100))

INDEX_FILE = os.getenv(
    "INDEX_FILE",
    "input/hnsw_index.bin"
)

ID_MAPPING_FILE = os.getenv(
    "ID_MAPPING_FILE",
    "input/id_mapping.json"
)

EMBEDDINGS_FILE = os.getenv(
    "EMBEDDINGS_FILE",
    "input/embeddings.jsonl"
)
