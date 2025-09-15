import os
import json
import google.generativeai as genai
from PIL import Image

# Path to the service account key file
key_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "credentials", "raterhubautomation-7886dd999472.json")

# Read the API key from the service account file
try:
    with open(key_file_path, 'r') as f:
        service_account_info = json.loads(f.read())
        # Use the private_key_id as the API key
        api_key = service_account_info.get('private_key_id', '')
        
    print(f"API Key: {api_key}")
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    print("Google Generative AI configured with API key from service account")
    
    # List available models
    models = genai.list_models()
    print("Available models:")
    for model in models:
        print(f" - {model.name}")
    
    # Test a simple text generation
    model = genai.GenerativeModel("gemini-2.5-pro")
    response = model.generate_content("Hello, how are you today?")
    print("\nTest response:")
    print(response.text)
    
except Exception as e:
    print(f"Error: {e}")