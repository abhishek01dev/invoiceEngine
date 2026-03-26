import re
from typing import Dict, Optional
from app.parser.patterns import InvoicePatterns


class FieldExtractor:
    """Extracts structured fields from unstructured invoice text"""

    def __init__(self):
        self.patterns = InvoicePatterns()

    def extract_all_fields(self, text: str) -> Dict:
        """Extract all fields from invoice text"""
        return {
            'invoice_no': self.extract_invoice_no(text),
            'secondary_invoice_date': self.extract_date(text),
            'end_customer_name': self.extract_customer_name(text),
            'end_customer_contact_number': self.extract_contact_number(text),
            'end_customer_address': self.extract_address(text),
            'state': self.extract_state(text),
            'city': self.extract_city(text),
        }

    def extract_invoice_no(self, text: str) -> Optional[str]:
        """Extract invoice/bill/reference number"""
        match = self.patterns.INVOICE_NO.search(text)
        if match:
            value = match.group(1).strip() if match.group(1) else match.group(0).strip()
            # Clean trailing punctuation
            return re.sub(r'[:\s]+$', '', value)
        return None

    def extract_date(self, text: str) -> Optional[str]:
        """Extract invoice/bill date"""
        match = self.patterns.DATE.search(text)
        if match:
            return match.group(1).strip()
        # Fallback: find any standalone date pattern in the text
        fallback = re.search(
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2})',
            text,
        )
        return fallback.group(1).strip() if fallback else None

    def extract_customer_name(self, text: str) -> Optional[str]:
        """Extract customer/client name from labeled sections"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(ind in line_lower for ind in self.patterns.CUSTOMER_INDICATORS):
                # Try inline value after colon
                if ':' in line:
                    value = line.split(':', 1)[-1].strip()
                    # If the value contains another label (like Delivery Address:), split it
                    if 'address' in value.lower() and ':' in value:
                        value = re.split(r'(?i)\b\w*\s*address\b', value)[0].strip()
                        # Clean up trailing punctuation
                        value = re.sub(r'[:\|\-]+$', '', value).strip()
                    if len(value) > 2 and 'details of' not in value.lower():
                        return value
                # Try next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # Skip if next line is another label
                    if not any(ind in next_line.lower() for ind in
                               self.patterns.CUSTOMER_INDICATORS + self.patterns.ADDRESS_INDICATORS):
                        if 'details of' not in next_line.lower():
                            return next_line
        return None

    def extract_contact_number(self, text: str) -> Optional[str]:
        """Extract phone/mobile/contact number"""
        for pattern in self.patterns.PHONE_PATTERNS:
            match = pattern.search(text)
            if match:
                # Use captured group if available, else full match
                phone = match.group(1) if match.lastindex else match.group(0)
                phone = re.sub(r'[^\d+]', '', phone)
                # Validate length (at least 10 digits)
                digits_only = re.sub(r'\D', '', phone)
                if len(digits_only) >= 10:
                    return phone
        return None

    def extract_address(self, text: str) -> Optional[str]:
        """Extract address from labeled address sections"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # First try ADDRESS_INDICATORS
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(ind in line_lower for ind in self.patterns.ADDRESS_INDICATORS):
                # If the indicator line itself has inline content after colon
                if ':' in line:
                    inline = line.split(':', 1)[-1].strip()
                    if len(inline) > 5:
                        address_parts = [inline]
                        for j in range(i + 1, min(i + 4, len(lines))):
                            candidate = lines[j]
                            if self._is_address_line(candidate):
                                address_parts.append(candidate)
                            else:
                                break
                        return ', '.join(address_parts)

                # Collect lines below the indicator
                address_parts = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    candidate = lines[j]
                    if self._is_address_line(candidate):
                        address_parts.append(candidate)
                    else:
                        break
                if address_parts:
                    return ', '.join(address_parts)

        # Fallback: try CUSTOMER_INDICATORS (address often follows customer block)
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(ind in line_lower for ind in self.patterns.CUSTOMER_INDICATORS):
                start = i + 2  # skip name line
                address_parts = []
                for j in range(start, min(start + 4, len(lines))):
                    candidate = lines[j]
                    if self._is_address_line(candidate):
                        address_parts.append(candidate)
                    else:
                        break
                if address_parts:
                    return ', '.join(address_parts)

        return None

    @staticmethod
    def _is_address_line(line: str) -> bool:
        """Heuristic: check if a line looks like part of an address"""
        if len(line) < 3:
            return False
        if re.match(r'^\d+$', line):
            return False
        if '@' in line:
            return False
        lower = line.lower()
        stop_words = ['invoice', 'bill no', 'date', 'total', 'amount',
                       'qty', 'quantity', 'description', 'sr no', 'item', 'a/c', 'ifsc']
        return not any(sw in lower for sw in stop_words)

    def extract_state(self, text: str) -> Optional[str]:
        """Extract state from text using keyword matching"""
        text_lower = text.lower()
        
        # In a side-by-side or flattened layout, try to find the state near the "billed to/shipped to"
        # First check the address string specifically if we can
        address = self.extract_address(text)
        if address:
            address_lower = address.lower()
            sorted_states = sorted(self.patterns.STATES, key=lambda s: len(s), reverse=True)
            for state in sorted_states:
                if re.search(r'\b' + re.escape(state) + r'\b', address_lower):
                    return state.title()

        # Fallback to whole text
        sorted_states = sorted(self.patterns.STATES, key=lambda s: len(s), reverse=True)
        for state in sorted_states:
            if re.search(r'\b' + re.escape(state) + r'\b', text_lower):
                return state.title()
        return None

    def extract_city(self, text: str) -> Optional[str]:
        """Extract city — typically appears before state in address lines"""
        state = self.extract_state(text)
        if not state:
            return None

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines:
            if state.lower() in line.lower():
                # Try comma-separated: "City, State"
                parts = [p.strip() for p in line.split(',')]
                for idx, part in enumerate(parts):
                    if state.lower() in part.lower() and idx > 0:
                        city_candidate = parts[idx - 1]
                        # Clean up pincode or extra text
                        city_candidate = re.sub(r'\d{5,6}', '', city_candidate).strip()
                        if len(city_candidate) > 1:
                            return city_candidate.title()
                # Try dash-separated: "City - State"
                parts = [p.strip() for p in line.split('-')]
                for idx, part in enumerate(parts):
                    if state.lower() in part.lower() and idx > 0:
                        city_candidate = parts[idx - 1].strip()
                        if len(city_candidate) > 1:
                            return city_candidate.title()
        return None