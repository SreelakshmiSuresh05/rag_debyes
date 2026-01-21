from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
import json
import logging

logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """Analyze query complexity to determine if decomposition is needed."""
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query analysis expert. Analyze if a user query is simple (single intent) or complex (multiple intents).

A query is COMPLEX if it:
- Asks multiple distinct questions
- Requires information from different topics
- Contains "and", "also", "additionally" connecting different questions

A query is SIMPLE if it:
- Asks one focused question
- Can be answered with a single coherent response

Respond ONLY with valid JSON in this exact format:
{{"is_complex": true/false, "reasoning": "brief explanation"}}"""),
            ("human", "Query: {query}")
        ])
    
    def analyze(self, query: str) -> dict:
        """
        Analyze query complexity.
        
        Args:
            query: User query
            
        Returns:
            Dict with 'is_complex' (bool) and 'reasoning' (str)
        """
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({"query": query})
            
            # Parse JSON response
            result = json.loads(response.content)
            
            logger.info(f"Query analysis - Complex: {result['is_complex']}, Reason: {result['reasoning']}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {response.content}")
            # Default to simple if parsing fails
            return {"is_complex": False, "reasoning": "Failed to parse response"}
        
        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")
            return {"is_complex": False, "reasoning": f"Error: {str(e)}"}
