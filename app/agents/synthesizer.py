from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AnswerSynthesizer:
    """Generate grounded answers using retrieved context."""
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that answers questions based ONLY on the provided context.

CRITICAL RULES:
1. Use ONLY information from the provided context
2. If the answer is not in the context, clearly state "The information is not available in the provided documents"
3. Synthesize information from multiple sources when relevant
4. Be concise and accurate
5. Cite sources when possible (e.g., "According to [Source 1]...")
6. Do NOT make up or infer information not present in the context"""),
            ("human", """Context:
{context}

User Question: {question}

Answer:""")
        ])
    
    def synthesize(
        self,
        question: str,
        context: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate an answer based on the provided context.
        
        Args:
            question: User's original question
            context: Formatted context from retrieved chunks
            sources: List of source chunks for citation
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "context": context,
                "question": question
            })
            
            answer = response.content.strip()
            
            logger.info(f"Generated answer for question: '{question[:50]}...'")
            
            return {
                "answer": answer,
                "sources": self._format_sources(sources),
                "context_used": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error synthesizing answer: {str(e)}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "context_used": 0
            }
    
    def _format_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source information for response."""
        sources = []
        
        for chunk in chunks:
            sources.append({
                "document_name": chunk.get('document_name', 'Unknown'),
                "page_number": chunk.get('page_number', 'N/A'),
                "content_type": chunk.get('content_type', 'text'),
                "similarity": round(chunk.get('similarity', 0), 3)
            })
        
        return sources
