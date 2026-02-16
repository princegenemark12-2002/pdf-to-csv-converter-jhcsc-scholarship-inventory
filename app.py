import os
import csv
import pdfplumber
import pandas as pd
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'downloads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def pdf_to_csv(pdf_path, csv_path):
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
                                    cleaned_cell = cell.replace('\n', ' ').strip()
                                    cleaned_row.append(cleaned_cell)
                                else:
                                    cleaned_row.append("")
                            writer.writerow(cleaned_row)
                        writer.writerow([])
                        total_tables += 1
                return total_tables
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return -1

def excel_to_csv(excel_path, csv_path):
    try:
        df = pd.read_excel(excel_path, engine="openpyxl")
        df.to_csv(csv_path, index=False)
        return "ok"
    except ImportError:
        return "missing_engine"
    except ValueError as e:
        print(f"Error processing Excel value: {e}")
        return "value_error"
    except Exception as e:
        print(f"Error processing Excel: {e}")
        return "other_error"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        lower_name = filename.lower()
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        csv_filename = os.path.splitext(filename)[0] + '.csv'
        csv_path = os.path.join(app.config['OUTPUT_FOLDER'], csv_filename)
        
        if lower_name.endswith('.pdf'):
            result = pdf_to_csv(input_path, csv_path)
            if result >= 0:
                flash(f'Successfully converted PDF. Found {result} tables.')
                return render_template('index.html', download_file=csv_filename)
            else:
                flash('An error occurred during PDF conversion.')
                return redirect(request.url)
        elif lower_name.endswith('.xlsx') or lower_name.endswith('.xls'):
            result = excel_to_csv(input_path, csv_path)
            if result == "ok":
                flash('Successfully converted Excel file.')
                return render_template('index.html', download_file=csv_filename)
            elif result == "missing_engine":
                flash('Excel support requires the openpyxl package. Please install it and restart the app.')
                return redirect(request.url)
            elif result == "value_error":
                flash('Excel file format cannot be read. Please upload a valid .xlsx or .xls file.')
                return redirect(request.url)
            else:
                flash('An unexpected error occurred during Excel conversion.')
                return redirect(request.url)
        else:
            flash('Allowed file types are PDF and Excel (.xlsx, .xls)')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
