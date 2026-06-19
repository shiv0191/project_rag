# Development Guide - Scientific GraphRAG Platform

## 🎯 Objectives

This guide walks through developing a production-grade GraphRAG platform for scientific decision support.

## 📋 Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git
- OpenAI API key (optional, can use Llama)
- 8GB+ RAM
- PostgreSQL client tools (optional)

## 🚀 Getting Started

### 1. Project Setup

```bash
# Clone or create project
git clone <repo> scientific-graphrag
cd scientific-graphrag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# Minimum required:
#   OPENAI_API_KEY=sk-...
#   DEBUG=true  (for development)
```

### 3. Start Infrastructure

```bash
# Start all services
docker-compose up -d

# Verify services started
docker-compose ps

# View logs
docker-compose logs -f

# Check health
curl http://localhost:8000/health
```

## 🏗️ Architecture Overview

### Layer 1: Frontend/Client
- HTTP clients
- Authentication headers
- Query/upload endpoints

### Layer 2: API Gateway (FastAPI)
- Request routing
- Rate limiting
- Authentication
- Response formatting

### Layer 3: Service Layer
```
Intent Agent ─→ Planner Agent
    ↓                    ↓
Vector Agent ←───→ Graph Agent
    ↓                    ↓
Evidence Agent ←───→ Decision Agent
    ↓
Response Agent
```

### Layer 4: Data Layer
- Neo4j (Knowledge Graph)
- Qdrant (Vector Database)
- PostgreSQL (Structured Data)
- Redis (Caching)

## 📚 Core Components

### 1. API Gateway (Phase 1)

**File**: `services/api-service/main.py`

**Responsibilities**:
- Authentication with Bearer tokens
- Rate limiting (100 req/min)
- Health checks
- Request/response handling

**Endpoints**:
- `GET /health` - System health
- `POST /query` - Query submission
- `POST /upload` - Document upload

**Testing**:
```bash
# Health check
curl http://localhost:8000/health

# Query with auth
curl -H "Authorization: Bearer demo-token" \
  -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

### 2. Ingestion Service (Phase 2-3)

**File**: `services/ingestion-service/main.py`

**Supports**:
- PDF files (via PyMuPDF)
- CSV files
- TXT files

**Process**:
```
Document → Parse → Chunk → Embed
```

**Key Classes**:
- `PDFParser` - Extracts text from PDFs
- `CSVParser` - Parses CSV data
- `DocumentChunker` - Creates overlapping chunks
- `IngestionService` - Orchestrates process

**Usage**:
```python
from services.ingestion_service.main import IngestionService

service = IngestionService()
result = service.process_document(content, "file.pdf", DocumentType.PDF)
print(f"Chunks: {len(result.chunks)}")
```

### 3. Retrieval Service (Phase 3-4)

**File**: `services/retrieval-service/main.py`

**Components**:
- `EmbeddingService` - BAAI/bge-large-en-v1.5 embeddings
- `QdrantVectorDB` - Vector database operations
- `RetrievalService` - Unified retrieval

**Collections**:
- `scientific_papers` - Research papers
- `scientific_guidelines` - Clinical guidelines
- `reference_documents` - Supporting docs
- `ontology_documents` - Medical ontology

**Usage**:
```python
from services.retrieval_service.main import RetrievalService

service = RetrievalService()
results = service.search("query text", "scientific_papers", top_k=5)
```

### 4. Graph Service (Phase 5)

**File**: `services/graph-service/main.py`

**Node Types**:
- `Concept` - Scientific concepts
- `Chemical` - Chemical compounds
- `Disease` - Medical conditions
- `Experiment` - Experimental studies
- `ReferenceRange` - Lab reference ranges
- `Author` - Research authors
- `Property` - Measurable properties

**Relationships**:
- `RELATED_TO` - Concept to Concept
- `CAUSES` - Chemical to Disease
- `MEASURED_BY` - Property to Experiment
- `SUPPORTS` - Paper to Concept
- `APPLIES_TO` - ReferenceRange to Property

**Usage**:
```python
from services.graph_service.main import GraphService

service = GraphService()
concept = service.add_concept("Iron Deficiency")
disease = service.add_disease("Anemia")
relationship = service.add_relationship(concept.entity_id, disease.entity_id, "CAUSES")
```

### 5. Reasoning Service (Phase 10-12)

**File**: `services/reasoning-service/main.py`

**Components**:

#### Reference Range Engine
```python
engine = ReferenceRangeEngine()
result = engine.check_value("Hemoglobin", 15.0)
# result.status: "NORMAL" | "LOW" | "HIGH"
```

#### Scientific Reasoning Engine
```python
reasoning = ScientificReasoningEngine()
findings = reasoning.generate_findings({
    "Ferritin": 8,
    "Hemoglobin": 10
})
# Returns: List[Finding]
```

#### Confidence Engine
```python
confidence_engine = ConfidenceEngine()
score = confidence_engine.calculate_confidence(
    retrieval_score=0.9,
    reranker_score=0.85,
    graph_score=0.8,
    source_count=3
)
# Returns: float (0.0-1.0)
```

## 🧪 Testing

### Unit Tests

```bash
# Run specific test class
pytest tests/test_comprehensive.py::TestReasoningEngine -v

