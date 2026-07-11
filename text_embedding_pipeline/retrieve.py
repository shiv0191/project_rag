from src.retriever import Retriever


def main():

    print("=" * 80)
    print("Initializing Retriever...")
    print("=" * 80)

    retriever = Retriever(
        "output/sample_embeddings.jsonl"
    )

    print("\nRetriever is ready.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:

        query = input("Enter your question: ").strip()

        if query.lower() in ("exit", "quit"):
            print("\nExiting Retriever...")
            break

        if not query:
            print("Please enter a valid question.\n")
            continue

        results = retriever.search(
            query,
            top_k=5,
        )

        print("\nTop Matches\n")

        for rank, (score, record) in enumerate(
            results,
            start=1,
        ):

            print("=" * 80)
            print(f"Rank      : {rank}")
            print(f"Score     : {score:.4f}")
            print(f"Chunk ID  : {record['chunk_id']}")
            print(f"Page      : {record['page']}")

            print("\nText\n")
            print(record["text"][:500])
            print()

        print("-" * 80)


if __name__ == "__main__":
    main()
