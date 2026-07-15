from qdrant_client import QdrantClient

client = QdrantClient(path="./qdrant_data")

try:
    collections = client.get_collections()

    print("\nCollections")
    print(collections)

    points, _ = client.scroll(
        collection_name="manual_chunks",
        limit=3,
        with_vectors=False,
        with_payload=True,
    )

    print("\nStored Points\n")

    for point in points:

        print("=" * 80)
        print(f"ID       : {point.id}")
        print(f"Chunk ID : {point.payload['chunk_id']}")
        print(f"Page     : {point.payload['page']}")
        print(f"Text     : {point.payload['text'][:150]}...")

finally:
    client.close()