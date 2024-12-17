import os
import re
from pdf2image import convert_from_path
import pytesseract
import pandas as pd
import tabula

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Poppler path (adjust based on installation)
poppler_path = r"C:\Program Files (x86)\poppler-24.08.0\Library\bin"
os.environ["PATH"] += os.pathsep + poppler_path

def extract_text_from_pdf(pdf_path, pages):
    """Extract text from specific pages of the PDF using OCR."""
    text = ""
    images = convert_from_path(pdf_path, first_page=pages[0] + 1, last_page=pages[-1] + 1, dpi=300)
    for image in images:
        page_text = pytesseract.image_to_string(image, lang="eng")
        text += page_text + "\n"
    return text

def clean_text(text):
    """Clean the extracted text by removing unnecessary characters."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s\.\:\%\$\n]", "", text)
    cleaned = re.sub(r"\n{2,}", "\n", cleaned)  # Remove extra newlines
    return cleaned.strip()

def parse_education_data(text):
    """Parse the educational data such as degree, unemployment rate, and median earnings."""
    data = {}
    degree_patterns = [
        (r"Doctoral degree.*?(\d+\.\d)%.*?(\$\d+)", "Doctoral degree"),
        (r"Professional degree.*?(\d+\.\d)%.*?(\$\d+)", "Professional degree"),
        (r"Masters degree.*?(\d+\.\d)%.*?(\$\d+)", "Masters degree"),
        (r"Bachelors degree.*?(\d+\.\d)%.*?(\$\d+)", "Bachelors degree"),
        (r"Associates degree.*?(\d+\.\d)%.*?(\$\d+)", "Associates degree"),
        (r"Some college no degree.*?(\d+\.\d)%.*?(\$\d+)", "Some college no degree"),
        (r"High school diploma.*?(\d+\.\d)%.*?(\$\d+)", "High school diploma"),
        (r"Less than a high school diploma.*?(\d+\.\d)%.*?(\$\d+)", "Less than high school"),
    ]
    
    for pattern, degree in degree_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            data[degree] = {"Unemployment Rate": match.group(1), "Median Earnings": match.group(2)}
    
    return data

def extract_pdf_table(pdf_path, pages):
    """Extract tables from the PDF using tabula."""
    try:
        tables = tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True)
        return tables
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []

def process_pdf(pdf_path):
    """Process the PDF: extract tables, text, and parse educational data."""
    
    # Extract tables from specific pages
    tables_page_6 = extract_pdf_table(pdf_path, pages="6")
    print_tables(tables_page_6, page=6)

    # Extract and process text from page 2
    text_page_2 = extract_text_from_pdf(pdf_path, pages=[1])  # Page 2 (0-based index)
    cleaned_text_page_2 = clean_text(text_page_2)
    educational_data_page_2 = parse_education_data(cleaned_text_page_2)
    print_educational_data(educational_data_page_2, page=2)

    # Extract and process text from page 6
    text_page_6 = extract_text_from_pdf(pdf_path, pages=[5])  # Page 6 (0-based index)
    cleaned_text_page_6 = clean_text(text_page_6)
    educational_data_page_6 = parse_education_data(cleaned_text_page_6)
    print_educational_data(educational_data_page_6, page=6)

def print_tables(tables, page):
    """Display tables extracted from a given page."""
    if tables:
        print(f"\nExtracted Tables from Page {page}:")
        for idx, table in enumerate(tables):
            print(f"\nTable {idx + 1}:")
            print(table)
    else:
        print(f"No tables found on page {page}.")

def print_educational_data(educational_data, page):
    """Display the parsed educational data."""
    if educational_data:
        print(f"\nParsed Educational Data from Page {page}:")
        for degree, stats in educational_data.items():
            print(f"{degree}: Unemployment Rate = {stats['Unemployment Rate']}%, Median Earnings = {stats['Median Earnings']}")
    else:
        print(f"No structured data found on page {page}.")

# Main execution
if __name__ == "__main__":
    pdf_path = input("Enter the path to the PDF file: ")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("PDF file not found. Please provide a valid path.")

    # Process the PDF and extract required data
    process_pdf(pdf_path)
