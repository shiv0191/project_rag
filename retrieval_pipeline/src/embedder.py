from sentence_transformers import SentenceTransformer
import numpy as np

from src.config import EMBEDDING_MODEL


class Embedder:
    def __init__(self):
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate an embedding for a user query.

        Args:
            query: User's search query.

        Returns:
            NumPy array of shape (embedding_dimension,)
        """
        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embedding
    