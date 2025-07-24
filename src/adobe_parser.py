# src/document_parser.py

import fitz  # PyMuPDF
import re
from collections import Counter
import statistics # We'll use this for better analysis

class DocumentParser:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.font_counts, self.size_counts = self._get_document_styles()
        self.body_text_size = self._get_body_text_size()
        # NEW: A flag to check if the document has rich font info
        self.has_font_info = self._check_font_variety()

    def _get_document_styles(self):
        """Extracts font names, sizes, and their counts."""
        font_counts, size_counts = Counter(), Counter()
        for page in self.doc:
            for block in page.get_text("dict")["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_counts[span["font"]] += 1
                            size_counts[round(span["size"])] += 1
        return font_counts, size_counts

    def _get_body_text_size(self):
        """Determines the most common font size."""
        if not self.size_counts:
            return 10.0
        # Get the most common font size
        return self.size_counts.most_common(1)[0][0]

    def _check_font_variety(self):
        """Checks if the document has more than one font size. Crucial for scanned PDF detection."""
        # If there's only one font size and it's 0 or 1, it's likely a scanned PDF
        if len(self.size_counts) <= 1 and (0 in self.size_counts or 1 in self.size_counts):
            print("INFO: This looks like a scanned PDF with no font size information.")
            return False
        return True

    # In src/adobe_parser.py

    def _calculate_score_full(self, span, text):
        """Calculates score using FULL metadata. For digitally native PDFs."""
        score = 0
        
        # Rule 1: Relative Font Size
        if span['size'] > self.body_text_size * 1.4:
            score += 15
        elif span['size'] > self.body_text_size * 1.1: # Made this more sensitive
            score += 8

        # Rule 2: Boldness - now more important
        if span['flags'] & 16: # Bold
            score += 7 # Increased score for boldness

        # Rule 3: Numbering
        if re.match(r'^\d+(\.\d+)*\s', text):
             score += 8
             
        # NEW Rule 4: Short Line Length - Headings are usually short.
        # This helps distinguish a heading from a long, bolded paragraph.
        if len(text.split()) < 10:
            score += 4
        
        return score

    def _calculate_score_text_only(self, text):
        """Calculates score using ONLY text. For scanned PDFs."""
        score = 0
        if re.match(r'^\d+(\.\d+)*\s', text) or re.match(r'^[A-Z]\.\s', text):
            score += 20
        if text.isupper() and len(text.split()) < 10:
            score += 10
        if len(text.split()) < 8:
            score += 5
        return score

    def extract_outline(self):
        """Extracts the title and a hierarchical outline."""
        potential_headings = []
        
        for page_num, page in enumerate(self.doc):
            blocks = page.get_text("dict", sort=True)["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = "".join(span['text'] for span in line["spans"]).strip()
                        if not line_text:
                            continue
                        
                        first_span = line["spans"][0]
                        
                        if self.has_font_info:
                            score = self._calculate_score_full(first_span, line_text)
                        else:
                            score = self._calculate_score_text_only(line_text)
                        
                        # >>>>> THIS IS THE LINE TO CHANGE <<<<<
                        if score >= 5: # Changed from 'score > 5'
                        # >>>>>-----------------------------<<<<<
                            potential_headings.append({
                                "text": line_text,
                                "score": score,
                                "size": first_span['size'],
                                "page": page_num + 1,
                                "y0": line['bbox'][1]
                            })
        if not potential_headings:
            return {"title": "Unknown Title", "outline": []}

        # Sort by page then position on page to ensure correct order
        potential_headings.sort(key=lambda x: (x['page'], x['y0']))
        
        # A more robust way to find the title
        title = potential_headings[0]['text'] # Assume first major heading is title
        
        outline = []
        current_h1_size = 0
        current_h2_size = 0

        # A more dynamic H1/H2/H3 assignment
        for h in potential_headings[1:]: # Skip title
            # This is a simple heuristic, can be improved with clustering
            if h['score'] > 18: level = "H1"
            elif h['score'] > 12: level = "H2"
            else: level = "H3"
            
            outline.append({"level": level, "text": h['text'], "page": h['page']})

        return {"title": title, "outline": outline}

    # NEW: A helper function for you to debug
    def inspect_document(self, page_limit=3):
        """Prints diagnostic info for the first few pages."""
        print("--- Document Inspector ---")
        print(f"Body Text Size Determined: {self.body_text_size}pt")
        print(f"Rich Font Info Detected: {self.has_font_info}")
        print("\n--- Sample Spans and Scores ---")
        for i, page in enumerate(self.doc):
            if i >= page_limit: break
            print(f"\n--- Page {i+1} ---")
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = "".join(s['text'] for s in line["spans"]).strip()
                        if line_text:
                            span = line["spans"][0]
                            if self.has_font_info:
                                score = self._calculate_score_full(span, line_text)
                            else:
                                score = self._calculate_score_text_only(line_text)
                            
                            # Print any line with a potential score, or anything in bold/large
                            if score > 0 or span['flags'] & 16 or span['size'] > self.body_text_size:
                                print(f"Text: '{line_text[:50]}...' | Size: {span['size']:.1f} | Bold: {bool(span['flags'] & 16)} | Score: {score}")
        print("\n--- End of Inspection ---")