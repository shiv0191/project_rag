"""
Agent Service - Phase 9

Implements LangGraph workflow with multiple agents
- Intent Agent
- Planner Agent
- Vector Agent
- Graph Agent
- Evidence Agent
- Decision Agent
- Response Agent
"""

from fastapi import FastAPI
import logging

from shared.utils.logger import setup_logging

logger = setup_logging(__name__)

app = FastAPI(title="Agent Service", version="1.0.0")


@app.post("/process-query")
async def process_query(query: str):
    """Process a query through the agent workflow"""
    try:
        # In Phase 9, this will coordinate all agents
        # For now, return a placeholder response
        
        return {
            "status": "success",
            "query": query,
            "message": "Agent workflow - under development"
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "agent-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
