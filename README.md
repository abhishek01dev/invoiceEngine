# Invoice OCR Parser Microservice

A lightweight, production-ready OCR-based microservice that processes invoices (PDFs and images), extracts structured data, and returns it in a predefined JSON format.

## Features

- ✅ Extract text from PDF, JPG, PNG files
- ✅ Handle both text-based and scanned documents
- ✅ Rule-based field extraction (no AI/LLM)
- ✅ Low memory and CPU usage
- ✅ Docker support
- ✅ RESTful API with FastAPI
- ✅ Health check endpoints

## Extracted Fields

| Field | Matched Keywords |
|---|---|
| `invoice_no` | Invoice No/Number, Bill No/Number, Ref No, Reference No |
| `secondary_invoice_date` | Invoice Date, Bill Date, Date, Dated |
| `end_customer_name` | Customer Name, Client Name, Bill To, Sold To |
| `end_customer_contact_number` | Phone, Mobile, Contact |
| `end_customer_address` | Address, Billing Address, Ship To |
| `state` | All 28 Indian states + 8 UTs + US states |
| `city` | Extracted from address context |

## Tech Stack

- **Framework**: FastAPI
- **OCR**: Tesseract (pytesseract)
- **PDF Processing**: PyMuPDF, pdfplumber, pdf2image
- **Image Processing**: OpenCV, Pillow
- **Parsing**: Regex + rule-based heuristics

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/parse-invoice` | Upload and parse an invoice |
| `GET` | `/health` | Health check |
| `GET` | `/` | Service info |

## Installation

### Prerequisites

- Python 3.11+
- Tesseract OCR
- Docker (optional)

### Local Setup

```bash
git clone <repository-url>
cd invoice-engine
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker (Development)

```bash
docker-compose up --build
```

## Production Deployment

This service is designed to be lightweight and production-ready. 

### 1. Using Docker Compose (Recommended)

For production, ensure your `.env` file is properly configured with `DEBUG=False` and appropriate volume mappings.

```bash
# Build and run in detached mode
docker-compose up -d --build
```

### 2. Manual Production Setup (Gunicorn + Uvicorn)

If you are not using Docker, you should run the FastAPI application using Gunicorn with Uvicorn workers for better concurrency and stability in production.

1. **Install Gunicorn**:
   ```bash
   pip install gunicorn
   ```

2. **Run the server**:
   ```bash
   gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
   *(Rule of thumb: number of workers = `(2 x $num_cores) + 1`)*

### 3. Environment Variables for Production

Ensure you have a `.env` file in your root directory based on `.env.example`:

- `DEBUG=False` (Crucial for security and performance)
- `MAX_FILE_SIZE_MB=10` (Adjust based on your requirements to prevent DoS via large files)
- `MAX_WORKERS=4`

### 4. Reverse Proxy (Nginx)

It is highly recommended to place Nginx or another reverse proxy in front of the API to handle SSL/TLS termination, rate limiting, and caching.

Example Nginx Block:
```nginx
server {
    listen 80;
    server_name invoice.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Usage

```bash
curl -X POST "http://localhost:8000/parse-invoice" \
  -F "file=@invoice.pdf"
```

Response:
```json
{
  "success": true,
  "message": "Invoice parsed successfully",
  "data": {
    "invoice_no": "INV-2024-001",
    "secondary_invoice_date": "15/03/2024",
    "end_customer_name": "Acme Corp",
    "end_customer_contact_number": "+919876543210",
    "end_customer_address": "123 Main St, Mumbai",
    "state": "Maharashtra",
    "city": "Mumbai"
  },
  "processing_time": 1.23
}
```

## Testing

```bash
python -m pytest tests/ -v
```