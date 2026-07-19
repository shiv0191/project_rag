@echo off
setlocal

REM ============================================================
REM Create Reranker Pipeline Project Structure
REM ============================================================

set PROJECT_NAME=reranker_pipeline

echo.
echo Creating project: %PROJECT_NAME%
echo.

mkdir %PROJECT_NAME%
cd %PROJECT_NAME%

REM Root files
type nul > main.py
type nul > README.md
type nul > requirements.txt
type nul > .env

REM Directories
mkdir input
mkdir output
mkdir logs
mkdir models
mkdir src

REM Source files
type nul > src\__init__.py
type nul > src\config.py
type nul > src\models.py
type nul > src\reader.py
type nul > src\reranker.py
type nul > src\writer.py
type nul > src\pipeline.py
type nul > src\utils.py

echo.
echo ==========================================
echo Project structure created successfully!
echo ==========================================
echo.

tree /F

pause