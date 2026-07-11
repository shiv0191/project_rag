import json
import os


class EmbeddingWriter:

    def __init__(self, output_file):

        self.output_file = output_file

        if os.path.exists(output_file):
            os.remove(output_file)

    def append(
        self,
        chunks,
        embeddings,
    ):

        with open(
            self.output_file,
            "a",
            encoding="utf-8",
        ) as f:

            for chunk, embedding in zip(
                chunks,
                embeddings,
            ):

                record = {
                    "chunk_id": chunk["chunk_id"],
                    "page": chunk["page"],
                    "text": chunk["text"],
                    "embedding_dimension": len(
                        embedding
                    ),
                    "embedding": embedding.tolist(),
                    "metadata": chunk["metadata"],
                }

                f.write(
                    json.dumps(record)
                    + "\n"
                )
