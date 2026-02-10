import pdfplumber

pdf_path = r"c:\Users\ACER\python\Josefina H. Cerilles State College_2nd SemAY23-24_Batch 1.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        if len(pdf.pages) > 0:
            page = pdf.pages[0]
            
            print("\n--- Raw Text Extraction (First 500 chars) ---")
            text = page.extract_text()
            if text:
                print(text[:500])
            else:
                print("No text found.")

            print("\n--- Default Table Extraction ---")
            tables = page.extract_tables()
            if tables:
                print(f"Found {len(tables)} tables.")
                for i, table in enumerate(tables):
                    print(f"Table {i+1} - First row (Header): {table[0]}")
                    if len(table) > 1:
                        print(f"Table {i+1} - Second row (Data): {table[1]}")
            else:
                print("No tables found with default settings.")
                
except Exception as e:
    print(f"Error: {e}")
