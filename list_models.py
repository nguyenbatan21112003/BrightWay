import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    print("Please make sure your GOOGLE_API_KEY is set correctly in the .env file.")
    exit()

print("Available Gemini models that support 'generateContent':")

# List all available models
for model in genai.list_models():
    # Check if the model supports the 'generateContent' method
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
