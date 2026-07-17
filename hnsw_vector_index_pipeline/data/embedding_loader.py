import json
from pathlib import Path

import numpy as np


class EmbeddingLoader:

    @staticmethod
    def load_embeddings(file_path: Path):
        """
        Load embeddings from JSONL file.

        Returns
        -------
        vectors : np.ndarray
        ids : list[int]
        chunk_ids : list[str]
        payloads : dict[str, dict]
        """

        vectors = []
        ids = []
        chunk_ids = []
        payloads = {}

        with open(file_path, "r", encoding="utf-8") as file:

            for idx, line in enumerate(file):

                record = json.loads(line)

                vectors.append(record["embedding"])

                # Integer labels for HNSW
                ids.append(idx)

                # Actual document chunk IDs
                chunk_ids.append(record["chunk_id"])

                # Payloads keyed by chunk_id
                payloads[record["chunk_id"]] = {
                    "chunk_id": record["chunk_id"],
                    "text": record["text"],
                    "page": record["page"],
                    "metadata": record["metadata"],
                }

        vectors = np.asarray(vectors, dtype=np.float32)

        return vectors, ids, chunk_ids, payloads
