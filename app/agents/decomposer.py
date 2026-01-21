from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from typing import List
import json
import logging

logger = logging.getLogger(__name__)


class QueryDecomposer:
    """Decompose complex queries into atomic sub-questions."""
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query decomposition expert. Break down complex queries into atomic sub-questions.

Rules for sub-questions:
1. Each sub-question should cover ONE specific intent
2. Each should be answerable independently
3. Together they should cover the full original query
4. Keep them concise and focused
5. Maintain the original query's context

Respond ONLY with valid JSON in this exact format:
{{"sub_questions": ["question1", "question2", ...]}}"""),
            ("human", "Original query: {query}\n\nDecompose this into atomic sub-questions.")
        ])
    
    def decompose(self, query: str) -> List[str]:
        """
        Decompose a complex query into sub-questions.
        
        Args:
            query: Complex user query
            
        Returns:
            List of sub-questions
        """
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({"query": query})
            
            # Parse JSON response
            result = json.loads(response.content)
            sub_questions = result.get("sub_questions", [])
            
            logger.info(f"Decomposed query into {len(sub_questions)} sub-questions")
            for i, sq in enumerate(sub_questions, 1):
                logger.info(f"  {i}. {sq}")
            
            return sub_questions
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {response.content}")
            # Fallback: return original query
            return [query]
        
        except Exception as e:
            logger.error(f"Error decomposing query: {str(e)}")
            return [query]
