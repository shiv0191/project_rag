from qdrant_client import QdrantClient

client = QdrantClient(path="./qdrant_data")

try:
    print("Connected successfully!")
    print(client.get_collections())
finally:
    client.close()