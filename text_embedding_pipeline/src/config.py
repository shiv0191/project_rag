from dotenv import load_dotenv
import os

load_dotenv()

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "models/bge-base-en-v1.5",
)

DEVICE = os.getenv(
    "DEVICE",
    "cpu",
)

BATCH_SIZE = int(
    os.getenv(
        "BATCH_SIZE",
        32,
    )
)
