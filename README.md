# IFRS / IAS Research Assistant

An AI-powered accounting research assistant that uses Retrieval-Augmented Generation (RAG) to retrieve relevant IFRS and IAS source material and generate concise answers to accounting questions.

The system combines hybrid information retrieval using semantic embeddings and TF-IDF with Qwen3 running locally through Ollama.

---

## 1. Project Overview

Accounting and finance students, accountants, auditors, and other professionals frequently need to research IFRS and IAS requirements.

Traditional document searching can require manually reviewing large standards and locating the relevant paragraphs.

This project demonstrates an AI-assisted research workflow that allows a user to enter an accounting question in natural language.

The system:

1. Receives an accounting question.
2. Automatically detects a relevant IFRS or IAS standard when possible.
3. Searches the indexed IFRS/IAS material.
4. Combines semantic and lexical retrieval.
5. Selects the most relevant paragraphs.
6. Sends the retrieved material to Qwen3.
7. Generates an answer based only on the supplied IFRS/IAS material.
8. Returns the answer together with the retrieved standard and paragraph references.

---

## 2. Objectives

The main objectives of the project are:

* Build a practical RAG application for accounting research.
* Process IFRS and IAS PDF documents.
* Preserve paragraph-level accounting references.
* Automatically identify the relevant IFRS/IAS standard from a question.
* Implement semantic retrieval using sentence embeddings.
* Implement lexical retrieval using TF-IDF.
* Combine both retrieval approaches using hybrid search.
* Use a local Large Language Model to generate answers.
* Provide an API using FastAPI.
* Provide a user interface using React.
* Return supporting IFRS/IAS paragraph references with each answer.

---

## 3. System Architecture

```text
                         User
                           |
                           v
                  +----------------+
                  | React Frontend |
                  +-------+--------+
                          |
                          | HTTP POST /ask
                          v
                  +----------------+
                  | FastAPI Backend |
                  +-------+--------+
                          |
                          v
                  +----------------+
                  | RAG Service     |
                  +-------+--------+
                          |
              +-----------+-----------+
              |                       |
              v                       v
       +-------------+         +-------------+
       | FAISS       |         | TF-IDF      |
       | Semantic    |         | Lexical     |
       | Retrieval   |         | Retrieval   |
       +------+------+         +------+------+
              |                       |
              +-----------+-----------+
                          |
                          v
                  Hybrid Retrieval
                          |
                          v
                  +---------------+
                  | Qwen3:8b      |
                  | Ollama        |
                  +-------+-------+
                          |
                          v
                 Answer + References
```

---

## 4. Technology Stack

### Backend

* Python
* FastAPI
* Pydantic
* Ollama

### Retrieval

* FAISS
* Sentence Transformers
* `all-MiniLM-L6-v2`
* TF-IDF
* Scikit-learn

### Document Processing

* PyMuPDF
* Python

### Large Language Model

* Qwen3:8b
* Ollama

### Frontend

* React
* Vite
* JavaScript
* CSS

### Development

* VS Code
* Git
* GitHub

---

## 5. RAG Pipeline

### Step 1 — PDF ingestion

IFRS and IAS standards are stored as PDF documents.

The PDF extraction process uses PyMuPDF to extract document blocks while retaining their positional information.

---

### Step 2 — Document processing

The extracted PDF blocks are processed into paragraph-level chunks.

Each chunk contains:

```text
standard
paragraph
section
text
```

Example:

```json
{
  "standard": "IFRS 15",
  "paragraph": "9",
  "section": "Identifying the contract",
  "text": "..."
}
```

Paragraph-level processing is important because accounting research normally requires references to specific standard paragraphs.

---

### Step 3 — Embeddings

The text of each chunk is converted into a numerical vector using:

```text
all-MiniLM-L6-v2
```

The resulting vectors are used for semantic similarity search.

---

### Step 4 — FAISS retrieval

FAISS is used to perform efficient similarity search against the document embeddings.

The implementation uses normalized vectors and inner-product similarity.

---

### Step 5 — TF-IDF retrieval

A TF-IDF index is also constructed using Scikit-learn.

The lexical search uses word and bigram features to identify documents containing important accounting terminology.

---

### Step 6 — Hybrid retrieval

Semantic and lexical retrieval results are combined.

This allows the system to benefit from:

* semantic similarity
* exact accounting terminology
* important phrases
* standard-specific filtering
* query intent

---

### Step 7 — LLM generation

The retrieved IFRS/IAS material is supplied to Qwen3 through Ollama.

