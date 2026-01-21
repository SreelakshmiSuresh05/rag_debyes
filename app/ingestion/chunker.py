from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunk document content with metadata preservation."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_content_blocks(
        self,
        content_blocks: List[Dict[str, Any]],
        document_name: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk content blocks while preserving metadata.
        
        Args:
            content_blocks: List of extracted content blocks
            document_name: Name of the source document
            
        Returns:
            List of chunks with metadata
        """
        all_chunks = []
        
        for block in content_blocks:
            content = block['content']
            content_type = block['content_type']
            page_number = block.get('page_number')
            
            # For tables, don't split - keep them whole
            if content_type == 'table':
                chunk = {
                    'content': content,
                    'metadata': {
                        'document_name': document_name,
                        'page_number': page_number,
                        'content_type': content_type,
                        'chunk_index': 0,
                        'is_table': True,
                        **block.get('metadata', {})
                    }
                }
                all_chunks.append(chunk)
            
            else:
                # Split text and image content
                text_chunks = self.text_splitter.split_text(content)
                
                for idx, chunk_text in enumerate(text_chunks):
                    chunk = {
                        'content': chunk_text,
                        'metadata': {
                            'document_name': document_name,
                            'page_number': page_number,
                            'content_type': content_type,
                            'chunk_index': idx,
                            **block.get('metadata', {})
                        }
                    }
                    all_chunks.append(chunk)
        
        # Add total chunks count to each chunk
        total_chunks = len(all_chunks)
        for chunk in all_chunks:
            chunk['metadata']['total_chunks'] = total_chunks
        
        logger.info(f"Created {total_chunks} chunks from {len(content_blocks)} content blocks")
        
        return all_chunks