# Run with coverage
pytest tests/ --cov=services --cov=shared --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Integration Tests

```bash
# Run integration tests only
pytest tests/ -m integration -v

# Run with specific markers
pytest tests/ -m "not skip" -v
```

### Example Test

```python
def test_reference_range_engine():
    from services.reasoning_service.main import ReferenceRangeEngine
    
    engine = ReferenceRangeEngine()
    
    # Normal value
    result = engine.check_value("Hemoglobin", 15.0)
    assert result.status == "NORMAL"
    
    # Low value
    result = engine.check_value("Hemoglobin", 12.0)
    assert result.status == "LOW"
```

## 🔍 Debugging

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-service

# Last 100 lines
docker-compose logs --tail=100 api-service
```

### Database Exploration

```bash
# Neo4j Browser
http://localhost:7474

# Query example
MATCH (n) RETURN n LIMIT 10

# Qdrant UI
http://localhost:6333/dashboard

# Redis CLI
redis-cli
> KEYS *
> GET key
```

### Health Checks

```bash
# API Gateway
curl http://localhost:8000/health

# All services
for port in 8000 8001 8002 8003 8004 8005 8006; do
  curl http://localhost:$port/health 2>/dev/null | jq .
done
```

## 📦 Database Management

### Neo4j

```bash
# Connect
neo4j start

# Query
cypher-shell -u neo4j -p password

# Common queries
CREATE (n:Concept {name: "Anemia"}) RETURN n
MATCH (n) RETURN COUNT(n)
```

### PostgreSQL

```bash
# Connect
psql -h localhost -U graphrag -d graphrag

# Create tables
\dt

# Query
SELECT COUNT(*) FROM documents;
```

### Qdrant

```bash
# Python client
from qdrant_client import QdrantClient

client = QdrantClient("http://localhost:6333")
collections = client.get_collections()
print(collections)
```

## 🚀 Deployment

### Local Development

```bash
# Start all services
docker-compose up -d

# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

### Production (AWS)

```bash
# Deploy with Terraform
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### Kubernetes

```bash
# Create namespace
kubectl create namespace graphrag

# Deploy services
kubectl apply -f infrastructure/kubernetes/

# Check status
kubectl get pods -n graphrag
kubectl logs <pod-name> -n graphrag
```

## 📊 Performance Tuning

### Optimization Tips

1. **Vector Database**
   - Adjust `VECTOR_SIZE` based on model
   - Use batch operations for ingestion
   - Monitor memory usage

2. **Neo4j**
   - Create indexes on frequently queried properties
   - Use APOC plugins for complex queries
   - Monitor query performance

3. **API Gateway**
   - Adjust `RateLimiter` settings
   - Enable caching with Redis
   - Use connection pooling

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs api-service

# Verify port availability
lsof -i :8000

# Restart service
docker-compose restart api-service
```

### Connection Errors

```bash
# Check network
docker network ls
docker network inspect graphrag-network

# Test connectivity
docker exec api-service curl http://neo4j:7687
```

### Memory Issues

```bash
# Check resource usage
docker stats

# Increase limits in docker-compose.yml
services:
  neo4j:
    mem_limit: 2g
```

## 📚 Additional Resources

### Documentation
- [README.md](./README.md) - Project overview
- [API Documentation](./docs/api.md)
- [Architecture Guide](./docs/architecture.md)

### External Resources
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Neo4j Docs](https://neo4j.com/docs/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [LangChain Docs](https://python.langchain.com/docs/)
- [RAGAS Docs](https://docs.ragas.io/)

## ✅ Next Steps

1. **Phase 6**: Implement entity extraction pipeline
2. **Phase 7-8**: Build hybrid retrieval with reranking
3. **Phase 13-14**: Integrate evaluation & observability
4. **Phase 15-17**: Prepare production deployment

## 🤝 Contributing

1. Create a feature branch
2. Write tests (80%+ coverage required)
3. Update documentation
4. Submit pull request

## 📝 Notes

- All services should have health check endpoints
- Use async/await for I/O operations
- Log important operations
- Add error handling
- Document complex logic

---

**Version**: 1.0.0-alpha
**Last Updated**: 2024