The model is instructed to:

* use only the supplied source material
* avoid inventing requirements
* avoid inventing paragraph numbers
* provide relevant paragraph references
* state when the retrieved material is insufficient

---

## 6. Automatic Standard Detection

The system can detect standards such as:

```text
IFRS 15
IAS 16
IAS 37
IFRS 9
IFRS 16
IAS 38
```

from the user's question.

The user does not need to manually select the accounting standard.

For example:

```text
What is the depreciation policy under IAS 16?
```

automatically applies an IAS 16 filter during retrieval.

---

## 7. Example Questions

### IFRS 15

```text
What are the recognition criteria for a contract under IFRS 15?
```

### IAS 16

```text
What is the depreciation policy for property, plant and equipment under IAS 16?
```

### IAS 37

```text
What is the difference between a provision and a contingent liability?
```

### IFRS 15

```text
What are the five steps of revenue recognition under IFRS 15?
```

---

## 8. Project Structure

```text
ifrs-rag-assistant/
│
├── backend/
│   ├── main.py
│   └── rag_service.py
│
├── frontend/
│   └── React/Vite application
│
├── ingestion/
│   ├── pdf_extractor.py
│   ├── document_processor.py
│   └── create_embeddings.py
│
├── vectorstore/
│   ├── build_index.py
│   └── search.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 9. Installation

### Requirements

Install:

* Python 3.12
* Node.js
* npm
* Ollama

---

## 10. Python Environment

From the project root:

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

---

## 11. Ollama Setup

Install Ollama and make sure it is running.

Verify:

```powershell
ollama --version
```

Download the Qwen model:

```powershell
ollama pull qwen3:8b
```

Verify the model:

```powershell
ollama list
```

The project expects:

```text
qwen3:8b
```

---

## 12. Preparing the IFRS/IAS Documents

Place the IFRS/IAS PDF files in:

```text
data/raw/
```

Run PDF extraction:

```powershell
python ingestion/pdf_extractor.py
```

Run document processing:

```powershell
python ingestion/document_processor.py
```

Create embeddings:

```powershell
python ingestion/create_embeddings.py
```

Build the FAISS index:

```powershell
python vectorstore/build_index.py
```

The exact processing sequence may depend on the current implementation of the ingestion scripts.

---

## 13. Running the Backend

From the project root:

```powershell
uvicorn backend.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 14. Running the Frontend

Open another terminal.

Move to the frontend directory:

```powershell
cd frontend
```

Install JavaScript dependencies if required:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

## 15. API Example

### Request

```http
POST /ask
```

Example:

```json
{
  "question": "What are the recognition criteria for a contract under IFRS 15?"
}
```

### Response

```json
{
  "question": "What are the recognition criteria for a contract under IFRS 15?",
  "answer": "...",
  "sources": [
    {
      "standard": "IFRS 15",
      "paragraph": "9",
      "score": 0.6273
    }
  ]
}
```

---

## 16. Current Limitations

This is a prototype research assistant and should not be considered a replacement for professional accounting judgment or authoritative IFRS/IAS publications.

Current limitations include:

* Retrieval quality can vary depending on the wording of the question.
* Some questions may retrieve related but not optimal paragraphs.
* Standard detection is rule-based rather than a dedicated classification model.
* The application currently uses a local Qwen3 model through Ollama.
* Conversational memory is not currently implemented.
* The system does not independently verify the generated answer against external authoritative sources.
* Section metadata extracted from PDF layouts may not always be perfect.
* The quality of the answer depends on the quality of the retrieved source material.

---

## 17. Future Improvements

Future development could include:

* Improved paragraph-aware retrieval.
* Better reranking using a cross-encoder.
* More advanced query expansion.
* Improved IAS/IFRS standard classification.
* Hybrid retrieval optimization.
* Citation validation.
* Answer faithfulness evaluation.
* Conversational research history.
* User authentication.
* Database storage for research history.
* Document version management.
* Support for additional accounting standards.
* Cloud deployment.
* More advanced evaluation datasets.
* Automated retrieval quality benchmarks.

---

## 18. Disclaimer

This application is an educational and research prototype.

Users should refer to the applicable official IFRS/IAS publications and exercise professional judgment before relying on accounting conclusions for financial reporting, audit, regulatory, tax, or other professional purposes.

---

## 19. Author

Developed as an AI/ML portfolio project demonstrating the application of Retrieval-Augmented Generation to accounting and IFRS/IAS research.
