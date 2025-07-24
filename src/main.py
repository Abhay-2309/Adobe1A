# src/main.py

import os
import json
import time
from adobe_parser import DocumentParser

def process_all_pdfs(input_dir, output_dir):
    """
    Processes all PDF files in the input directory and saves the
    structured output as JSON files in the output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            start_time = time.time()
            print(f"Processing {pdf_path}...")

            try:
                # 1. Initialize the parser
                parser = DocumentParser(pdf_path)

                # 2. Extract the outline
                result = parser.extract_outline()

                end_time = time.time()
                processing_time = end_time - start_time
                print(f"Processed {filename} in {processing_time:.2f} seconds.")
                # 3. Save the result to a JSON file
                output_filename = os.path.splitext(filename)[0] + ".json"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"Successfully created {output_path}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    # These paths will be used inside the Docker container
    # INPUT_DIR = "/app/input"
    # OUTPUT_DIR = "/app/output"

    # For local testing, you might want to use relative paths
    INPUT_DIR = "D:\\ML projects\\Adobe ubdate\\input"
    OUTPUT_DIR = "D:\\ML projects\\Adobe ubdate\\output"

    process_all_pdfs(INPUT_DIR, OUTPUT_DIR)