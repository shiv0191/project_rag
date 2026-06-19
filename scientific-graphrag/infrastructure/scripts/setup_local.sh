#!/bin/bash
docker-compose up -d
sleep 10
python create_qdrant_collections.py
