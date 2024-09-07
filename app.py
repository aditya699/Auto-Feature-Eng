from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import json

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'csvFile' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['csvFile']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.csv'):
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Convert DataFrame to JSON for analysis
        csv_content = df.to_json(orient='records')
        
        # Analyze the CSV using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f'''Analyze the following CSV data and provide insights. 
        Also, suggest a relevant chart type (pie, bar, line, or scatter) and provide the data for it.
        Return your response as a JSON object with two keys: 'analysis' (string) and 'chart' (object with type, labels, and data).
        CSV content: {csv_content}'''
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        result = json.loads(response.text)
        
        # Return the analysis and chart data
        return jsonify(result)
    
    return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(debug=True)