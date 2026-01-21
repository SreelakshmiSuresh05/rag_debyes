import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery
from typing import List, Dict, Any, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)


class WeaviateVectorStore:
    """Weaviate vector database operations."""
    
    CLASS_NAME = "DocumentChunk"
    
    def __init__(self, url: str, api_key: Optional[str] = None):
        """Initialize Weaviate client and create schema if needed."""
        try:
            if api_key:
                self.client = weaviate.connect_to_custom(
                    http_host=url.replace("http://", "").replace("https://", ""),
                    http_port=8080,
                    http_secure=False,
                    auth_credentials=weaviate.auth.AuthApiKey(api_key)
                )
            else:
                self.client = weaviate.connect_to_custom(
                    http_host=url.replace("http://", "").replace("https://", ""),
                    http_port=8080,
                    http_secure=False
                )
            
            logger.info("Connected to Weaviate")
            self._create_schema()
            
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {str(e)}")
            raise
    
    def _create_schema(self):
        """Create Weaviate schema if it doesn't exist."""
        try:
            # Check if class already exists
            if self.client.collections.exists(self.CLASS_NAME):
                logger.info(f"Schema '{self.CLASS_NAME}' already exists")
                return
            
            # Create collection
            self.client.collections.create(
                name=self.CLASS_NAME,
                vectorizer_config=Configure.Vectorizer.none(),  # We provide embeddings
                properties=[
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="document_name", data_type=DataType.TEXT),
                    Property(name="page_number", data_type=DataType.INT),
                    Property(name="content_type", data_type=DataType.TEXT),
                    Property(name="chunk_index", data_type=DataType.INT),
                    Property(name="total_chunks", data_type=DataType.INT),
                ]
            )
            
            logger.info(f"Created schema '{self.CLASS_NAME}'")
            
        except Exception as e:
            logger.error(f"Error creating schema: {str(e)}")
            raise
    
    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray):
        """
        Add document chunks with embeddings to Weaviate.
        
        Args:
            chunks: List of chunk dictionaries with content and metadata
            embeddings: Numpy array of embeddings
        """
        try:
            collection = self.client.collections.get(self.CLASS_NAME)
            
            # Prepare data objects
            objects_to_insert = []
            for chunk, embedding in zip(chunks, embeddings):
                data_object = {
                    "content": chunk['content'],
                    "document_name": chunk['metadata']['document_name'],
                    "page_number": chunk['metadata'].get('page_number', 0) or 0,
                    "content_type": chunk['metadata']['content_type'],
                    "chunk_index": chunk['metadata']['chunk_index'],
                    "total_chunks": chunk['metadata']['total_chunks'],
                }
                objects_to_insert.append({
                    "properties": data_object,
                    "vector": embedding.tolist()
                })
            
            # Batch insert
            with collection.batch.dynamic() as batch:
                for obj in objects_to_insert:
                    batch.add_object(
                        properties=obj["properties"],
                        vector=obj["vector"]
                    )
            
            logger.info(f"Added {len(chunks)} chunks to Weaviate")
            
        except Exception as e:
            logger.error(f"Error adding chunks: {str(e)}")
            raise
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        document_filter: Optional[str] = None,
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in Weaviate.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            document_filter: Optional document name filter
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results with content and metadata
        """
        try:
            collection = self.client.collections.get(self.CLASS_NAME)
            
            # Build query
            query_params = {
                "limit": top_k,
                "return_metadata": MetadataQuery(distance=True)
            }
            
            # Add document filter if provided
            if document_filter:
                response = collection.query.near_vector(
                    near_vector=query_embedding.tolist(),
                    **query_params,
                    filters=weaviate.classes.query.Filter.by_property("document_name").equal(document_filter)
                )
            else:
                response = collection.query.near_vector(
                    near_vector=query_embedding.tolist(),
                    **query_params
                )
            
            # Process results
            results = []
            for obj in response.objects:
                # Convert distance to similarity (cosine similarity = 1 - distance)
                similarity = 1 - obj.metadata.distance
                
                if similarity >= similarity_threshold:
                    results.append({
                        "content": obj.properties["content"],
                        "document_name": obj.properties["document_name"],
                        "page_number": obj.properties["page_number"],
                        "content_type": obj.properties["content_type"],
                        "similarity": similarity
                    })
            
            logger.info(f"Found {len(results)} results above threshold {similarity_threshold}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            raise
    
    def delete_document(self, document_name: str):
        """Delete all chunks for a specific document."""
        try:
            collection = self.client.collections.get(self.CLASS_NAME)
            
            collection.data.delete_many(
                where=weaviate.classes.query.Filter.by_property("document_name").equal(document_name)
            )
            
            logger.info(f"Deleted all chunks for document: {document_name}")
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def close(self):
        """Close Weaviate connection."""
        self.client.close()
        logger.info("Closed Weaviate connection")
