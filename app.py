import os
import csv
import pdfplumber
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'downloads'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def pdf_to_csv(pdf_path, csv_path):
    """
    Converts tables found in a PDF file to a CSV file.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                total_tables = 0
                for page in pdf.pages:
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
                        writer.writerow([]) # Separator
                        total_tables += 1
                return total_tables
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return -1

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pdf_path)
            
            # Generate output filename
            csv_filename = os.path.splitext(filename)[0] + '.csv'
            csv_path = os.path.join(app.config['OUTPUT_FOLDER'], csv_filename)
            
            # Convert
            result = pdf_to_csv(pdf_path, csv_path)
            
            if result >= 0:
                flash(f'Successfully converted! Found {result} tables.')
                return render_template('index.html', download_file=csv_filename)
            else:
                flash('An error occurred during conversion.')
                return redirect(request.url)
        else:
            flash('Allowed file types are PDF')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
