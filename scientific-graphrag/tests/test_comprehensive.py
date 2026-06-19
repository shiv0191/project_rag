"""
Comprehensive tests for Scientific GraphRAG Platform
Unit and integration tests with 80%+ coverage target
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.schemas.models import (
    DocumentChunk, Entity, EntityType, QueryType, ReferenceRange
)
from shared.utils.logger import setup_logging, GraphRAGException


class TestSharedModels:
    """Test shared data models"""
    
    def test_document_chunk_creation(self):
        """Test creating a document chunk"""
        chunk = DocumentChunk(
            chunk_id="chunk1",
            doc_id="doc1",
            content="Test content",
            metadata={"page": 1}
        )
        assert chunk.chunk_id == "chunk1"
        assert chunk.content == "Test content"
    
    def test_entity_creation(self):
        """Test creating an entity"""
        entity = Entity(
            entity_id="ent1",
            name="Test Concept",
            entity_type=EntityType.CONCEPT,
            properties={"prop": "value"},
            document_ids=["doc1"]
        )
        assert entity.name == "Test Concept"
        assert entity.entity_type == EntityType.CONCEPT
    
    def test_reference_range_creation(self):
        """Test creating a reference range"""
        ref_range = ReferenceRange(
            property_name="Hemoglobin",
            unit="g/dL",
            min_value=13.5,
            max_value=17.5,
            status="normal"
        )
        assert ref_range.property_name == "Hemoglobin"
        assert ref_range.min_value == 13.5


class TestIngestionService:
    """Test ingestion service"""
    
    def test_txt_parser(self):
        """Test TXT parser"""
        from services.ingestion_service.main import TXTParser
        
        parser = TXTParser()
        content = b"Test content"
        result = parser.parse(content, "test.txt")
        
        assert "content" in result
        assert result["content"] == "Test content"
    
    def test_csv_parser(self):
        """Test CSV parser"""
        from services.ingestion_service.main import CSVParser
        
        parser = CSVParser()
        content = b"name,value\ntest,123\n"
        result = parser.parse(content, "test.csv")
        
        assert "content" in result
    
    def test_document_chunker(self):
        """Test document chunker"""
        from services.ingestion_service.main import DocumentChunker
        
        chunker = DocumentChunker(chunk_size=10, overlap=2)
        text = " ".join(["word"] * 30)
        chunks = chunker.chunk_text(text, "doc1")
        
        assert len(chunks) > 0
        assert all(isinstance(c, DocumentChunk) for c in chunks)


class TestReasoningEngine:
    """Test reasoning engines"""
    
    def test_reference_range_engine(self):
        """Test reference range engine"""
        from services.reasoning_service.main import ReferenceRangeEngine
        
        engine = ReferenceRangeEngine()
        
        # Test normal value
        result = engine.check_value("Hemoglobin", 15.0)
        assert result.status == "NORMAL"
        
        # Test low value
        result = engine.check_value("Hemoglobin", 12.0)
        assert result.status == "LOW"
        
        # Test high value
        result = engine.check_value("Hemoglobin", 18.0)
        assert result.status == "HIGH"
    
    def test_scientific_reasoning_engine(self):
        """Test scientific reasoning engine"""
        from services.reasoning_service.main import ScientificReasoningEngine
        
        engine = ScientificReasoningEngine()
        
        measurements = {
            "Ferritin": 8,
            "Hemoglobin": 10
        }
        
        findings = engine.generate_findings(measurements)
        assert isinstance(findings, list)
    
    def test_confidence_engine(self):
        """Test confidence engine"""
        from services.reasoning_service.main import ConfidenceEngine
        
        engine = ConfidenceEngine()
        
        confidence = engine.calculate_confidence(
            retrieval_score=0.9,
            reranker_score=0.85,
            graph_score=0.8,
            source_count=3
        )
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.8  # Should be high with good scores


class TestGraphService:
    """Test graph service"""
    
    @pytest.mark.skip(reason="Requires Neo4j connection")
    def test_neo4j_connection(self):
        """Test Neo4j connection"""
        from services.graph_service.main import Neo4jGraphDB
        
        graph_db = Neo4jGraphDB()
        assert graph_db.driver is not None
    
    def test_graph_service_entity_creation(self):
        """Test creating entities"""
        from services.graph_service.main import GraphService
        
        # This test would require a Neo4j instance
        # For now, just test that the service initializes
        service = GraphService()
        assert service.graph_db is not None


class TestRetrievalService:
    """Test retrieval service"""
    
    @pytest.mark.skip(reason="Requires Qdrant connection")
    def test_embedding_service(self):
        """Test embedding service"""
        from services.retrieval_service.main import EmbeddingService
        
        service = EmbeddingService()
        embeddings = service.embed_documents(["Test document"])
        assert embeddings is not None
    
    @pytest.mark.skip(reason="Requires Qdrant connection")
    def test_qdrant_connection(self):
        """Test Qdrant connection"""
        from services.retrieval_service.main import QdrantVectorDB
        
        db = QdrantVectorDB()
        assert db.client is not None


class TestUtilities:
    """Test utility functions"""
    
    def test_setup_logging(self):
        """Test logging setup"""
        logger = setup_logging("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"
    
    def test_exceptions(self):
        """Test custom exceptions"""
        from shared.utils.logger import GraphRAGException, RetrievalException
        
        with pytest.raises(GraphRAGException):
            raise GraphRAGException("Test error")
        
        with pytest.raises(RetrievalException):
            raise RetrievalException("Retrieval error")


class TestAPIGateway:
    """Test API gateway"""
    
    def test_gateway_startup(self):
        """Test gateway can be imported"""
        from services.api_service.main import app
        assert app is not None
    
    @pytest.mark.skip(reason="Requires running server")
    def test_health_endpoint(self):
        """Test health endpoint"""
        from fastapi.testclient import TestClient
        from services.api_service.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.fixture
def sample_measurements():
    """Fixture with sample measurements"""
    return {
        "Ferritin": 25.0,
        "Hemoglobin": 12.0,
        "Hematocrit": 38.0,
        "WBC": 9.5,
        "Platelets": 250.0
    }


@pytest.fixture
def sample_entity():
    """Fixture with sample entity"""
    return Entity(
        entity_id="test_entity_1",
        name="Test Entity",
        entity_type=EntityType.CONCEPT,
        properties={"source": "test"},
        document_ids=["doc1", "doc2"]
    )


# Integration test examples
@pytest.mark.integration
class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_workflow(self, sample_measurements):
        """Test end-to-end workflow"""
        from services.reasoning_service.main import (
            ReferenceRangeEngine,
            ScientificReasoningEngine,
            ConfidenceEngine
        )
        
        # Check values
        ref_engine = ReferenceRangeEngine()
        results = ref_engine.check_batch(sample_measurements)
        assert len(results) > 0
        
        # Generate findings
        reasoning_engine = ScientificReasoningEngine()
        findings = reasoning_engine.generate_findings(sample_measurements)
        
        # Calculate confidence
        confidence_engine = ConfidenceEngine()
        confidence = confidence_engine.calculate_confidence(
            retrieval_score=0.85,
            reranker_score=0.80,
            graph_score=0.75
        )
        
        assert 0.0 <= confidence <= 1.0


# Performance benchmarks
@pytest.mark.performance
class TestPerformance:
    """Performance tests"""
    
    def test_large_batch_processing(self):
        """Test processing large batch"""
        from services.reasoning_service.main import ReferenceRangeEngine
        
        engine = ReferenceRangeEngine()
        measurements = {f"Property_{i}": float(i) for i in range(100)}
        
        # Should handle large batches
        results = engine.check_batch(measurements)
        assert len(results) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
