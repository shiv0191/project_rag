import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# ==========================================================
# Model Configuration
# ==========================================================
RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL",
    "models/bge-reranker-base"
)


# ==========================================================
# Device Configuration
# ==========================================================
DEVICE = os.getenv("DEVICE", "cpu")


# ==========================================================
# Inference Configuration
# ==========================================================
TOP_N = int(os.getenv("TOP_N", 5))

BATCH_SIZE = int(os.getenv("BATCH_SIZE", 16))


# ==========================================================
# File Paths
# ==========================================================
INPUT_FILE = os.getenv(
    "INPUT_FILE",
    "input/retrieved_results.json"
)

OUTPUT_FILE = os.getenv(
    "OUTPUT_FILE",
    "output/reranked_results.json"
)

LOG_DIR = os.getenv(
    "LOG_DIR",
    "logs"
)