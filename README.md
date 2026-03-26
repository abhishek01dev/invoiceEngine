<div align="center">
  
# 🧾 InvoiceEngine
**A Lightweight, Production-Ready OCR Parser Microservice**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker Support](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

*Extract structured data from invoices (PDFs and images) in milliseconds securely, and efficiently.*

[Getting Started](#-getting-started) •
[Features](#-features) •
[Tech Stack](#-tech-stack) •
[API Docs](#-api-endpoints) •
[Deployment](#-production-deployment) •
[Contributing](#-contributing)

</div>

---

**InvoiceEngine** is a lightweight microservice designed to process invoices, extract relevant fields, and return deterministic structured JSON data. By avoiding heavy AI/LLM dependencies, it runs efficiently with low memory and CPU footprint, making it perfect for rapid scanning constraints.

## ✨ Features

- **Multi-Format Support**: Extract text seamlessly from PDF, JPG, JPEG, and PNG files.
- **Versatile Parsing**: Handle both native text-based PDFs and scanned document images.
- **Rule-based Extraction**: Deterministic extraction (no AI/LLM hallucinations).
- **Resource Efficient**: Low memory and CPU usage compared to deep-learning approaches.
- **Fast & Modern API**: Built on the blazingly fast FastAPI framework.
- **Ready for Scale**: Dockerized setup, health checks, and production-ready ASGI configuration.

---

## 📦 What gets extracted?

| Field | Description / Matched Keywords |
|---|---|
| 🆔 `invoice_no` | Invoice No/Number, Bill No/Number, Ref No, Reference No |
| 📅 `secondary_invoice_date` | Invoice Date, Bill Date, Date, Dated |
| 👤 `end_customer_name` | Customer Name, Client Name, Bill To, Sold To |
| 📞 `end_customer_contact_number` | Phone, Mobile, Contact |
| 📍 `end_customer_address` | Address, Billing Address, Ship To |
| 🏛️ `state` | All 28 Indian states + 8 UTs + US states |
| 🏙️ `city` | Extracted from address context dynamically |

---

## 🏗️ Tech Stack

- **Framework**: FastAPI, Uvicorn
- **OCR Engine**: Tesseract OCR (`pytesseract`)
- **PDF Processing**: PyMuPDF, `pdfplumber`, `pdf2image`
- **Image Processing**: OpenCV, Pillow
- **Data Parsing**: Advanced Regex + rule-based heuristics

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Tesseract OCR engine installed locally
- Docker (optional but highly recommended)

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/abhishek01dev/invoiceEngine.git
   cd invoiceEngine
   ```

2. **Set up a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and supply necessary settings like TESSERACT_CMD path
   ```

4. **Run the server natively:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Docker Setup (Development)

The fastest way to get started without dealing with manual OCR engine setups:

```bash
docker-compose up --build
```
*The service will be instantly available on `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.*

---

## 📖 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/parse-invoice` | Upload and parse an invoice document (multipart/form-data) |
| `GET`  | `/health` | Application health check status |
| `GET`  | `/api/info` | API metadata and configuration info |
| `GET`  | `/` | Service root and basic info |

### Usage Example: Parse Invoice

```bash
curl -X POST "http://localhost:8000/parse-invoice" \
  -F "file=@sample_invoice.pdf"
```

**JSON Response:**
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

---

## 🛳️ Production Deployment

This service is engineered to be lightweight and production-ready.

### 1. Using Docker Compose (Recommended)

Ensure your `.env` file is properly configured (`DEBUG=False`).

```bash
# Build and run the optimized production container in detached mode
docker-compose up -d --build
```

### 2. Manual Production Setup (Gunicorn + Uvicorn)

To run the FastAPI application on bare metal, use Gunicorn with Uvicorn workers for high concurrency.

1. Install Gunicorn: `pip install gunicorn`
2. Run the server:
   ```bash
   gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
   *(Rule of thumb: number of workers = `(2 x $num_cores) + 1`)*

### 3. Environment Variables (.env)

Critical variables for production performance and security:
```env
APP_NAME=Invoice OCR Parser Service
DEBUG=False
MAX_FILE_SIZE_MB=10 # Prevents DoS attacks from large files
MAX_WORKERS=4
TESSERACT_CMD=/usr/bin/tesseract
```

### 4. Reverse Proxying (Nginx Example)

It is highly recommended to place Nginx or another reverse proxy in front of the API to handle SSL/TLS termination and general rate-limiting.

```nginx
server {
    listen 80;
    server_name api.invoiceengine.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🧪 Testing

Run tests locally using Pytest to ensure everything works flawlessly:

```bash
python -m pytest tests/ -v
```

---

## 🤝 Contributing

We welcome contributions! As an open-source project, your help makes this tool better for everyone.

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally.
3. **Commit your changes**: Make your features, bug fixes, or documentation updates.
4. **Submit a Pull Request**: Detail the changes and why they are valuable.

If you encounter a bug or have a feature request, please [open an issue](https://github.com/abhishek01dev/invoiceEngine/issues).

---

<div align="center">
  <b>Built with ❤️ by the Open Source Community.</b>
</div>