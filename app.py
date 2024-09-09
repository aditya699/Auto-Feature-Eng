from flask import Flask, request, jsonify, render_template
import pandas as pd
import json
import traceback
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
            
            if not categorical_columns:
                return jsonify({'error': 'No categorical columns found in the CSV'}), 400
            
            # Select the first categorical column as the filter
            filter_column = categorical_columns[3]
            filter_categories = df[filter_column].unique().tolist()
            
            data = []
            for col in numeric_columns:
                for category in filter_categories:
                    subset = df[df[filter_column] == category]
                    data.append({
                        "name": col,
                        "category": category,
                        "value": subset[col].mean()
                    })
            
            return jsonify({
                'data': data,
                'columns': numeric_columns,
                'categories': filter_categories,
                'filterColumn': filter_column
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        app.logger.error(f"Error processing file: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)