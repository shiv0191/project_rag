from sentence_transformers import CrossEncoder

from src.config import (
    RERANKER_MODEL,
    DEVICE,
    TOP_N,
    BATCH_SIZE
)

from src.models import (
    RetrievedQuery,
    RetrievedChunk,
    RerankedChunk,
    RerankedQuery
)


class Reranker:
    """
    Cross-Encoder based reranker.
    """

    def __init__(self):
        self.model = CrossEncoder(
            model_name=RERANKER_MODEL,
            device=DEVICE
        )

    def rerank(
        self,
        retrieved_query: RetrievedQuery
    ) -> RerankedQuery:
        """
        Rerank the retrieved chunks for one query.
        """

        # ---------------------------------------------
        # Build (query, document) pairs
        # ---------------------------------------------

        sentence_pairs = [
            (retrieved_query.query, chunk.text)
            for chunk in retrieved_query.results
        ]

        # ---------------------------------------------
        # Predict relevance scores
        # ---------------------------------------------

        scores = self.model.predict(
            sentence_pairs,
            batch_size=BATCH_SIZE,
            show_progress_bar=False
        )

        # ---------------------------------------------
        # Attach scores
        # ---------------------------------------------

        reranked_chunks = []

        for chunk, score in zip(retrieved_query.results, scores):

            reranked_chunks.append(
                RerankedChunk(
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    retriever_score=chunk.retriever_score,
                    reranker_score=float(score),
                    metadata=chunk.metadata
                )
            )

        # ---------------------------------------------
        # Sort by reranker score
        # ---------------------------------------------

        reranked_chunks.sort(
            key=lambda x: x.reranker_score,
            reverse=True
        )

        # ---------------------------------------------
        # Keep Top N
        # ---------------------------------------------

        reranked_chunks = reranked_chunks[:TOP_N]

        return RerankedQuery(
            query=retrieved_query.query,
            results=reranked_chunks
        )