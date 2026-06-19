# Scientific GraphRAG Decision Support Platform

A production-grade GraphRAG (Graph Retrieval-Augmented Generation) platform for intelligent scientific decision support, combining knowledge graphs, vector databases, and AI-powered reasoning.

## 🎯 Project Overview

This platform is designed to:

- **Retrieve** scientific information using hybrid search (BM25, dense, graph-based)
- **Reason** about clinical data using knowledge graphs and reference ranges
- **Decide** on diagnoses and recommendations with confidence scores
- **Explain** findings with evidence chains and source citations

## 🏗️ Architecture

```
Frontend/Client
    ↓
┌─────────────────────────────────────┐
│     FastAPI Gateway (8000)          │
│  - Authentication & Rate Limiting   │
│  - Health Checks                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Multi-Agent Workflow                  │
│  1. Intent Agent (classify query type)                       │
│  2. Planner Agent (create execution plan)                    │
│  3. Vector Agent (search Qdrant)                             │
│  4. Graph Agent (query Neo4j)                                │
│  5. Evidence Agent (merge evidence)                          │
│  6. Decision Agent (reasoning)                               │
│  7. Response Agent (format output)                           │
└─────────────────────────────────────────────────────────────┘
    ↓
┌──────────────────┬──────────────────┬──────────────────┐
│  Neo4j Graph DB  │  Qdrant Vector   │  Reference Ranges│
│  (Knowledge)     │  DB (Semantic)   │  Engine          │
└──────────────────┴──────────────────┴──────────────────┘
```

## 🛠️ Tech Stack

### Core Services
- **API Gateway**: FastAPI with authentication & rate limiting
- **Ingestion**: PDF/CSV/TXT document processing with chunking
- **Graph**: Neo4j knowledge graph with entity/relationship management
- **Retrieval**: Qdrant vector DB with BAAI/bge embeddings
- **Reasoning**: Scientific reasoning with reference ranges & confidence scoring
- **Agents**: LangGraph workflow orchestration
- **Evaluation**: RAGAS + DeepEval metrics

### Infrastructure
- **Docker & Docker Compose** for containerization
- **Kubernetes** for production orchestration
- **AWS** (EKS, S3, CloudWatch, ALB)
- **Terraform** for IaC

### Databases
- **Neo4j**: Knowledge graph
- **Qdrant**: Vector embeddings
- **PostgreSQL**: Structured data
- **Redis**: Caching

## 📦 Project Structure

```
scientific-graphrag/
├── services/
│   ├── api-service/              # FastAPI Gateway
│   ├── ingestion-service/        # Document ingestion & chunking
│   ├── graph-service/            # Neo4j integration
│   ├── retrieval-service/        # Embeddings & Qdrant
│   ├── agent-service/            # LangGraph agents
│   ├── evaluation-service/       # RAGAS evaluation
│   └── reasoning-service/        # Scientific reasoning
├── shared/
│   ├── models/                   # LLM providers
│   ├── prompts/                  # Agent prompts
│   ├── config/                   # Configuration
│   ├── utils/                    # Utilities
│   └── schemas/                  # Data models
├── infrastructure/
│   ├── docker/                   # Docker configs
│   ├── kubernetes/               # K8s manifests
│   ├── terraform/                # AWS IaC
│   └── scripts/                  # Automation
├── datasets/
│   ├── papers/                   # Scientific papers
│   ├── ontology/                 # Medical ontology
│   ├── reference_ranges/         # Lab ranges
│   └── guidelines/               # Clinical guidelines
├── tests/                        # Comprehensive test suite
├── docker-compose.yml            # Local development
└── requirements.txt              # Dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- OpenAI API key (or Llama setup)

### 1. Clone & Install

```bash
cd scientific-graphrag
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

### 3. Start Services

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or run services individually
python services/api-service/main.py
python services/ingestion-service/main.py
python services/graph-service/main.py
python services/retrieval-service/main.py
python services/reasoning-service/main.py
```

### 4. Test the Platform

```bash
# Health check
curl http://localhost:8000/health

# Upload a document
curl -X POST -F "file=@paper.pdf" http://localhost:8000/upload

