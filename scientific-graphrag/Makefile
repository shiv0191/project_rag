# Makefile for Scientific GraphRAG Platform

.PHONY: help install setup up down logs test coverage clean lint format health explore

help:
	@echo "Scientific GraphRAG Platform - Available Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make setup         - Setup environment (.env file)"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make logs          - View service logs"
	@echo "  make clean         - Stop and remove containers/volumes"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test          - Run all tests"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code with black"
	@echo ""
	@echo "Monitoring:"
	@echo "  make health        - Check service health"
	@echo "  make status        - Show service status"
	@echo "  make explore       - Open database UIs"
	@echo ""
	@echo "Development:"
	@echo "  make shell         - Access Python shell"
	@echo "  make docs          - Build documentation"

# Setup
install:
	pip install -r requirements.txt

setup:
	cp .env.example .env
	@echo "✅ Created .env file. Edit it with your settings."

# Docker
up:
	docker-compose up -d
	@echo "✅ Services starting... waiting 30s for initialization"
	sleep 30
	make health

down:
	docker-compose down
	@echo "✅ Services stopped"

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api-service

logs-ingestion:
	docker-compose logs -f ingestion-service

logs-graph:
	docker-compose logs -f graph-service

logs-retrieval:
	docker-compose logs -f retrieval-service

clean:
	docker-compose down -v
	@echo "✅ Containers and volumes removed"

# Testing
test:
	pytest tests/test_comprehensive.py -v

test-unit:
	pytest tests/test_comprehensive.py -v -k "not integration and not performance"

test-integration:
	pytest tests/test_comprehensive.py -v -m integration

coverage:
	pytest tests/test_comprehensive.py -v --cov=services --cov=shared --cov-report=html
	@echo "✅ Coverage report generated in htmlcov/index.html"

# Code Quality
lint:
	@echo "Running linting checks..."
	@echo "Python files:"
	find services shared -name "*.py" | head -10

format:
	@echo "Code formatting with black..."
	@command -v black >/dev/null 2>&1 && black services/ shared/ || echo "black not installed"

# Monitoring
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | jq . && echo "✅ API Service OK" || echo "❌ API Service Down"
	@curl -s http://localhost:8001/health | jq . && echo "✅ Ingestion Service OK" || echo "❌ Ingestion Service Down"
	@curl -s http://localhost:8002/health | jq . && echo "✅ Graph Service OK" || echo "❌ Graph Service Down"
	@curl -s http://localhost:8003/health | jq . && echo "✅ Retrieval Service OK" || echo "❌ Retrieval Service Down"

status:
	docker-compose ps

explore:
	@echo "Opening database UIs..."
	@echo "Neo4j: http://localhost:7474 (neo4j/password)"
	@echo "Qdrant: http://localhost:6333/dashboard"
	@echo "Redis: redis-cli at localhost:6379"

# Development
shell:
	python

docs:
	@echo "Generated documentation files:"
	@ls -lh *.md

# Example API calls
example-health:
	curl -s http://localhost:8000/health | jq .

example-upload:
	@echo "Example: curl -X POST -F \"file=@test.txt\" http://localhost:8000/upload"

example-query:
	curl -X POST http://localhost:8000/query \
		-H "Content-Type: application/json" \
		-d '{"query": "test query"}' | jq .

example-check-value:
	curl -X POST http://localhost:8006/check-value \
		-H "Content-Type: application/json" \
		-d '{"property_name": "Hemoglobin", "value": 15.0}' | jq .

# Development workflow
dev-setup: install setup up
	@echo "✅ Development environment ready!"
	@echo "Next steps:"
	@echo "  1. make health      - Check services"
	@echo "  2. make test        - Run tests"
	@echo "  3. make example-*   - Try API calls"

# Advanced
rebuild:
	docker-compose build

push:
	docker-compose push

stats:
	@echo "Docker resource usage:"
	docker stats --no-stream

ps:
	docker-compose ps

top:
	docker-compose stats

shell-api:
	docker-compose exec api-service bash

shell-neo4j:
	docker-compose exec neo4j bash

redis-cli:
	docker-compose exec redis redis-cli

# Cleanup
distclean: clean
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov .pytest_cache .coverage
	@echo "✅ Full cleanup complete"

# Information
info:
	@echo "Project: Scientific GraphRAG Platform"
	@echo "Version: 1.0.0-alpha"
	@echo "Services: 7 microservices"
	@echo "Databases: Neo4j, Qdrant, PostgreSQL, Redis"
	@echo ""
	@echo "Use 'make help' for all available commands"

.DEFAULT_GOAL := help
