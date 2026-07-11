from sentence_transformers import SentenceTransformer

from src.config import (
    EMBEDDING_MODEL,
    DEVICE,
    BATCH_SIZE,
)


class Embedder:

    def __init__(self):

        print(f"\nLoading model: {EMBEDDING_MODEL}")

        self.model = SentenceTransformer(
            EMBEDDING_MODEL,
            device=DEVICE,
        )

        print("Model loaded successfully.\n")

    def embed_chunks(self, chunks):

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self.model.encode(
            texts,
            batch_size=BATCH_SIZE,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        return embeddings
