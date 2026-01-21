from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SemanticRetriever:
    """Retrieve relevant document chunks using semantic search."""
    
    def __init__(self, vector_store, embedder, top_k: int = 5, similarity_threshold: float = 0.7):
        self.vector_store = vector_store
        self.embedder = embedder
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        document_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Search query
            top_k: Number of results (uses default if None)
            document_filter: Optional document name filter
            
        Returns:
            List of relevant chunks with metadata
        """
        k = top_k or self.top_k
        
        # Generate query embedding
        query_embedding = self.embedder.generate_single_embedding(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=k,
            document_filter=document_filter,
            similarity_threshold=self.similarity_threshold
        )
        
        logger.info(f"Retrieved {len(results)} chunks for query: '{query[:50]}...'")
        
        return results
    
    def retrieve_for_multiple_queries(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        document_filter: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve chunks for multiple queries independently.
        
        Args:
            queries: List of search queries
            top_k: Number of results per query
            document_filter: Optional document name filter
            
        Returns:
            Dictionary mapping queries to their results
        """
        results_by_query = {}
        
        for query in queries:
            results = self.retrieve(
                query=query,
                top_k=top_k,
                document_filter=document_filter
            )
            results_by_query[query] = results
        
        logger.info(f"Retrieved chunks for {len(queries)} queries")
        
        return results_by_query
