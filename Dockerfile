FROM python:3.11-alpine

# Install system dependencies including Tesseract and OpenCV
# Using Alpine system packages for heavy libs minimizes compile time and size
RUN apk update && apk add --no-cache \
    tesseract-ocr \
    tesseract-ocr-data-eng \
    poppler-utils \
    opencv \
    py3-opencv \
    zlib-dev \
    jpeg-dev \
    gcc \
    musl-dev \
    linux-headers

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Filter out opencv-headless from pip since we use the Alpine py3-opencv package
RUN grep -v "opencv-python-headless" requirements.txt > req_alpine.txt && \
    pip install --no-cache-dir -r req_alpine.txt

# Copy application code
COPY app/ ./app/

# Create necessary directories
RUN mkdir -p /tmp/invoice_uploads

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TESSERACT_CMD=/usr/bin/tesseract

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]