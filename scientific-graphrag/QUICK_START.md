# Quick Start Guide - Scientific GraphRAG Platform

Get the platform running in 5 minutes!

## 📋 Prerequisites (2 minutes)

```bash
# Check Python version
python --version  # Must be 3.12+

# Check Docker
docker --version
docker-compose --version
```

## 🚀 Setup (3 minutes)

### Step 1: Clone/Navigate to Project
```bash
cd scientific-graphrag
```

### Step 2: Create Environment File
```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY if you have it (optional for testing)
```

### Step 3: Start Services
```bash
docker-compose up -d
```

### Step 4: Verify Services
```bash
# Wait 30 seconds for services to start
sleep 30

# Check health
curl http://localhost:8000/health
```

## ✅ Verify Everything Works

### Test 1: Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "api-gateway", "version": "1.0.0"}
```

### Test 2: Upload Document
```bash
curl -X POST -F "file=@test.txt" \
  -H "Authorization: Bearer demo-token" \
  http://localhost:8000/upload
# Expected: 200 OK with document_id
```

### Test 3: Submit Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Authorization: Bearer demo-token" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
# Expected: 200 OK with query results
```

## 📊 Monitor Services

### View Logs
```bash
docker-compose logs -f api-service
```

### Check Status
```bash
docker-compose ps
```

### Access Databases

**Neo4j Browser** (Knowledge Graph):
- URL: http://localhost:7474
- User: neo4j
- Password: password

**Qdrant UI** (Vector DB):
- URL: http://localhost:6333/dashboard

**Redis CLI**:
```bash
redis-cli
> PING
> KEYS *
```

## 🧪 Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/test_comprehensive.py -v

# Run with coverage
pytest tests/test_comprehensive.py -v --cov=services --cov=shared

# Run specific test
pytest tests/test_comprehensive.py::TestReasoningEngine -v
```

## 🔍 Explore APIs

### Reference Range Check
```bash
curl -X POST http://localhost:8006/check-value \
  -H "Content-Type: application/json" \
  -d '{
    "property_name": "Hemoglobin",
    "value": 15.0
  }'
```

### Generate Findings
```bash
curl -X POST http://localhost:8006/generate-findings \
  -H "Content-Type: application/json" \
  -d '{
    "measurements": {
      "Ferritin": 8,
      "Hemoglobin": 10
    }
  }'
```

### Calculate Confidence
```bash
curl -X POST http://localhost:8006/calculate-confidence \
  -H "Content-Type: application/json" \
  -d '{
    "retrieval_score": 0.9,
    "reranker_score": 0.85,
    "graph_score": 0.8,
    "source_count": 3
  }'
```

## 🛑 Stop Services

```bash
docker-compose down
```

## 📚 Next Steps

1. **Read Documentation**
   - [README.md](./README.md) - Full overview
   - [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) - Detailed guide
   - [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - What's been built

2. **Explore Code**
   - Services in `services/` folder
   - Shared utilities in `shared/` folder
   - Tests in `tests/` folder

3. **Add Data**
   - Place documents in `datasets/` folder
   - Ingest via `/upload` endpoint
   - Query via `/query` endpoint

4. **Deploy**
   - See DEVELOPMENT_GUIDE.md for AWS/K8s setup

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000

# Kill the process or use different port in .env
```

### Service Won't Start
```bash
# Check logs
docker-compose logs api-service

# Restart service
docker-compose restart api-service
```

### Database Connection Failed
```bash
# Verify services are running
docker-compose ps

# Check network connectivity
docker exec api-service curl http://neo4j:7687
```

## 💡 Common Commands

```bash
# View all services
docker-compose ps

# View specific service logs
docker-compose logs api-service

# Restart a service
docker-compose restart api-service

# Stop all services
docker-compose down

# Remove volumes (WARNING: data loss)
docker-compose down -v

# Rebuild images
docker-compose build

# Run command in container
docker-compose exec api-service bash
```

## 📖 Documentation Links

- [Full README](./README.md)
- [Development Guide](./DEVELOPMENT_GUIDE.md)
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md)
- [API Endpoints](./README.md#-api-endpoints)

## ⚡ Performance Tips

- Wait 30 seconds after `docker-compose up` for services to initialize
- First query may take longer as models load
- Use batch operations for bulk ingestion
- Check logs if queries seem slow

## ✨ You're Ready!

The platform is now running. Start with:
1. Uploading a test document
2. Running a sample query
3. Checking the logs
4. Exploring the databases

**Happy GraphRAG-ing! 🚀**
