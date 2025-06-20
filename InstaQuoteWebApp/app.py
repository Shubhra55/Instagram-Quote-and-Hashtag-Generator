import os
import logging
from flask import Flask, request, render_template
import google.generativeai as genai
from config import GEMINI_API_KEY
import pandas as pd

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Add file handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

# Initialize the Google Generative AI model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/", methods=["GET", "POST"])
def generate_description():
    if request.method == "POST":
        input_text = request.form.get("input_text")

        prompt = (
            f"Give me 2 line Quotes and 10 Hashtags for an Instagram post for the following text:\n{input_text}\n\n"
            "The description should be no more than 100 characters."
        )

        try:
            response = model.generate_content(prompt)
            description = response.text.strip()
        except Exception as e:
            logging.error(f"API request failed: {e}")
            description = "An error occurred while generating the description."

        # Log the prompt and description
        logging.info(f"Prompt: {input_text}")
        logging.info(f"Description: {description}")

        # Save the prompt and description to an Excel file
        data = {'Prompt': [input_text], 'Description': [description]}
        df = pd.DataFrame(data)
        excel_file = 'prompts_responses.xlsx'
        
        if os.path.exists(excel_file):
            existing_df = pd.read_excel(excel_file)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_excel(excel_file, index=False)

        return render_template("index.html", input_text=input_text, description=description, original_input=input_text)
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)


