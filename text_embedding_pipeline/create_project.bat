@echo off
echo ==========================================
echo Creating Text Embedding Pipeline Structure
echo ==========================================

:: Create directories
mkdir input
mkdir output
mkdir logs
mkdir src

:: Root files
type nul > .env
type nul > README.md
type nul > requirements.txt
type nul > main.py

:: src files
type nul > src\__init__.py
type nul > src\config.py
type nul > src\reader.py
type nul > src\embedder.py
type nul > src\writer.py
type nul > src\models.py
type nul > src\utils.py
type nul > src\pipeline.py

echo.
echo Project structure created successfully.
echo.

tree /F

pause
