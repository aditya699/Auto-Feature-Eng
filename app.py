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
        processed_df = auto_clean_feature_data(df)
        
        # Convert the processed dataframe back to CSV
        output = io.StringIO()
        processed_df.to_csv(output, index=False)
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
    import re

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
    1. Create new columns
    2. Use other columns to create new columns
    3. Handle potential errors or missing data and datatypes error.
    4. Return the updated DataFrame

    IMPORTANT:While creating new columns make sure to not add any business logic by yourself.
    Make use of the existing columns to create new columns.
    Create Generic columns not specific to any business logic.

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

        # Extract email domain
        df['email_domain'] = df['email'].str.split('@').str[1]
        
        return df

    # Apply the function to the DataFrame
    df = process_dataframe(df)
    """

    # Function to execute generated code and handle errors
    def execute_generated_code(code, df, prompt, max_tries=3):
        for attempt in range(max_tries):
            try:
                df_copy = df.copy()
                exec(code, globals(), {'df': df_copy})
                if len(df_copy.columns) > len(df.columns):
                    return df_copy
                else:
                    raise ValueError("No new columns were added to the DataFrame")
            except Exception as e:
                error_message = f"Error in attempt {attempt + 1}: {str(e)}"
                print(error_message)
                
                error_prompt = f"""
                {prompt}

                The previous code produced an error or did not add any new columns. Please fix the code and try again.
                Error message: {error_message}

                Previous code:
                {code}

                Please provide corrected code that addresses this error, ensures new columns are added, and follows the original instructions.
                Only provide Python code as output.
                """
                
                code = generate_code_with_gemini(error_prompt)
                code_match = re.search(r'```python\n(.*?)```', code, re.DOTALL)
                if code_match:
                    code = code_match.group(1).strip()
                else:
                    print("No Python code block found in the generated content")
                    continue  # Try again with a new generation
        
        print(f"Failed to generate working code after {max_tries} attempts.")
        raise ValueError("Unable to process the DataFrame")

    # Generate initial code using Gemini
    generated_code = generate_code_with_gemini(prompt)

    # Extract code from markdown format
    code_match = re.search(r'```python\n(.*?)```', generated_code, re.DOTALL)
    
    if code_match:
        extracted_code = code_match.group(1).strip()
        print("Extracted code:")
        print(extracted_code)
        
        # Execute the extracted code with error handling and retries
        try:
            processed_df = execute_generated_code(extracted_code, df, prompt)
            return processed_df
        except ValueError as e:
            print(f"Error: {str(e)}")
            return df  # Return original DataFrame if processing fails
    else:
        print("No Python code block found in the generated content")
        return df  # Return original DataFrame if no code is generated


if __name__ == '__main__':
    app.run(debug=True)
