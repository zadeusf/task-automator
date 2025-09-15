# RaterHubAutomator/ai_analyzer.py
import logging
import re
import os
import json
import base64
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from ..utils.config_manager import config

# Constants
GEMINI_PROMPT = """
You are a Principal AI Quality Analyst tasked with evaluating AI-generated responses for helpfulness and quality. 

Please analyze the provided screenshots of a RaterHub task and provide ratings for:

1. Response A Rating: Rate from 1-8 (1=Not at all helpful, 2=Somewhat helpful, 3=Somewhat helpful+, 4=Mostly helpful, 5=Mostly helpful+, 6=Very helpful, 7=Very helpful+, 8=Extremely helpful)

2. Response B Rating: Rate from 1-8 using the same scale as above

3. SxS (Side-by-Side) Comparison: Choose one of:
   - Much Better on left
   - Better on left  
   - Slightly Better on left
   - About The Same
   - Slightly Better on right
   - Better on right
   - Much Better on right

4. Overall Explanation: Provide a clear explanation of your ratings and comparison

If the task appears to have issues, is incomplete, or cannot be properly evaluated, respond with "Release task" instead.

Format your response exactly as follows:
Response A Rating: [rating]
Response B Rating: [rating]  
SxS: [comparison]
Overall Explanation: [explanation]

OR simply:
Release task
"""

class AIAnalyzer:
    def __init__(self):
        vertex_config = config.get('vertex_ai', {})
        self.project = vertex_config.get("project", "raterhubautomation")
        self.location = vertex_config.get("location", "us-central1")
        self.model_name = vertex_config.get("model", "gemini-1.5-pro")

        # Set the service account key file path from config
        key_file = vertex_config.get("key_file", "raterhubautomation-7886dd999472.json")
        key_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), key_file)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path
        logging.info(f"Using Google Cloud service account key: {key_file_path}")

        # Initialize the Vertex AI SDK
        try:
            vertexai.init(project=self.project, location=self.location)
            logging.info(f"Vertex AI initialized with project '{self.project}' in location '{self.location}'")
        except Exception as e:
            logging.error(f"Error initializing Vertex AI: {e}")

    def analyze_screenshots(self, screenshot_paths):
        """Sends screenshots to Vertex AI and returns the text response."""
        try:
            # Load the generative model
            model = GenerativeModel(self.model_name)
            logging.info(f"Using model: {self.model_name}")

            # Prepare the content parts (prompt and images)
            content_parts = [GEMINI_PROMPT]
            
            # Add images to the request
            for path in screenshot_paths:
                try:
                    # Read the image file and create Part from data
                    with open(path, "rb") as f:
                        image_bytes = f.read()
                    # Create image part from bytes using the correct method
                    image_part = Part.from_data(data=image_bytes, mime_type="image/png")
                    content_parts.append(image_part)
                    logging.info(f"Added image {path} to content parts")
                except Exception as img_error:
                    logging.error(f"Error processing image {path}: {img_error}")
            
            # Generate content
            response = model.generate_content(content_parts)
            
            if response and hasattr(response, 'text'):
                logging.info("Received response from Vertex AI.")
                return response.text
            else:
                logging.warning("Empty or invalid response from Vertex AI. Defaulting to 'Release task'.")
                return "Release task"

        except Exception as e:
            logging.error(f"Vertex AI error: {e}. Defaulting to 'Release task'.")
            return "Release task"

def parse_ai_response(response_text):
    """Parses the raw text from the AI into a structured dictionary."""
    if 'Release task' in response_text:
        logging.info("AI response indicates 'Release task'.")
        return {'action': 'release', 'explanation': 'AI recommended releasing this task.'}

    patterns = {
        'a_rating': r'Response A\s*Rating:\s*(.+)',
        'b_rating': r'Response B\s*Rating:\s*(.+)',
        'sxs': r'SxS:\s*(.+)',
        'explanation': r'Overall Explanation:\s*(.+)'
    }

    parsed_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
        if match:
            parsed_data[key] = match.group(1).strip()
        else:
            logging.error(f"Parsing failed: Could not find pattern for '{key}'")
            return {'action': 'release', 'explanation': f'Failed to parse {key} from AI response'} # Fail safely

    # Clean up explanation
    parsed_data['explanation'] = ' '.join(parsed_data['explanation'].split())
    parsed_data['action'] = 'rate'

    logging.info(f"Successfully parsed AI response: {parsed_data}")
    return parsed_data
