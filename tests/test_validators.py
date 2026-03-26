import pytest
from app.utils.validators import validate_file, clean_text


class TestValidateFile:
    def test_valid_pdf(self):
        is_valid, msg = validate_file("invoice.pdf", 1024)
        assert is_valid is True
        assert msg == ""

    def test_valid_jpg(self):
        is_valid, msg = validate_file("scan.jpg", 2048)
        assert is_valid is True

    def test_valid_png(self):
        is_valid, msg = validate_file("image.png", 1024)
        assert is_valid is True

    def test_invalid_extension(self):
        is_valid, msg = validate_file("readme.txt", 100)
        assert is_valid is False
        assert "Invalid file type" in msg

    def test_invalid_docx(self):
        is_valid, msg = validate_file("doc.docx", 100)
        assert is_valid is False

    def test_oversized_file(self):
        # 11 MB should exceed the default 10 MB limit
        is_valid, msg = validate_file("big.pdf", 11 * 1024 * 1024)
        assert is_valid is False
        assert "too large" in msg.lower()

    def test_exactly_max_size(self):
        # Exactly 10 MB should be valid
        is_valid, msg = validate_file("exact.pdf", 10 * 1024 * 1024)
        assert is_valid is True


class TestCleanText:
    def test_preserves_newlines(self):
        text = "Line 1\nLine 2\nLine 3"
        result = clean_text(text)
        assert "\n" in result
        assert "Line 1" in result
        assert "Line 2" in result

    def test_collapses_spaces_within_lines(self):
        text = "Too   many    spaces   here"
        result = clean_text(text)
        assert result == "Too many spaces here"

    def test_removes_blank_lines(self):
        text = "Line 1\n\n\n\nLine 2"
        result = clean_text(text)
        assert result == "Line 1\nLine 2"

    def test_strips_leading_trailing(self):
        text = "  Hello World  \n  Another Line  "
        result = clean_text(text)
        assert "Hello World" in result
        assert "Another Line" in result

    def test_empty_text(self):
        result = clean_text("")
        assert result == ""

    def test_multiline_address_preserved(self):
        text = "Address:\n123 MG Road\nMumbai, Maharashtra\n400001"
        result = clean_text(text)
        lines = result.split("\n")
        assert len(lines) == 4
