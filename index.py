import pdfplumber
import csv
import os
import sys

def pdf_to_csv(pdf_path, csv_path):
    """
    Converts tables found in a PDF file to a CSV file.
    """
    try:
        # Check if the PDF file exists
        if not os.path.exists(pdf_path):
            print(f"Error: The file '{pdf_path}' was not found.")
            return

        print(f"Opening PDF: {pdf_path}...")
        
        with pdfplumber.open(pdf_path) as pdf:
            with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                
                total_tables = 0
                for i, page in enumerate(pdf.pages):
                    print(f"Processing page {i + 1}...")
                    tables = page.extract_tables()
                    
                    for table in tables:
                        for row in table:
                            cleaned_row = []
                            for cell in row:
                                if cell is not None:
                                    # Replace newlines with spaces and strip whitespace
                                    cleaned_cell = cell.replace('\n', ' ').strip()
                                    cleaned_row.append(cleaned_cell)
                                else:
                                    cleaned_row.append("")
                            writer.writerow(cleaned_row)
                        
                        # Add an empty row between tables for separation
                        writer.writerow([])
                        total_tables += 1
                
                if total_tables == 0:
                    print("No tables were found in the PDF.")
                else:
                    print(f"Successfully converted {total_tables} tables to '{csv_path}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # If arguments are passed via command line
    if len(sys.argv) == 3:
        input_pdf = sys.argv[1]
        output_csv = sys.argv[2]
        pdf_to_csv(input_pdf, output_csv)
    else:
        # Interactive mode
        print("PDF to CSV Converter")
        print("--------------------")
        input_pdf = input("Enter the path to the PDF file: ").strip().strip('"')
        
        if not input_pdf:
            print("No file path provided.")
        else:
            # Create a default output name if user doesn't specify one (though here we ask)
            default_output = os.path.splitext(input_pdf)[0] + ".csv"
            output_csv = input(f"Enter the path for the CSV file (default: {default_output}): ").strip().strip('"')
            
            if not output_csv:
                output_csv = default_output
            
            pdf_to_csv(input_pdf, output_csv)
