docker-compose up -d
Start-Sleep -Seconds 10
python create_qdrant_collections.py
