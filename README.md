# Agentic RAG System

A local-LLM-based agentic document question-answering system that ingests multi-modal documents, stores semantic embeddings in a vector database, decomposes complex user queries into atomic sub-questions, performs independent retrieval for each sub-query, aggregates relevant context, and synthesizes grounded answers using retrieval-augmented generation.

## Features

- 🔍 **Multi-modal Document Ingestion**: Extract text, tables, and images (with OCR) from PDFs
- 🤖 **Agentic Query Processing**: Automatic query complexity analysis and decomposition
- 🎯 **Semantic Retrieval**: Vector-based search using local embedding models
- 💬 **Groq Cloud LLM**: Fast inference using Mixtral or LLaMA models
- 📊 **RAG Evaluation**: Built-in metrics using RAGAS framework
- 🐳 **Docker Deployment**: Fully containerized with Docker Compose

## Architecture

```
Document Upload → Extraction (Text/Tables/Images) → Chunking → Embedding → Vector Store
                                                                                ↓
User Query → Complexity Analysis → Query Decomposition → Multi-Retrieval → Context Aggregation → Answer Synthesis
```

## Prerequisites

- Docker and Docker Compose
- Groq API key (get free tier at https://console.groq.com)


## Quick Start

### 1. Clone and Setup

```bash
cd path/to/rag_debyes
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 3. Start Services

```bash
cd docker
docker-compose up --build
```

This will start:
- **Weaviate** vector database on port 8080
- **FastAPI** application on port 8000

### 4. Access the API

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Weaviate: http://localhost:8080

## Usage

### Ingest a Document

```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@/path/to/your/document.pdf"
```

Response:
```json
{
  "status": "success",
  "document_name": "document.pdf",
  "total_chunks": 42,
  "message": "Successfully ingested document.pdf with 42 chunks"
}
```

### Query Documents

**Simple Query:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of the document?"
  }'
```

**Complex Query (with automatic decomposition):**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the revenue growth and the main risks mentioned?"
  }'
```

Response:
```json
{
  "question": "What are the revenue growth and the main risks mentioned?",
  "answer": "According to the documents...",
  "is_complex": true,
  "sub_questions": [
    "What is the revenue growth mentioned?",
    "What are the main risks mentioned?"
  ],
  "sources": [
    {
      "document_name": "report.pdf",
      "page_number": 5,
      "content_type": "text",
      "similarity": 0.892
    }
  ],
  "metadata": {
    "total_chunks_retrieved": 8,
    "analysis_reasoning": "Query contains multiple distinct intents"
  }
}
```

## Configuration

Edit `.env` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | Your Groq API key (required) |
| `GROQ_MODEL` | `mixtral-8x7b-32768` | LLM model (`llama3-70b-8192` for better quality) |
| `CHUNK_SIZE` | 512 | Token size for document chunks |
| `CHUNK_OVERLAP` | 50 | Overlap between chunks |
| `TOP_K` | 5 | Number of chunks to retrieve per query |
| `SIMILARITY_THRESHOLD` | 0.7 | Minimum similarity score |
| `LLM_TEMPERATURE` | 0.1 | LLM temperature (lower = more factual) |

## Project Structure

```
rag_debyes/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── ingestion/
│   │   ├── extractors.py    # PDF extraction (text/tables/images)
│   │   ├── chunker.py       # Document chunking
│   │   └── embedder.py      # Embedding generation
│   ├── retrieval/
│   │   ├── vector_store.py  # Weaviate operations
│   │   └── retriever.py     # Semantic search
│   ├── agents/
│   │   ├── query_analyzer.py   # Complexity analysis
│   │   ├── decomposer.py       # Query decomposition
│   │   ├── aggregator.py       # Context aggregation
│   │   └── synthesizer.py      # Answer generation
│   └── evaluation/
│       ├── metrics.py       # RAGAS evaluation
│       └── test_data.py     # Test dataset
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
└── .env
```

## How It Works

### 1. Document Ingestion

1. Upload PDF via `/ingest` endpoint
2. Extract text using `pypdf`
3. Extract tables using `tabula-py`
4. Extract images and perform OCR using `pytesseract`
5. Chunk content with metadata (512 tokens, 50 overlap)
6. Generate embeddings using `sentence-transformers`
7. Store in Weaviate vector database

### 2. Query Processing (Agentic Workflow)

1. **Query Analysis**: LLM determines if query is simple or complex
2. **Decomposition** (if complex): Break into atomic sub-questions
3. **Retrieval**: Semantic search for each sub-question independently
4. **Aggregation**: Deduplicate and rank retrieved chunks
5. **Synthesis**: LLM generates grounded answer from context

### 3. Query Decomposition Example

**Input:**
> "Explain the revenue growth and the risks mentioned in the report."

**Decomposed:**
1. "What revenue growth is mentioned in the report?"
2. "What risks are mentioned in the report?"

Each sub-question retrieves independently, ensuring comprehensive coverage.

## Evaluation

The system includes RAGAS-based evaluation:

1. Create test cases in `app/evaluation/test_data.py`
2. Run evaluation (add `/evaluate` endpoint if needed)
3. Metrics computed:
   - Context Precision
   - Context Recall
   - Faithfulness
   - Answer Relevancy

## Development

### Run Locally (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Install system dependencies (macOS)
brew install tesseract
brew install openjdk

# Set environment variables
export GROQ_API_KEY=your_key
export WEAVIATE_URL=http://localhost:8080

# Start Weaviate
docker run -d -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  semitechnologies/weaviate:1.23.7

# Run application
uvicorn app.main:app --reload
```

### Add Test Documents

Place sample PDFs in `tests/test_documents/` for testing.

## Troubleshooting

**Weaviate connection error:**
- Ensure Weaviate is running: `docker ps`
- Check URL in `.env`: `WEAVIATE_URL=http://weaviate:8080` (in Docker) or `http://localhost:8080` (local)

**Groq API errors:**
- Verify API key is correct
- Check rate limits (free tier has limits)

**OCR not working:**
- Ensure tesseract is installed in Docker container
- Check image quality in PDFs

**Out of memory:**
- Reduce `CHUNK_SIZE` and `TOP_K`
- Use smaller embedding model
- Limit concurrent requests

## Technology Stack

- **API Framework**: FastAPI
- **LLM Provider**: Groq Cloud (Mixtral/LLaMA)
- **LLM Framework**: LangChain
- **Vector Database**: Weaviate
- **Embeddings**: sentence-transformers
- **PDF Processing**: pypdf, tabula-py, pytesseract
- **Evaluation**: RAGAS
- **Deployment**: Docker, Docker Compose


