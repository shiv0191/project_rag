"""
FastAPI Gateway Service - Phase 1

Main entry point for the Scientific GraphRAG Platform
Handles authentication, rate limiting, and request routing
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from contextlib import asynccontextmanager
import logging
from typing import Optional

from shared.config.settings import settings
from shared.schemas.models import (
    DocumentUploadRequest, QueryRequest, QueryResponse, DocumentProcessingResult
)
from shared.utils.logger import setup_logging

# Setup logging
logger = setup_logging(__name__)
security = HTTPBearer()


# Lifespan context for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting GraphRAG API Gateway")
    yield
    logger.info("Shutting down GraphRAG API Gateway")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Scientific GraphRAG Decision Support Platform",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting decorator (simplified)
class RateLimiter:
    """Simple rate limiter"""
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    async def check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limit"""
        import time
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests outside window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < self.window_seconds
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        self.requests[client_id].append(current_time)
        return True


rate_limiter = RateLimiter()


# Authentication
async def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """Verify authentication token"""
    token = credentials.credentials
    # Placeholder authentication for demo purposes only
    # In production, validate against a real token store
    if settings.DEBUG and token == "demo-token":
        return token
    raise HTTPException(status_code=401, detail="Invalid token")


# Health Check Endpoint (Phase 1)
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": settings.API_VERSION
    }


# Ready Check Endpoint
@app.get("/ready")
async def readiness_check():
    """Check if service is ready"""
    # In production, check all dependencies
    return {
        "status": "ready",
        "service": "api-gateway"
    }


# Upload Endpoint (Phase 1)
@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    credentials: HTTPAuthCredentials = Depends(security)
):
    """Upload a document for ingestion"""
    try:
        # Verify token
        await verify_token(credentials)
        
        # Check rate limit
        client_id = credentials.credentials
        if not await rate_limiter.check_rate_limit(client_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Read file
        contents = await file.read()
        
        logger.info(f"Document uploaded: {file.filename} ({len(contents)} bytes)")
        
        return {
            "status": "success",
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "size": len(contents),
            "document_id": f"doc_{file.filename.replace('.', '_')}"
        }
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Query Endpoint (Phase 1)
@app.post("/query")
async def query_platform(
    request: QueryRequest,
    credentials: HTTPAuthCredentials = Depends(security)
):
    """Submit a query to the platform"""
    try:
        # Verify token
        await verify_token(credentials)
        
        # Check rate limit
        client_id = credentials.credentials
        if not await rate_limiter.check_rate_limit(client_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        logger.info(f"Query received: {request.query[:100]}...")
        
        # In Phase 1, return mock response
        # This will be connected to actual services in later phases
        
        return {
            "status": "success",
            "message": "Query processed successfully",
            "query": request.query,
            "query_type": request.query_type,
            "processing_status": "In development - Phase 1"
        }
    
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Status Endpoint
@app.get("/status")
async def get_status():
    """Get platform status"""
    return {
        "api_service": "operational",
        "ingestion_service": "initializing",
        "graph_service": "initializing",
        "retrieval_service": "initializing",
        "agent_service": "initializing",
        "evaluation_service": "initializing",
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
        ))
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
