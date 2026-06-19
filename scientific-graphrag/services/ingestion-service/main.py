"""
Ingestion Service - Phase 2

Handles document ingestion and chunking
Supports PDF, CSV, and TXT formats
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from abc import ABC, abstractmethod
import hashlib
import uuid

from shared.utils.logger import setup_logging
from shared.schemas.models import DocumentChunk, DocumentProcessingResult, DocumentType

logger = setup_logging(__name__)


class DocumentParser(ABC):
    """Abstract base class for document parsers"""
    
    @abstractmethod
    def parse(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse document content"""
        pass


class PDFParser(DocumentParser):
    """Parser for PDF documents"""
    
    def parse(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse PDF document"""
        try:
            import pymupdf
            
            pdf_document = pymupdf.open(stream=content, filetype="pdf")
            text_content = ""
            metadata = {
                "pages": len(pdf_document),
                "title": pdf_document.metadata.get("title", filename),
                "author": pdf_document.metadata.get("author", "Unknown")
            }
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text_content += page.get_text() + "\n"
            
            pdf_document.close()
            
            return {
                "content": text_content,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise


class CSVParser(DocumentParser):
    """Parser for CSV documents"""
    
    def parse(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse CSV document"""
        try:
            import csv
            import io
            
            text_content = ""
            content_str = content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(content_str))
            
            for row in reader:
                text_content += str(row) + "\n"
            
            return {
                "content": text_content,
                "metadata": {"format": "csv"}
            }
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")
            raise


class TXTParser(DocumentParser):
    """Parser for TXT documents"""
    
    def parse(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse TXT document"""
        try:
            text_content = content.decode('utf-8')
            return {
                "content": text_content,
                "metadata": {"format": "txt"}
            }
        except Exception as e:
            logger.error(f"Error parsing TXT: {str(e)}")
            raise


class DocumentChunker:
    """Handles document chunking with overlaps"""
    
    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 50
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, doc_id: str) -> List[DocumentChunk]:
        """Chunk text into overlapping chunks"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if chunk_text.strip():
                chunk_id = str(uuid.uuid4())
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    content=chunk_text,
                    metadata={
                        "chunk_index": len(chunks),
                        "word_count": len(chunk_words)
                    }
                )
                chunks.append(chunk)
        
        return chunks


class IngestionService:
    """Main ingestion service"""
    
    def __init__(self):
        self.parsers = {
            DocumentType.PDF: PDFParser(),
            DocumentType.CSV: CSVParser(),
            DocumentType.TXT: TXTParser()
        }
        self.chunker = DocumentChunker(chunk_size=512, overlap=50)
    
    def process_document(
        self,
        content: bytes,
        filename: str,
        document_type: DocumentType
    ) -> DocumentProcessingResult:
        """Process a document"""
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        logger.info(f"Processing document: {filename} (ID: {doc_id})")
        
        # Parse document
        if document_type not in self.parsers:
            raise ValueError(f"Unsupported document type: {document_type}")
        
        parser = self.parsers[document_type]
        parsed = parser.parse(content, filename)
        
        # Chunk document
        chunks = self.chunker.chunk_text(parsed["content"], doc_id)
        
        logger.info(f"Document chunked into {len(chunks)} chunks")
        
        # Create result
        result = DocumentProcessingResult(
            doc_id=doc_id,
            filename=filename,
            chunks=chunks,
            entity_count=0,  # Will be updated in entity extraction
            processed_at=datetime.now()
        )
        
        return result
    
    def process_batch(
        self,
        documents: List[tuple]  # List of (content, filename, type)
    ) -> List[DocumentProcessingResult]:
        """Process multiple documents"""
        results = []
        for content, filename, doc_type in documents:
            try:
                result = self.process_document(content, filename, doc_type)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
        
        return results


# Service initialization
ingestion_service = IngestionService()


# FastAPI app for ingestion service
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

app = FastAPI(title="Ingestion Service", version="1.0.0")


@app.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...)
):
    """Ingest a document"""
    try:
        content = await file.read()
        
        # Determine document type from filename
        if file.filename.endswith('.pdf'):
            doc_type = DocumentType.PDF
        elif file.filename.endswith('.csv'):
            doc_type = DocumentType.CSV
        else:
            doc_type = DocumentType.TXT
        
        result = ingestion_service.process_document(content, file.filename, doc_type)
        
        return {
            "status": "success",
            "document_id": result.doc_id,
            "filename": result.filename,
            "chunk_count": len(result.chunks)
        }
    
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "ingestion-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
