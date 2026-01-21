import io
from typing import List, Dict, Any
from pypdf import PdfReader
from PIL import Image
import pytesseract
import tabula
import logging

logger = logging.getLogger(__name__)


class DocumentExtractor:
    """Extract text, tables, and images from PDF documents."""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract all content from a PDF file.
        
        Returns:
            List of content blocks with metadata
        """
        content_blocks = []
        
        try:
            # Extract text
            text_blocks = self._extract_text(pdf_path)
            content_blocks.extend(text_blocks)
            
            # Extract tables
            table_blocks = self._extract_tables(pdf_path)
            content_blocks.extend(table_blocks)
            
            # Extract images with OCR
            image_blocks = self._extract_images(pdf_path)
            content_blocks.extend(image_blocks)
            
            logger.info(f"Extracted {len(content_blocks)} content blocks from {pdf_path}")
            
        except Exception as e:
            logger.error(f"Error extracting from PDF: {str(e)}")
            raise
        
        return content_blocks
    
    def _extract_text(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text content from PDF."""
        text_blocks = []
        
        try:
            reader = PdfReader(pdf_path)
            
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                
                if text and text.strip():
                    text_blocks.append({
                        'content': text.strip(),
                        'content_type': 'text',
                        'page_number': page_num,
                        'metadata': {
                            'extraction_method': 'pypdf'
                        }
                    })
            
            logger.info(f"Extracted text from {len(text_blocks)} pages")
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
        
        return text_blocks
    
    def _extract_tables(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF and convert to markdown."""
        table_blocks = []
        
        try:
            # Read all tables from PDF
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            
            for idx, table_df in enumerate(tables):
                if not table_df.empty:
                    # Convert table to markdown format
                    table_markdown = table_df.to_markdown(index=False)
                    
                    table_blocks.append({
                        'content': table_markdown,
                        'content_type': 'table',
                        'page_number': None,  # tabula doesn't always provide page numbers
                        'metadata': {
                            'extraction_method': 'tabula',
                            'table_index': idx,
                            'rows': len(table_df),
                            'columns': len(table_df.columns)
                        }
                    })
            
            logger.info(f"Extracted {len(table_blocks)} tables")
            
        except Exception as e:
            logger.warning(f"Error extracting tables (this is normal if no tables exist): {str(e)}")
        
        return table_blocks
    
    def _extract_images(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract images from PDF and perform OCR."""
        image_blocks = []
        
        try:
            reader = PdfReader(pdf_path)
            
            for page_num, page in enumerate(reader.pages, start=1):
                if '/XObject' in page['/Resources']:
                    xobjects = page['/Resources']['/XObject'].get_object()
                    
                    for obj_name in xobjects:
                        obj = xobjects[obj_name]
                        
                        if obj['/Subtype'] == '/Image':
                            try:
                                # Extract image data
                                size = (obj['/Width'], obj['/Height'])
                                data = obj.get_data()
                                
                                # Convert to PIL Image
                                image = Image.open(io.BytesIO(data))
                                
                                # Perform OCR
                                ocr_text = pytesseract.image_to_string(image)
                                
                                # Only keep if OCR extracted meaningful text
                                if ocr_text and len(ocr_text.strip()) > 20:
                                    image_blocks.append({
                                        'content': ocr_text.strip(),
                                        'content_type': 'image',
                                        'page_number': page_num,
                                        'metadata': {
                                            'extraction_method': 'pytesseract',
                                            'image_size': size
                                        }
                                    })
                            
                            except Exception as e:
                                logger.debug(f"Could not process image on page {page_num}: {str(e)}")
                                continue
            
            logger.info(f"Extracted text from {len(image_blocks)} images")
            
        except Exception as e:
            logger.warning(f"Error extracting images: {str(e)}")
        
        return image_blocks
