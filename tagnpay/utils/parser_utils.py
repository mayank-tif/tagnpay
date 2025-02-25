import re
from datetime import datetime

def parse_bill_text(ocr_text):
    """
    Parse the extracted text to find relevant bill details.
    :param ocr_text: Raw text from OCR.
    :return: Parsed data as a dictionary.
    """
    # Example regex for extracting details (adjust based on your bill format)
    items = []
    total = None
    bill_date = extract_date_time(ocr_text)
    if bill_date == None:
        bill_date = extract_date(ocr_text)

    bill_number = extract_invoice_number(ocr_text)
    bill_amount=extract_total_amount(ocr_text)

    lines = ocr_text.split("\n")
    for line in lines:
        # Example format: "ItemName Quantity Price"
        match = re.match(r"(.+)\s+(\d+)\s+([\d\.]+)", line)
        """ 
        if match:
            items.append({
                "item": match.group(1).strip(),
                "quantity": int(match.group(2)),
                "price": float(match.group(3)),
            }) 
        """
        
        
        # Example format: "Total: 123.45"
        """ 
        if "total" in line.lower():
            total_match = re.search(r"[\d\.]+", line)
            if total_match:
                total = float(total_match.group(0)) 
        """

    return {"total": bill_amount, "billdate": bill_date, "bill_number": bill_number}


def extract_date(ocr_text):
    """
    Extracts the bill date from OCR-extracted text.
    :param ocr_text: Raw text extracted from the bill.
    :return: Date as a string in ISO format (YYYY-MM-DD), or None if not found.
    """
    # Define regex patterns for common date formats
    date_patterns = [
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',       # Matches DD/MM/YYYY, MM-DD-YYYY, etc.
        r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',         # Matches YYYY/MM/DD
        r'\b(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\b',     # Matches 14 Nov 2023
    ]

    for pattern in date_patterns:
        match = re.search(pattern, ocr_text)
        if match:
            date_str = match.group(1)
            # Try to parse the date to standardize the format
            for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y-%m-%d', '%d %b %Y'):
                try:
                    return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue

    return None

def extract_date_time(ocr_text):
    """
    Extracts the bill date and time from OCR-extracted text.
    :param ocr_text: Raw text extracted from the bill.
    :return: Date and time as a string in ISO format (YYYY-MM-DD HH:MM:SS), or None if not found.
    """
    # Define regex patterns for date and time
    date_time_patterns = [
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s+\d{1,2}:\d{2}(?:\s*[APap][Mm])?)\b',  # Matches DD/MM/YYYY HH:MM AM/PM
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s+\d{1,2}:\d{2})\b',                    # Matches DD/MM/YYYY HH:MM
        r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2}\s+\d{1,2}:\d{2})\b',                      # Matches YYYY/MM/DD HH:MM
        r'\b(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4},?\s+\d{1,2}:\d{2}(?:\s*[APap][Mm])?)\b',  # Matches 14 Nov 2023, 11:45 AM
    ]

    for pattern in date_time_patterns:
        match = re.search(pattern, ocr_text)
        if match:
            date_time_str = match.group(1)
            # Try to parse the date-time to standardize the format
            for fmt in ('%d/%m/%Y %I:%M %p', '%d-%m-%Y %H:%M', '%Y/%m/%d %H:%M', '%d %b %Y, %I:%M %p'):
                try:
                    return datetime.strptime(date_time_str, fmt).strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue

    return None


def extract_invoice_number(ocr_text):
    """
    Extracts the invoice or bill number from OCR-extracted text.
    :param ocr_text: Raw text extracted from the bill.
    :return: Invoice number as a string, or None if not found.
    """
    # Define regex patterns to search for invoice/bill number
    patterns = [
        r'\b(?:Invoice Number|InvoiceNo|Bill No|Bill Number|Invoice|Order No|Tinvoteetio)\s*[:\-]?\s*([A-Za-z0-9\-]+)\b',  # Matches "Invoice Number: 12345"
        r'\b(?:INV|BILL)\-?(\d+)\b',  # Matches "INV12345" or "BILL-12345"
    ]

    for pattern in patterns:
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            return match.group(1)  # Return the matched invoice/bill number

    return None


def extract_total_amount(ocr_text):
    """
    Extracts the total amount from OCR-extracted text.
    :param ocr_text: Raw text extracted from the bill.
    :return: Total amount as a float, or None if not found.
    """
    # Define regex patterns to search for total amount
    patterns = [
        r'\b(?:Bill Total|Net Bill Amount|Total|Grand Total|Amount Due|Amount Paid|Balance)\s*[:\-]?\s*([\$₹€]?\s*[0-9,]+(?:\.[0-9]{1,2})?)\b',  # Matches "Total: 1234.56"
        r'\b(?:Net Bill Amount|Total|Grand Total|Amount Due|Amount Paid|Balance|Bill Total)?\s*([\$₹€]?\s*[0-9,]+(?:\.[0-9]{1,2})?)\b',
        r'\b([\$₹€]?\s*[0-9,]+(?:\.[0-9]{1,2})?)\b\s*(?:Total|Grand Total|Amount Due|Balance)',  # Matches "1234.56 Total"
    ]

    for pattern in patterns:
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            # Clean up the matched amount (remove currency symbols, spaces, and commas)
            amount = match.group(1).replace(',', '').replace('$', '').replace('₹', '').replace('€', '').strip()
            try:
                return float(amount)  # Convert to float
            except ValueError:
                continue

    return None