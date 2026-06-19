"""
Shared data models and schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Types of documents"""
    PDF = "pdf"
    CSV = "csv"
    TXT = "txt"
    JSON = "json"


class EntityType(str, Enum):
    """Types of entities"""
    CONCEPT = "concept"
    CHEMICAL = "chemical"
    DISEASE = "disease"
    EXPERIMENT = "experiment"
    REFERENCE_RANGE = "reference_range"
    AUTHOR = "author"
    PROPERTY = "property"


class QueryType(str, Enum):
    """Types of queries"""
    REFERENCE_RANGE = "reference_range"
    SCIENTIFIC_CONTEXT = "scientific_context"
    ANALYTICAL_DECISION = "analytical_decision"


# Request/Response Models

class DocumentUploadRequest(BaseModel):
    """Request to upload a document"""
    filename: str
    document_type: DocumentType
    metadata: Optional[Dict[str, Any]] = None


class DocumentChunk(BaseModel):
    """A chunk of a document"""
    chunk_id: str
    doc_id: str
    content: str
    metadata: Dict[str, Any]


class DocumentProcessingResult(BaseModel):
    """Result of document processing"""
    doc_id: str
    filename: str
    chunks: List[DocumentChunk]
    entity_count: int
    processed_at: datetime


class Entity(BaseModel):
    """An entity in the knowledge graph"""
    entity_id: str
    name: str
    entity_type: EntityType
    properties: Dict[str, Any]
    document_ids: List[str]


class Relationship(BaseModel):
    """A relationship between entities"""
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    properties: Dict[str, Any]
    confidence: float


class RetrievedDocument(BaseModel):
    """A retrieved document from vector/graph search"""
    doc_id: str
    chunk_id: Optional[str] = None
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str  # "vector" or "graph" or "bm25"


class QueryRequest(BaseModel):
    """Request for a query"""
    query: str
    query_type: QueryType = QueryType.SCIENTIFIC_CONTEXT
    top_k: int = 5
    metadata: Optional[Dict[str, Any]] = None


class Evidence(BaseModel):
    """Evidence for a finding"""
    source_document: RetrievedDocument
    relevance_score: float
    reasoning: str


class Finding(BaseModel):
    """A finding from the system"""
    finding_statement: str
    confidence: float
    evidence: List[Evidence]


class QueryResponse(BaseModel):
    """Response to a query"""
    query: str
    query_type: QueryType
    findings: List[Finding]
    reasoning_chain: str
    sources: List[RetrievedDocument]
    graph_entities: List[Entity]
    graph_relationships: List[Relationship]
    execution_time_ms: float


class ReferenceRange(BaseModel):
    """Reference range for a property"""
    property_name: str
    unit: str
    min_value: float
    max_value: float
    status: str  # "normal", "low", "high"


class ReferenceRangeCheckResult(BaseModel):
    """Result of checking a value against reference ranges"""
    property_name: str
    value: float
    unit: str
    reference_range: ReferenceRange
    status: str  # "normal", "low", "high"


class AnalyticalQuery(BaseModel):
    """Analytical query with multiple values"""
    measurements: Dict[str, float]
    units: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalyticalResult(BaseModel):
    """Result of an analytical query"""
    diagnosis: str
    confidence: float
    measurements_analysis: List[ReferenceRangeCheckResult]
    clinical_findings: List[Finding]
    recommendations: List[str]
