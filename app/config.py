import os
from pathlib import Path
from typing import Optional
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = os.getenv("APP_NAME", "Invoice OCR Parser Service")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # File Upload Settings
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", 10))
    ALLOWED_EXTENSIONS: str = os.getenv("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png")
    
    # OCR Settings
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe" if os.name == 'nt' else "/usr/bin/tesseract")
    OCR_LANG: str = os.getenv("OCR_LANG", "eng")
    OCR_DPI: int = int(os.getenv("OCR_DPI", 300))
    
    # Processing Settings
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", 2))
    PROCESSING_TIMEOUT: int = int(os.getenv("PROCESSING_TIMEOUT", 30))
    
    # Directories
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "tmp", "invoice_uploads")))
    
    class Config:
        case_sensitive = True


settings = Settings()

# Create upload directory if it doesn't exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  