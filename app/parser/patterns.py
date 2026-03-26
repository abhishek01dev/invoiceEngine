import re


class InvoicePatterns:
    """Regex patterns and keywords for invoice parsing"""

    # Invoice Number — matches variations like Invoice No, Bill No, Ref No, etc.
    INVOICE_NO = re.compile(
        r'(?:invoice\s*(?:no|number|#)|inv\s*(?:no|number|#)|'
        r'bill\s*(?:no|number|#)|ref(?:erence)?\s*(?:no|number|#))'
        r'[\s.:#-]*([A-Za-z0-9\-_/]+)',
        re.IGNORECASE,
    )

    # Date — matches Invoice Date, Bill Date, Date, Dated
    DATE = re.compile(
        r'(?:invoice\s*date|bill\s*date|dated?)'
        r'[\s.:#-]*'
        r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}'   # DD/MM/YYYY or DD-MM-YYYY
        r'|\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2}'       # YYYY-MM-DD
        r'|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})',      # Month DD, YYYY
        re.IGNORECASE,
    )

    # Customer name indicators (lowercase for comparison)
    CUSTOMER_INDICATORS = [
        'customer name', 'client name',
        'billed to', 'bill to', 'sold to',
        'buyer', 'consignee', 'name :', 'name:'
    ]

    # Address section indicators (lowercase for comparison)
    ADDRESS_INDICATORS = [
        'billing address', 'ship to', 'shipping address',
        'delivery address', 'address',
    ]

    # Phone number extraction patterns — Indian & international
    PHONE_PATTERNS = [
        re.compile(r'(?:phone|mobile|contact|tel|cell|ph\s*:)[\s.:#-]*(\+?\d[\d\s\-().]{8,15}\d)', re.IGNORECASE),
        re.compile(r'\+91[\s\-.]?\d{5}[\s\-.]?\d{5}'),
        re.compile(r'\+?\d{1,3}[\-.\s]?\(?\d{3}\)?[\-.\s]?\d{3}[\-.\s]?\d{4}'),
        re.compile(r'\(?\d{3}\)?[\-.\s]?\d{3}[\-.\s]?\d{4}'),
        re.compile(r'\+?\d{1,3}[\-.\s]?\d{10}')
    ]

    # All 28 Indian states + 8 UTs + common US states (lowercase)
    STATES = [
        # Indian States
        'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar',
        'chhattisgarh', 'goa', 'gujarat', 'haryana',
        'himachal pradesh', 'jharkhand', 'karnataka', 'kerala',
        'madhya pradesh', 'maharashtra', 'manipur', 'meghalaya',
        'mizoram', 'nagaland', 'odisha', 'punjab',
        'rajasthan', 'sikkim', 'tamil nadu', 'telangana',
        'tripura', 'uttar pradesh', 'uttarakhand', 'west bengal', 'jharkhand',
        # Indian Union Territories
        'andaman and nicobar islands', 'chandigarh',
        'dadra and nagar haveli and daman and diu',
        'delhi', 'jammu and kashmir', 'ladakh',
        'lakshadweep', 'puducherry',
        # Common US States
        'california', 'texas', 'new york', 'florida', 'illinois',
        'pennsylvania', 'ohio', 'georgia', 'north carolina', 'michigan',
        'new jersey', 'virginia', 'washington', 'arizona', 'massachusetts',
        'tennessee', 'indiana', 'maryland', 'missouri', 'wisconsin',
        'colorado', 'minnesota', 'south carolina', 'alabama', 'louisiana',
        'kentucky', 'oregon', 'oklahoma', 'connecticut', 'utah',
    ]