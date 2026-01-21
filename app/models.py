from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    pass  # File will be uploaded via multipart/form-data


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    status: str
    document_name: str
    total_chunks: int
    message: str


class QueryRequest(BaseModel):
    """Request model for querying documents."""
    question: str = Field(..., description="User's question about the documents")
    document_filter: Optional[str] = Field(None, description="Optional filter by document name")


class SubQuestion(BaseModel):
    """Model for decomposed sub-questions."""
    question: str
    retrieved_chunks: List[str] = []


class QueryResponse(BaseModel):
    """Response model for query results."""
    question: str
    answer: str
    is_complex: bool
    sub_questions: Optional[List[str]] = None
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class EvaluationMetrics(BaseModel):
    """Model for evaluation metrics."""
    context_precision: float
    context_recall: float
    faithfulness: float
    answer_relevancy: float


class EvaluationResult(BaseModel):
    """Response model for evaluation results."""
    metrics: EvaluationMetrics
    test_cases_count: int
    summary: str
