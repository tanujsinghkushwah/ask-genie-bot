"""AI service for Gemini API interactions."""

import google.generativeai as genai


class AIService:
    """Service for interacting with Google's Gemini AI."""
    
    def __init__(self, api_key: str, model_name: str):
        """Initialize the AI service with API key and model name."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.conversation_history = {}
    
    def generate_response(self, prompt: str, conversation_id: str = None) -> str:
        """Generate an AI response using Gemini API."""
        try:
            # If this is part of a conversation, use history
            if conversation_id and conversation_id in self.conversation_history:
                history = self.conversation_history[conversation_id]
                history.append({"role": "user", "parts": [prompt]})
                chat = self.model.start_chat(history=history)
                response = chat.send_message(prompt)
            else:
                # New conversation
                response = self.model.generate_content(prompt)
                
                if conversation_id:
                    self.conversation_history[conversation_id] = [
                        {"role": "user", "parts": [prompt]},
                        {"role": "model", "parts": [response.text]}
                    ]
            
            return response.text
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return None
    
    def generate_image_prompt(self, topic: str) -> str:
        """Generate a detailed prompt for image creation based on the topic."""
        prompt = f"""
        Create a detailed image prompt for a visually captivating tech-related image about '{topic}'. 
        
        Your image prompt should:
        - Be very specific and detailed (at least 50 words)
        - Include visual elements that would draw attention on social media
        - Describe lighting, style, mood, and composition
        - Mention vibrant colors and high contrast elements
        - Avoid mentioning text or words in the image
        - Have a modern, professional aesthetic
        
        Format your response as a single paragraph with no introductions or explanations.
        """
        
        response = self.model.generate_content(prompt)
        # Limit to 500 characters for image generation API
        image_prompt = response.text.strip()
        if len(image_prompt) > 500:
            image_prompt = image_prompt[:500]
        
        print(f"Generated image prompt: {image_prompt}")
        return image_prompt




