# Auto Feature Engineering

Auto Feature Engineering is an AI-powered web application that automatically enhances your CSV data by generating new features based on existing ones. This tool leverages the power of Google's Gemini AI to create intelligent and relevant features, saving time and improving the quality of your datasets for machine learning projects.

## Features

- Easy-to-use web interface for CSV file upload
- AI-powered feature generation using Google's Gemini model
- Automatic error handling and retry mechanism
- Download enhanced CSV with new features

## How It Works

1. Upload your CSV file through the web interface
2. Our Quantum AI analyzes your data and generates new features
3. Download the enhanced CSV file with additional columns

## Screenshots

![Upload Screen](https://saibaba9758140479.blob.core.windows.net/testimages/AI_FE_1.PNG)
*Initial upload screen*

![Processing Screen](https://saibaba9758140479.blob.core.windows.net/testimages/AI_FE_2.PNG)
*Data processing in progress*

![Download Screen](https://saibaba9758140479.blob.core.windows.net/testimages/AI_FE_3.PNG)
*Enhanced data ready for download*

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/auto-feature-engineering.git
   cd auto-feature-engineering
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the project root and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. Run the Flask application:
   ```
   python app.py
   ```

5. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Click on the "Select CSV File" button to choose your input CSV file.
2. Wait for the AI to process and enhance your data.
3. Once processing is complete, your enhanced CSV file will automatically download.

## Technologies Used

- Flask: Web framework
- Pandas: Data manipulation
- Google Gemini AI: Feature generation
- HTML/CSS: User interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Google Gemini AI for powering the feature generation
- Flask and Pandas communities for their excellent libraries