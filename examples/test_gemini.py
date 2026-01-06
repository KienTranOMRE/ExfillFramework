import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in environment variables")
    print("Please set GEMINI_API_KEY in your .env file")
    exit(1)

# Configure Gemini API
genai.configure(api_key=api_key)

try:
    # Initialize the model
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Test with a simple prompt
    print("Testing Gemini API with model: gemini-3.0-flash-preview")
    print("Sending test request...")
    
    response = model.generate_content("Say hello in one sentence.")
    
    print("\n✅ API Key is working!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("API Key may be invalid or there's a connection issue.")

