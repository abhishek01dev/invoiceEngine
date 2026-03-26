import time
import traceback
from io import BytesIO
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.models import UploadResponse, InvoiceData, HealthResponse
from app.ocr.extractor import OCRExtractor
from app.parser.field_extractor import FieldExtractor
from app.utils.validators import validate_file, clean_text
import pytesseract


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Tesseract path: {settings.TESSERACT_CMD}")
    yield
    # Shutdown
    print("Shutting down service...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Lightweight OCR-based invoice parser microservice",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ocr_extractor = OCRExtractor()
field_extractor = FieldExtractor()


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(
        status="online",
        service=settings.APP_NAME,
        version=settings.APP_VERSION
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION
    )


@app.post("/parse-invoice", response_model=UploadResponse)
async def parse_invoice(file: UploadFile = File(...)):
    """
    Upload and parse invoice file
    
    Accepts: PDF, JPG, JPEG, PNG
    Returns: Structured JSON with extracted invoice fields
    """
    start_time = time.time()
    
    try:
        # Read file
        file_bytes = await file.read()
        file_size = len(file_bytes)
        
        # Validate file
        is_valid, error_msg = validate_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Extract text using OCR
        try:
            raw_text = ocr_extractor.extract_text(file_bytes, file.filename)
        except pytesseract.TesseractNotFoundError:
            raise HTTPException(
                status_code=500,
                detail="Tesseract-OCR is not installed or not in your PATH. Please install Tesseract (e.g. via 'apt-get install tesseract-ocr' or Windows installer) and ensure it's in your PATH, or set TESSERACT_CMD in the .env file."
            )
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract text from file: {str(e)}"
            )
        
        # Clean text
        cleaned_text = clean_text(raw_text)
        
        if not cleaned_text or len(cleaned_text) < 10:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the document"
            )
        
        # Extract fields
        try:
            extracted_data = field_extractor.extract_all_fields(cleaned_text)
        except Exception as e:
            print(f"Parsing Error: {str(e)}")
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse invoice: {str(e)}"
            )
        
        # Create response
        invoice_data = InvoiceData(**extracted_data)
        processing_time = round(time.time() - start_time, 2)
        
        return UploadResponse(
            success=True,
            message="Invoice parsed successfully",
            data=invoice_data,
            processing_time=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get("/api/info")
async def api_info():
    """API information"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "health": "/health",
            "parse_invoice": "/parse-invoice (POST)",
        },
        "supported_formats": settings.ALLOWED_EXTENSIONS,
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )