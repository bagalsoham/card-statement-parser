import pdfplumber
import fitz  # PyMuPDF
from typing import Dict, List, Tuple
import structlog

logger = structlog.get_logger()

class PDFLoader:
    """Enhanced PDF extraction with multiple strategies"""
    
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extract raw text from PDF"""
        try:
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
            return full_text
        except Exception as e:
            logger.error("text_extraction_failed", error=str(e))
            raise
    
    @staticmethod
    def extract_tables(pdf_path: str) -> List[List[List[str]]]:
        """Extract tables from PDF"""
        try:
            all_tables = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)
            return all_tables
        except Exception as e:
            logger.warning("table_extraction_failed", error=str(e))
            return []
    
    @staticmethod
    def extract_layout_info(pdf_path: str) -> Dict:
        """Extract layout information using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            layout_info = {
                "page_count": len(doc),
                "pages": []
            }
            
            for page_num, page in enumerate(doc):
                text_dict = page.get_text("dict")
                layout_info["pages"].append({
                    "page_num": page_num,
                    "blocks": text_dict.get("blocks", [])
                })
            
            doc.close()
            return layout_info
        except Exception as e:
            logger.warning("layout_extraction_failed", error=str(e))
            return {"page_count": 0, "pages": []}