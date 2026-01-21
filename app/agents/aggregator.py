from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ContextAggregator:
    """Aggregate and deduplicate retrieved context from multiple sub-questions."""
    
    def __init__(self, max_context_tokens: int = 2048):
        self.max_context_tokens = max_context_tokens
    
    def aggregate(
        self,
        results_by_query: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Aggregate context from multiple query results.
        
        Args:
            results_by_query: Dictionary mapping queries to their retrieved chunks
            
        Returns:
            Deduplicated and ranked list of chunks
        """
        # Collect all chunks
        all_chunks = []
        seen_content = set()
        
        for query, chunks in results_by_query.items():
            for chunk in chunks:
                content = chunk['content']
                
                # Deduplicate by content
                if content not in seen_content:
                    seen_content.add(content)
                    all_chunks.append(chunk)
        
        # Sort by similarity score (highest first)
        all_chunks.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        # Limit by token count (rough estimate: 1 token ≈ 4 characters)
        aggregated_chunks = []
        total_chars = 0
        max_chars = self.max_context_tokens * 4
        
        for chunk in all_chunks:
            chunk_chars = len(chunk['content'])
            if total_chars + chunk_chars <= max_chars:
                aggregated_chunks.append(chunk)
                total_chars += chunk_chars
            else:
                break
        
        logger.info(f"Aggregated {len(aggregated_chunks)} unique chunks from {sum(len(c) for c in results_by_query.values())} total results")
        
        return aggregated_chunks
    
    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format aggregated chunks into a context string.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            doc_name = chunk.get('document_name', 'Unknown')
            page_num = chunk.get('page_number', 'N/A')
            content_type = chunk.get('content_type', 'text')
            content = chunk['content']
            
            context_parts.append(
                f"[Source {i}] Document: {doc_name}, Page: {page_num}, Type: {content_type}\n{content}"
            )
        
        formatted_context = "\n\n---\n\n".join(context_parts)
        
        return formatted_context
