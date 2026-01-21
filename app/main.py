from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
import os
import logging
from pathlib import Path

from app.config import settings
from app.models import IngestResponse, QueryRequest, QueryResponse
from app.ingestion.extractors import DocumentExtractor
from app.ingestion.chunker import DocumentChunker
from app.ingestion.embedder import EmbeddingGenerator
from app.retrieval.vector_store import WeaviateVectorStore
from app.retrieval.retriever import SemanticRetriever
from app.agents.query_analyzer import QueryAnalyzer
from app.agents.decomposer import QueryDecomposer
from app.agents.aggregator import ContextAggregator
from app.agents.synthesizer import AnswerSynthesizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic RAG System",
    description="Local-LLM-based document QA system with query decomposition and semantic retrieval",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Global components (initialized on startup)
vector_store = None
embedder = None
retriever = None
llm = None
query_analyzer = None
query_decomposer = None
context_aggregator = None
answer_synthesizer = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global vector_store, embedder, retriever, llm
    global query_analyzer, query_decomposer, context_aggregator, answer_synthesizer
    
    logger.info("Initializing application components...")
    
    try:
        # Initialize vector store
        vector_store = WeaviateVectorStore(
            url=settings.weaviate_url,
            api_key=settings.weaviate_api_key
        )
        
        # Initialize embedder
        embedder = EmbeddingGenerator(model_name=settings.embedding_model)
        
        # Initialize retriever
        retriever = SemanticRetriever(
            vector_store=vector_store,
            embedder=embedder,
            top_k=settings.top_k,
            similarity_threshold=settings.similarity_threshold
        )
        
        # Initialize LLM
        llm = ChatGroq(
            groq_api_key=settings.groq_api_key,
            model_name=settings.groq_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
        
        # Initialize agents
        query_analyzer = QueryAnalyzer(llm=llm)
        query_decomposer = QueryDecomposer(llm=llm)
        context_aggregator = ContextAggregator(max_context_tokens=2048)
        answer_synthesizer = AnswerSynthesizer(llm=llm)
        
        logger.info("Application initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if vector_store:
        vector_store.close()
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agentic RAG System API",
        "version": "1.0.0",
        "endpoints": {
            "ingest": "/ingest",
            "query": "/query",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "vector_store": vector_store is not None,
            "embedder": embedder is not None,
            "llm": llm is not None
        }
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingest a PDF document.
    
    Extracts text, tables, and images, chunks the content,
    generates embeddings, and stores in vector database.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing document: {file.filename}")
        
        # Extract content
        extractor = DocumentExtractor()
        content_blocks = extractor.extract_from_pdf(str(file_path))
        
        if not content_blocks:
            raise HTTPException(status_code=400, detail="No content extracted from PDF")
        
        # Chunk content
        chunker = DocumentChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        chunks = chunker.chunk_content_blocks(content_blocks, file.filename)
        
        # Generate embeddings
        chunk_texts = [chunk['content'] for chunk in chunks]
        embeddings = embedder.generate_embeddings(chunk_texts)
        
        # Store in vector database
        vector_store.add_chunks(chunks, embeddings)
        
        # Clean up uploaded file (optional)
        # os.remove(file_path)
        
        return IngestResponse(
            status="success",
            document_name=file.filename,
            total_chunks=len(chunks),
            message=f"Successfully ingested {file.filename} with {len(chunks)} chunks"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query ingested documents.
    
    Analyzes query complexity, decomposes if needed,
    retrieves relevant context, and generates answer.
    """
    try:
        question = request.question
        logger.info(f"Processing query: {question}")
        
        # Step 1: Analyze query complexity
        analysis = query_analyzer.analyze(question)
        is_complex = analysis['is_complex']
        
        # Step 2: Decompose if complex
        if is_complex:
            sub_questions = query_decomposer.decompose(question)
            logger.info(f"Query decomposed into {len(sub_questions)} sub-questions")
        else:
            sub_questions = [question]
            logger.info("Query is simple, no decomposition needed")
        
        # Step 3: Retrieve for each sub-question
        results_by_query = retriever.retrieve_for_multiple_queries(
            queries=sub_questions,
            document_filter=request.document_filter
        )
        
        # Step 4: Aggregate context
        aggregated_chunks = context_aggregator.aggregate(results_by_query)
        formatted_context = context_aggregator.format_context(aggregated_chunks)
        
        # Step 5: Synthesize answer
        synthesis_result = answer_synthesizer.synthesize(
            question=question,
            context=formatted_context,
            sources=aggregated_chunks
        )
        
        return QueryResponse(
            question=question,
            answer=synthesis_result['answer'],
            is_complex=is_complex,
            sub_questions=sub_questions if is_complex else None,
            sources=synthesis_result['sources'],
            metadata={
                "total_chunks_retrieved": len(aggregated_chunks),
                "analysis_reasoning": analysis['reasoning']
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
