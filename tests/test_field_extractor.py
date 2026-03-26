import pytest
from app.parser.field_extractor import FieldExtractor


@pytest.fixture
def extractor():
    return FieldExtractor()


# ---- Sample invoice texts for testing ----

SAMPLE_INVOICE_BASIC = """
INVOICE
Invoice No: INV-2024-0042
Invoice Date: 15/03/2024

Bill To:
Acme Corporation
Phone: +91 98765 43210

Address:
123 MG Road, Suite 400
Mumbai, Maharashtra 400001
India
"""

SAMPLE_INVOICE_BILL = """
TAX INVOICE
Bill Number: BN-987654
Bill Date: 2024-01-20

Sold To:
Rajesh Kumar
Mobile: 9876543210

Billing Address:
45 Park Street
Kolkata, West Bengal 700016
"""

SAMPLE_INVOICE_REF = """
Ref No: REF/2024/001
Dated: 10-05-2024

Customer Name: Priya Sharma
Contact: +919123456789

Ship To:
B-12, Industrial Area
Sector 5, Noida
Uttar Pradesh 201301
"""

SAMPLE_INVOICE_MINIMAL = """
Some random document text
with no invoice fields at all.
Just regular text.
"""


# ---- Invoice Number Tests ----

class TestInvoiceNo:
    def test_invoice_no(self, extractor):
        result = extractor.extract_invoice_no(SAMPLE_INVOICE_BASIC)
        assert result == "INV-2024-0042"

    def test_bill_number(self, extractor):
        result = extractor.extract_invoice_no(SAMPLE_INVOICE_BILL)
        assert result == "BN-987654"

    def test_ref_no(self, extractor):
        result = extractor.extract_invoice_no(SAMPLE_INVOICE_REF)
        assert result == "REF/2024/001"

    def test_no_invoice_no(self, extractor):
        result = extractor.extract_invoice_no(SAMPLE_INVOICE_MINIMAL)
        assert result is None


# ---- Date Tests ----

class TestDate:
    def test_dd_mm_yyyy(self, extractor):
        result = extractor.extract_date(SAMPLE_INVOICE_BASIC)
        assert result == "15/03/2024"

    def test_yyyy_mm_dd(self, extractor):
        result = extractor.extract_date(SAMPLE_INVOICE_BILL)
        assert result == "2024-01-20"

    def test_dd_mm_yyyy_dash(self, extractor):
        result = extractor.extract_date(SAMPLE_INVOICE_REF)
        assert result == "10-05-2024"

    def test_no_date(self, extractor):
        result = extractor.extract_date(SAMPLE_INVOICE_MINIMAL)
        assert result is None


# ---- Customer Name Tests ----

class TestCustomerName:
    def test_bill_to(self, extractor):
        result = extractor.extract_customer_name(SAMPLE_INVOICE_BASIC)
        assert result == "Acme Corporation"

    def test_sold_to(self, extractor):
        result = extractor.extract_customer_name(SAMPLE_INVOICE_BILL)
        assert result == "Rajesh Kumar"

    def test_customer_name_inline(self, extractor):
        result = extractor.extract_customer_name(SAMPLE_INVOICE_REF)
        assert result == "Priya Sharma"

    def test_no_name(self, extractor):
        result = extractor.extract_customer_name(SAMPLE_INVOICE_MINIMAL)
        assert result is None


# ---- Contact Number Tests ----

class TestContactNumber:
    def test_phone_with_plus91(self, extractor):
        result = extractor.extract_contact_number(SAMPLE_INVOICE_BASIC)
        assert result is not None
        assert "98765" in result

    def test_mobile_10digit(self, extractor):
        result = extractor.extract_contact_number(SAMPLE_INVOICE_BILL)
        assert result is not None
        assert "9876543210" in result

    def test_contact_plus91(self, extractor):
        result = extractor.extract_contact_number(SAMPLE_INVOICE_REF)
        assert result is not None
        assert "9123456789" in result

    def test_no_contact(self, extractor):
        result = extractor.extract_contact_number(SAMPLE_INVOICE_MINIMAL)
        assert result is None


# ---- State Tests ----

class TestState:
    def test_maharashtra(self, extractor):
        result = extractor.extract_state(SAMPLE_INVOICE_BASIC)
        assert result == "Maharashtra"

    def test_west_bengal(self, extractor):
        result = extractor.extract_state(SAMPLE_INVOICE_BILL)
        assert result == "West Bengal"

    def test_uttar_pradesh(self, extractor):
        result = extractor.extract_state(SAMPLE_INVOICE_REF)
        assert result == "Uttar Pradesh"

    def test_no_state(self, extractor):
        result = extractor.extract_state(SAMPLE_INVOICE_MINIMAL)
        assert result is None


# ---- City Tests ----

class TestCity:
    def test_mumbai(self, extractor):
        result = extractor.extract_city(SAMPLE_INVOICE_BASIC)
        assert result is not None
        assert "Mumbai" in result

    def test_kolkata(self, extractor):
        result = extractor.extract_city(SAMPLE_INVOICE_BILL)
        assert result is not None
        assert "Kolkata" in result

    def test_no_city(self, extractor):
        result = extractor.extract_city(SAMPLE_INVOICE_MINIMAL)
        assert result is None


# ---- Address Tests ----

class TestAddress:
    def test_address_block(self, extractor):
        result = extractor.extract_address(SAMPLE_INVOICE_BASIC)
        assert result is not None
        assert "MG Road" in result

    def test_billing_address(self, extractor):
        result = extractor.extract_address(SAMPLE_INVOICE_BILL)
        assert result is not None
        assert "Park Street" in result

    def test_ship_to_address(self, extractor):
        result = extractor.extract_address(SAMPLE_INVOICE_REF)
        assert result is not None
        assert "Industrial Area" in result or "Noida" in result

    def test_no_address(self, extractor):
        result = extractor.extract_address(SAMPLE_INVOICE_MINIMAL)
        assert result is None


# ---- Full Extraction Tests ----

class TestExtractAllFields:
    def test_all_fields_basic(self, extractor):
        result = extractor.extract_all_fields(SAMPLE_INVOICE_BASIC)
        assert result['invoice_no'] is not None
        assert result['secondary_invoice_date'] is not None
        assert result['end_customer_name'] is not None
        assert result['end_customer_contact_number'] is not None
        assert result['state'] is not None

    def test_all_fields_minimal(self, extractor):
        """All fields should be None for a non-invoice document"""
        result = extractor.extract_all_fields(SAMPLE_INVOICE_MINIMAL)
        assert result['invoice_no'] is None
        assert result['secondary_invoice_date'] is None
        assert result['end_customer_name'] is None
        assert result['end_customer_contact_number'] is None
        assert result['state'] is None
        assert result['city'] is None

    def test_returns_all_keys(self, extractor):
        """All required keys must be present in output"""
        result = extractor.extract_all_fields(SAMPLE_INVOICE_BASIC)
        required_keys = [
            'invoice_no', 'secondary_invoice_date', 'end_customer_name',
            'end_customer_contact_number', 'end_customer_address',
            'state', 'city',
        ]
        for key in required_keys:
            assert key in result
