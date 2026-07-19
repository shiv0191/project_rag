from sentence_transformers import CrossEncoder

print("Downloading BAAI/bge-reranker-base...")

model = CrossEncoder(
    "BAAI/bge-reranker-base"
)

print("Download complete!")
