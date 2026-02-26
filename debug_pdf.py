import pdfplumber
import pandas as pd
import sys

def debug_pdf_extraction(pdf_path):
    print(f"Analyzing {pdf_path}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages: {len(pdf.pages)}")
            
            # Check first few pages
            for i, page in enumerate(pdf.pages[:3]):
                print(f"\n--- Page {i+1} ---")
                
                # Try default extraction
                tables = page.extract_tables()
                print(f"Default extraction found {len(tables)} tables")
                
                if tables:
                    for j, table in enumerate(tables):
                        df = pd.DataFrame(table)
                        print(f"Table {j+1} shape: {df.shape}")
                        print("First 2 rows:")
                        print(df.head(2))
                else:
                    print("No tables found with default settings")
                    
                    # Try text extraction to see content
                    text = page.extract_text()
                    if text:
                        print("Page text preview:")
                        print(text[:200])
                    else:
                        print("No text found (might be image-based)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    pdf_path = r"c:\Users\ACER\python\1ST-SEM-23-24-MAIN-B-13.1 nnn.pdf"
    debug_pdf_extraction(pdf_path)
