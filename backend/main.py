from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.rag_service import ask_question


app = FastAPI(
    title="IFRS/IAS Research Assistant",
    description=(
        "AI-powered IFRS and IAS research assistant using "
        "Retrieval-Augmented Generation (RAG), hybrid retrieval, "
        "FAISS, TF-IDF and Qwen3."
    ),
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------

class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="The IFRS/IAS accounting question."
    )


class Source(BaseModel):
    standard: str
    paragraph: str
    score: float


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "application": "IFRS/IAS Research Assistant",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "IFRS/IAS Research Assistant"
    }


# ---------------------------------------------------------
# Ask Question
# ---------------------------------------------------------

@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):

    try:

        question = request.question.strip()

        if not question:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty."
            )

        result = ask_question(
            question,
            top_k=5
        )

        return result

    except HTTPException:
        raise

    except Exception as error:

        print(f"RAG error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the accounting question."
        )