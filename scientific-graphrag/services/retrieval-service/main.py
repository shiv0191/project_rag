"""
Retrieval Service - Phase 3 & 4

Handles embeddings and vector database integration
Uses BAAI/bge-large-en-v1.5 for embeddings
Uses Qdrant for vector storage and retrieval
"""

from typing import List, Dict, Any, Optional
import numpy as np
import logging
from datetime import datetime

from shared.utils.logger import setup_logging
from shared.schemas.models import RetrievedDocument
from shared.config.settings import settings

logger = setup_logging(__name__)


class EmbeddingService:
    """Phase 3: Embedding Service using BAAI/bge-large-en-v1.5"""
    
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5"):
        """Initialize embedding service"""
        self.model_name = model_name
        self.embedding_model = None
        self.init_model()
    
    def init_model(self):
        """Initialize embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """Embed multiple documents"""
        try:
            embeddings = self.embedding_model.encode(
                documents,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            logger.info(f"Embedded {len(documents)} documents")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}")
            raise
    
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query"""
        try:
            embedding = self.embedding_model.encode(
                query,
                convert_to_numpy=True
            )
            logger.info(f"Query embedded: {query[:50]}...")
            return embedding
        except Exception as e:
            logger.error(f"Error embedding query: {str(e)}")
            raise


class QdrantVectorDB:
    """Phase 4: Qdrant Vector Database Integration"""
    
    def __init__(self, url: str = settings.QDRANT_URL, vector_size: int = 1024):
        """Initialize Qdrant client"""
        self.url = url
        self.vector_size = vector_size
        self.client = None
        self.init_client()
    
    def init_client(self):
        """Initialize Qdrant client"""
        try:
            from qdrant_client import QdrantClient
            logger.info(f"Connecting to Qdrant at {self.url}")
            self.client = QdrantClient(url=self.url, timeout=settings.QDRANT_TIMEOUT)
            logger.info("Qdrant client initialized")
        except Exception as e:
            logger.error(f"Error initializing Qdrant client: {str(e)}")
            raise
    
    def create_collection(self, collection_name: str):
        """Create a collection in Qdrant"""
        try:
            from qdrant_client.models import Distance, VectorParams
            
            logger.info(f"Creating collection: {collection_name}")
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )
            
            logger.info(f"Collection created: {collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise
    
    def upsert_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]],
        embeddings: np.ndarray
    ):
        """Upsert documents with embeddings"""
        try:
            from qdrant_client.models import PointStruct
            
            points = []
            for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
                point = PointStruct(
                    id=idx,
                    vector=embedding.tolist(),
                    payload=doc
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"Upserted {len(documents)} documents to {collection_name}")
        except Exception as e:
            logger.error(f"Error upserting documents: {str(e)}")
            raise
    
    def search(
        self,
        collection_name: str,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[RetrievedDocument]:
        """Search in Qdrant collection"""
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding.tolist(),
                limit=top_k
            )
            
            retrieved = []
            for result in results:
                doc = RetrievedDocument(
                    doc_id=result.payload.get("doc_id", "unknown"),
                    chunk_id=result.payload.get("chunk_id", "unknown"),
                    content=result.payload.get("content", ""),
                    score=result.score,
                    metadata=result.payload.get("metadata", {}),
                    source="vector"
                )
                retrieved.append(doc)
            
            logger.info(f"Retrieved {len(retrieved)} documents from {collection_name}")
            return retrieved
        except Exception as e:
            logger.error(f"Error searching Qdrant: {str(e)}")
            raise


class RetrievalService:
    """Combined Retrieval Service"""
    
    def __init__(self):
        """Initialize retrieval service"""
        self.embedding_service = EmbeddingService()
        self.vector_db = QdrantVectorDB()
        
        # Create default collections
        self.collections = [
            "scientific_papers",
            "scientific_guidelines",
            "reference_documents",
            "ontology_documents"
        ]
        
        self._init_collections()
    
    def _init_collections(self):
        """Initialize collections"""
        for collection in self.collections:
            try:
                self.vector_db.create_collection(collection)
            except Exception as e:
                if "already exists" in str(e):
                    logger.info(f"Collection {collection} already exists")
                else:
                    logger.error(f"Error creating collection {collection}: {str(e)}")
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]]
    ):
        """Add documents to vector database"""
        try:
            # Extract content
            contents = [doc.get("content", "") for doc in documents]
            
            # Generate embeddings
            embeddings = self.embedding_service.embed_documents(contents)
            
            # Upsert to Qdrant
            self.vector_db.upsert_documents(collection_name, documents, embeddings)
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def search(
        self,
        query: str,
        collection_name: str = "scientific_papers",
        top_k: int = 5
    ) -> List[RetrievedDocument]:
        """Search for documents"""
        try:
            # Embed query
            query_embedding = self.embedding_service.embed_query(query)
            
            # Search Qdrant
            results = self.vector_db.search(collection_name, query_embedding, top_k)
            
            return results
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            raise


# FastAPI app for retrieval service
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="Retrieval Service", version="1.0.0")
retrieval_service = RetrievalService()


@app.post("/search")
async def search_documents(
    query: str,
    collection: str = "scientific_papers",
    top_k: int = 5
):
    """Search for documents"""
    try:
        results = retrieval_service.search(query, collection, top_k)
        
        return {
            "status": "success",
            "query": query,
            "collection": collection,
            "results": [
                {
                    "doc_id": r.doc_id,
                    "content": r.content[:200],
                    "score": r.score,
                    "source": r.source
                }
                for r in results
            ]
        }
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post("/add-documents")
async def add_documents(
    collection: str = "scientific_papers",
    documents: List[Dict[str, Any]] = None
):
    """Add documents to collection"""
    try:
        if not documents:
            documents = []
        
        retrieval_service.add_documents(collection, documents)
        
        return {
            "status": "success",
            "collection": collection,
            "documents_added": len(documents)
        }
    except Exception as e:
        logger.error(f"Add documents error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get("/collections")
async def get_collections():
    """Get available collections"""
    return {
        "collections": retrieval_service.collections
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "retrieval-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
