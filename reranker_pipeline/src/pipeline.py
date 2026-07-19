from tqdm import tqdm

from src.config import (
    INPUT_FILE,
    OUTPUT_FILE
)

from src.reader import Reader
from src.reranker import Reranker
from src.writer import Writer


class RerankerPipeline:
    """
    End-to-end reranking pipeline.
    """

    def __init__(self):
        self.reranker = Reranker()

    def run(self):
        """
        Execute the reranking pipeline.
        """

        print("=" * 60)
        print("Reading retrieval results...")
        print("=" * 60)

        retrieved_queries = Reader.read(INPUT_FILE)

        print(f"Loaded {len(retrieved_queries)} queries.\n")

        reranked_queries = []

        print("=" * 60)
        print("Reranking...")
        print("=" * 60)

        for query in tqdm(retrieved_queries):

            reranked_query = self.reranker.rerank(query)

            reranked_queries.append(reranked_query)

        print("\nSaving results...")

        Writer.write(
            OUTPUT_FILE,
            reranked_queries
        )

        print("\nPipeline completed successfully.")
        print(f"Output saved to: {OUTPUT_FILE}")
