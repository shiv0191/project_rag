import json
import numpy as np


class EmbeddingValidator:

    def __init__(self, embedding_file):
        self.embedding_file = embedding_file

    def load_embeddings(self):

        embeddings = []

        with open(
            self.embedding_file,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:
                embeddings.append(json.loads(line))

        return embeddings

    def validate_dimensions(
        self,
        embeddings,
    ):

        print("\nChecking embedding dimensions...")

        dimensions = {
            record["embedding_dimension"]
            for record in embeddings
        }

        print(f"Dimensions found : {dimensions}")

        if len(dimensions) == 1:
            print("PASS")
        else:
            print("FAIL")

    def validate_nan_inf(
        self,
        embeddings,
    ):

        print("\nChecking NaN / Infinity...")

        passed = True

        for record in embeddings:

            vector = np.array(record["embedding"])

            if np.isnan(vector).any():
                print(f"NaN found in {record['chunk_id']}")
                passed = False

            if np.isinf(vector).any():
                print(f"Infinity found in {record['chunk_id']}")
                passed = False

        if passed:
            print("PASS")

    def validate_norm(
        self,
        embeddings,
    ):

        print("\nChecking vector normalization...")

        for record in embeddings:

            vector = np.array(record["embedding"])

            norm = np.linalg.norm(vector)

            print(
                f"{record['chunk_id']} "
                f"Norm = {norm:.6f}"
            )

    def cosine_similarity(
        self,
        embeddings,
    ):

        print("\nCosine Similarity Matrix\n")

        vectors = [
            np.array(record["embedding"])
            for record in embeddings
        ]

        for i in range(len(vectors)):

            row = []

            for j in range(len(vectors)):

                similarity = np.dot(
                    vectors[i],
                    vectors[j],
                )

                row.append(
                    f"{similarity:.3f}"
                )

            print("  ".join(row))

    def summary(
        self,
        embeddings,
    ):

        print("\nSummary")
        print("-" * 40)

        print(
            f"Total embeddings : {len(embeddings)}"
        )

        print(
            f"Dimension        : {embeddings[0]['embedding_dimension']}"
        )

        print("-" * 40)
