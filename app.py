from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.csv'):
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Perform data cleaning and processing
        df = auto_clean_feature_data(df)
        
        # Convert the processed dataframe back to CSV
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        # Send the processed file back to the user
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='processed_data.csv'
        )
    
    return redirect(url_for('index'))

def auto_clean_feature_data(df):
    import google.generativeai as genai
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv()

    # Configure the Gemini API
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

    # Function to generate code using Gemini
    def generate_code_with_gemini(prompt):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text

    # Prepare the prompt for Gemini
    columns = ', '.join(df.columns)
    prompt = f"""
    Given a DataFrame with the following columns: {columns}
    Generate Python code to create new columns based on existing ones.
    The code should:
    1. Create  new columns
    2. Use other columns to create new columns
    3. Handle potential errors or missing data and datatypes error.
    4. Return the updated DataFrame

    Provide only the Python code, no explanations.
    
    Example Output:
    def process_dataframe(df):
        # Create new columns based on existing ones
        df['full_name'] = df['first_name'] + ' ' + df['last_name']
        
        # Use other columns to create new columns
        df['total_amount'] = df['quantity'] * df['price']
        
        # Handle potential errors or missing data
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        df['birth_year'] = pd.to_datetime('today').year - df['age']
        
        # Handle potential datatype errors
        df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
        
        
        return df

    # Apply the function to the DataFrame
    df = process_dataframe(df)
    """

    # Generate code using Gemini
    generated_code = generate_code_with_gemini(prompt)
    

    # Extract code from markdown format
    import re

    # Find the Python code block in the generated content
    code_match = re.search(r'```python\n(.*?)```', generated_code, re.DOTALL)
    
    if code_match:
        extracted_code = code_match.group(1).strip()
        print("Extracted code:")
        print(extracted_code)
        
        # Execute the extracted code
        try:
            exec(extracted_code)
            print("Code executed successfully")
        except Exception as e:
            print(f"Error executing extracted code: {e}")
    else:
        print("No Python code block found in the generated content")


    return df

if __name__ == '__main__':
    app.run(debug=True)
