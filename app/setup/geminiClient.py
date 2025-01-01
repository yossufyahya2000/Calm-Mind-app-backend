import google.generativeai as genai
from dotenv import load_dotenv
import os

def geminiClient():
    load_dotenv()
    
    # Configure the Gemini API
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    
    # Create the model
    model = genai.GenerativeModel('gemini-pro')
    
    return model
