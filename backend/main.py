"""
FastAPI main application for Neurologix Smart Search POV
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Neurologix Smart Search API",
    description="Natural Language Query Interface for C3Logix Concussion Management",
    version="1.0.0"
)

# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class QueryRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    team_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    source_modules: list[str]
    metadata: dict = {}

@app.get("/")
async def root():
    return {"message": "Neurologix Smart Search API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "neurologix-smart-search"}

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process natural language query and return structured response
    """
    try:
        # Import here to avoid circular imports
        from backend.services.query_processor import QueryProcessor
        
        processor = QueryProcessor()
        result = processor.process_query(
            question=request.question,
            team_id=request.team_id
        )
        
        return QueryResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            source_modules=result["source_modules"],
            metadata=result["metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
