import io
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
from typing import Optional
from app.config import settings
from app.ocr.preprocessor import ImagePreprocessor


class OCRExtractor:
    """Handles text extraction from various file formats"""
    
    def __init__(self):
        # Set Tesseract command path only if provided (otherwise defaults to system PATH)
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        self.preprocessor = ImagePreprocessor()
    
    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """
        Extract text from file based on extension
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename with extension
            
        Returns:
            Extracted text as string
        """
        extension = filename.lower().split('.')[-1]
        
        if extension == 'pdf':
            return self._extract_from_pdf(file_bytes)
        elif extension in ['jpg', 'jpeg', 'png']:
            return self._extract_from_image(file_bytes)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def _extract_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF (handles both text and scanned PDFs)"""
        text = ""
        
        # Try text-based extraction first (faster)
        try:
            text = self._extract_text_pdf(pdf_bytes)
            
            # If very little text extracted, it's likely a scanned PDF
            if len(text.strip()) < 50:
                text = self._extract_scanned_pdf(pdf_bytes)
        except Exception:
            # Fallback to OCR
            text = self._extract_scanned_pdf(pdf_bytes)
        
        return text
    
    def _extract_text_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from text-based PDF using pdfplumber"""
        text = ""
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text
    
    def _extract_scanned_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from scanned PDF using OCR via PyMuPDF"""
        text = ""
        
        # Convert PDF pages to images using PyMuPDF (fitz)
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page in doc:
                pix = page.get_pixmap(dpi=settings.OCR_DPI)
                img_bytes = pix.tobytes("jpeg")
                image = Image.open(io.BytesIO(img_bytes))
                
                page_text = self._ocr_image(image)
                text += page_text + "\n"
        except Exception as e:
            raise RuntimeError(f"Failed to process PDF pages for OCR: {str(e)}")
            
        return text
    
    def _extract_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image file"""
        image = Image.open(io.BytesIO(image_bytes))
        return self._ocr_image(image)
    
    def _ocr_image(self, image: Image.Image) -> str:
        """Perform OCR on a PIL Image"""
        # Preprocess image
        preprocessed = self.preprocessor.preprocess(image, settings.OCR_DPI)
        
        # Perform OCR
        text = pytesseract.image_to_string(
            preprocessed,
            lang=settings.OCR_LANG,
            config='--psm 6'  # Assume uniform block of text
        )
        
        return text