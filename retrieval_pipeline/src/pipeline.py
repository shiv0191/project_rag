from src.config import (
    TOP_K,
    ID_MAPPING_FILE,
)
from src.embedder import Embedder
from src.index_loader import IndexLoader
from src.payload_loader import PayloadLoader
from src.retriever import Retriever


class RetrievalPipeline:
    def __init__(self):
        # Load embedding model
        self.embedder = Embedder()

        # Load HNSW index
        self.index = IndexLoader().load()

        # Load payloads
        self.payload_loader = PayloadLoader()
        self.payload_loader.load()

        # Initialize retriever
        self.retriever = Retriever(
            index=self.index,
            id_mapping_file=ID_MAPPING_FILE,
            payload_loader=self.payload_loader,
        )

    def search(self, query: str, top_k: int = TOP_K):
        """
        Retrieve the top-k most relevant chunks.

        Args:
            query: User query
            top_k: Number of results

        Returns:
            List[RetrievalResult]
        """

        query_vector = self.embedder.embed_query(query)

        return self.retriever.search(
            query_vector=query_vector,
            top_k=top_k,
        )
