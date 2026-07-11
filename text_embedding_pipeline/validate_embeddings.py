from src.validator import EmbeddingValidator


def main():

    validator = EmbeddingValidator(
        "output/sample_embeddings.jsonl"
    )

    embeddings = validator.load_embeddings()

    validator.summary(
        embeddings
    )

    validator.validate_dimensions(
        embeddings
    )

    validator.validate_nan_inf(
        embeddings
    )

    validator.validate_norm(
        embeddings
    )

    validator.cosine_similarity(
        embeddings
    )


if __name__ == "__main__":
    main()

