import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data


def test_api_info():
    """Test API info endpoint"""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "supported_formats" in data
    assert "parse_invoice" in data["endpoints"]


def test_parse_invoice_invalid_file():
    """Test upload with invalid file type"""
    files = {"file": ("test.txt", b"test content", "text/plain")}
    response = client.post("/parse-invoice", files=files)
    assert response.status_code == 400


def test_upload_resume_returns_404():
    """Old /upload-resume endpoint must not exist"""
    files = {"file": ("test.pdf", b"test content", "application/pdf")}
    response = client.post("/upload-resume", files=files)
    assert response.status_code in [404, 405]


def test_parse_invoice_oversized_file():
    """Test upload with file exceeding max size"""
    # Create a fake file larger than 10MB
    large_content = b"x" * (11 * 1024 * 1024)
    files = {"file": ("big.pdf", large_content, "application/pdf")}
    response = client.post("/parse-invoice", files=files)
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()