from fastapi import FastAPI
from pydantic import BaseModel

from backend.rag_service import ask_question


# --------------------------------------------------
# Create FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="IFRS/IAS Research Assistant",
    description=(
        "AI-powered IFRS and IAS research assistant "
        "using RAG, FAISS and Qwen3."
    ),
    version="1.0.0"
)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "ok"
    }


# --------------------------------------------------
# Ask accounting question
# --------------------------------------------------

@app.post("/ask")
def ask(request: QuestionRequest):

    result = ask_question(
        request.question,
        top_k=5
    )

    return result