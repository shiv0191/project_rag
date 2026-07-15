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
        payloads : dict[int, dict]
        """

        vectors = []
        ids = []
        payloads = {}

        with open(file_path, "r", encoding="utf-8") as file:

            for idx, line in enumerate(file):

                record = json.loads(line)

                vectors.append(record["embedding"])

                ids.append(idx)

                payloads[idx] = {
                    "chunk_id": record["chunk_id"],
                    "text": record["text"],
                    "page": record["page"],
                    "metadata": record["metadata"],
                }

        vectors = np.asarray(vectors, dtype=np.float32)

        return vectors, ids, payloads