# Query the system
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the normal Ferritin range?"}'
```

## 📋 Development Phases

### ✅ Phase 1: FastAPI Gateway
- Authentication & rate limiting
- Health checks and status endpoints
- Request/response handling

### ✅ Phase 2-3: Ingestion & Embeddings
- PDF, CSV, TXT parsing
- Document chunking with overlap
- BAAI/bge-large-en-v1.5 embeddings

### ✅ Phase 4: Vector Database
- Qdrant collection management
- Document upsertion
- Semantic search

### ✅ Phase 5: Knowledge Graph
- Neo4j entity/relationship management
- Scientific entity types (concepts, chemicals, diseases, etc.)
- Graph relationships

### 🚧 Phase 6: Entity Extraction
- Named entity recognition
- Relationship extraction
- Graph population

### 🚧 Phase 7-8: Hybrid Retrieval
- BM25 search
- Dense vector search
- Graph-based search
- BAAI/bge-reranker-large reranking

### ✅ Phase 9: LangGraph Agents
- Multi-agent workflow
- Intent classification
- Planning & execution

### ✅ Phase 10-12: Reasoning Engines
- Reference range checking
- Clinical decision support
- Confidence scoring

### 🚧 Phase 13-14: Evaluation & Observability
- RAGAS metrics (Recall@K, NDCG, Faithfulness, etc.)
- LangSmith integration
- Performance tracking

### 🚧 Phase 15-17: Deployment
- Docker containerization
- Kubernetes orchestration
- AWS deployment with Terraform

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=services --cov=shared --cov-report=html

# Specific test class
pytest tests/test_comprehensive.py::TestReasoningEngine -v

# Integration tests only
pytest tests/ -m integration
```

## 📚 API Endpoints

### Gateway (8000)
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `POST /query` - Query the system
- `POST /upload` - Upload document
- `GET /status` - System status

### Ingestion (8001)
- `POST /ingest` - Ingest document
- `GET /health` - Service health

### Graph (8002)
- `POST /entities` - Add entity
- `POST /relationships` - Add relationship
- `GET /search` - Search entities
- `GET /health` - Service health

### Retrieval (8003)
- `POST /search` - Search documents
- `POST /add-documents` - Add to collection
- `GET /collections` - List collections
- `GET /health` - Service health

### Reasoning (8006)
- `POST /check-value` - Check against reference range
- `POST /generate-findings` - Generate clinical findings
- `POST /calculate-confidence` - Calculate confidence score
- `GET /health` - Service health

## 🔐 Authentication

The platform uses Bearer tokens for authentication:

```bash
curl -H "Authorization: Bearer your-token" http://localhost:8000/query
```

## 🎓 Example Queries

### Reference Range Query
```json
{
  "query": "What is the normal Ferritin range?",
  "query_type": "reference_range"
}
```

### Scientific Context Query
```json
{
  "query": "Can low Ferritin cause fatigue?",
  "query_type": "scientific_context"
}
```

### Analytical Decision Query
```json
{
  "query": "Ferritin=8, Hemoglobin=10. What does this indicate?",
  "query_type": "analytical_decision"
}
```

## 📊 Success Criteria

The system successfully answers:

1. ✅ Reference range queries
2. ✅ Scientific context queries
3. ✅ Analytical decision queries with evidence-backed answers

Expected outputs include:
- Evidence-backed findings
- Confidence scores (0.0-1.0)
- Source citations
- Reasoning chains
- Graph evidence
- Retrieved documents

## 🔄 CI/CD Pipeline

The project includes:

```bash
# Pre-commit checks
pytest tests/
pylint services/ shared/
black services/ shared/

# Test coverage
pytest --cov=services --cov=shared --cov-report=term-missing --cov-fail-under=80

# Docker build & push
docker-compose build
docker-compose push
```

## 📈 Performance Metrics

Target metrics:
- **Latency**: <500ms for retrieval, <1s for full workflow
- **Throughput**: >100 queries/second
- **Recall@5**: >0.85
- **NDCG**: >0.80
- **Faithfulness**: >0.85

## 🐛 Debugging

```bash
# View logs
docker-compose logs -f api-service

# Connect to Neo4j browser
http://localhost:7474

# Access Qdrant UI
http://localhost:6333/dashboard

# Check Redis
redis-cli
```

## 📝 Configuration

Key environment variables in `.env`:

```bash
# LLM
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Databases
NEO4J_URI=bolt://neo4j:7687
QDRANT_URL=http://qdrant:6333
DATABASE_URL=postgresql://user:pass@localhost:5432/graphrag

# API
DEBUG=false
API_TITLE="Scientific GraphRAG Platform"

# Models
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
RERANKER_MODEL=BAAI/bge-reranker-large
```

## 🤝 Contributing

1. Create a feature branch
2. Implement changes with tests
3. Ensure 80%+ test coverage
4. Submit PR with description

## 📄 License

MIT License - See LICENSE file

## 📞 Support

For issues and questions:
- Open GitHub issues
- Check documentation in `docs/`
- Review test examples in `tests/`

## 🎯 Roadmap

- [ ] Phase 6: Entity extraction pipeline
- [ ] Phase 7-8: Hybrid retrieval with reranking
- [ ] Phase 13-14: Evaluation & observability
- [ ] Phase 15-17: Production deployment
- [ ] Fine-tuning on scientific datasets
- [ ] Multi-language support
- [ ] Real-time streaming responses

---

**Project Status**: In Development 🚀
**Version**: 1.0.0-alpha
**Last Updated**: 2024
