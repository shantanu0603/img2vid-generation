# prompt_generator.py
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = ""
genai.configure(api_key=GEMINI_API_KEY)

def generate_random_prompt():
    """Generate a random prompt using Gemini API"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt_template = """
        Generate a creative and specific prompt for a short video (10-30 seconds) featuring 
        two people engaged in a casual, everyday activity. The prompt should:
        - Be natural and realistic
        - Involve simple interaction between the people
        - Be suitable for filming in a typical location
        - Not require special effects or complex setup
        - Be specific about the action but brief (1-2 sentences)
        
        Generate just the prompt with no additional text or explanation.
        """
        response = model.generate_content(prompt_template)
        return response.text.strip()
    except Exception as e:
        return f"Error generating prompt: {str(e)}"
