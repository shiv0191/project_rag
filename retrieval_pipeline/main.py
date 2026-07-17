from src.pipeline import RetrievalPipeline


def print_results(results):
    print("\n" + "=" * 80)
    print(f"Retrieved {len(results)} result(s)")
    print("=" * 80)

    for result in results:
        print(f"\nRank      : {result.rank}")
        print(f"Score     : {result.score:.4f}")
        print(f"Chunk ID  : {result.chunk_id}")
        print(f"Page      : {result.page}")
        print(f"Source    : {result.source}")
        print(f"Text      :")
        print(result.text[:300])

        if len(result.text) > 300:
            print("...")

        print("-" * 80)


def main():
    print("Initializing Retrieval Pipeline...\n")

    pipeline = RetrievalPipeline()

    print("\nRetrieval Pipeline Ready!")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Enter query: ").strip()

        if query.lower() in {"exit", "quit"}:
            print("Exiting...")
            break

        if not query:
            print("Please enter a valid query.\n")
            continue

        results = pipeline.search(query)

        print_results(results)


if __name__ == "__main__":
    main()
