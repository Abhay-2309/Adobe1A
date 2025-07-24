# inspect.py
from src.adobe_parser import DocumentParser

# IMPORTANT: Put the name of your big PDF file here
PDF_FILE = "input/sample.pdf"

# Initialize the parser
parser = DocumentParser(PDF_FILE)

# Run the inspection
parser.inspect_document()