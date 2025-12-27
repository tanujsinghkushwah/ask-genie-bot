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
    
    def generate_image_prompt(self, topic: str, tweet_content: str = None) -> str:
        """Generate a detailed prompt for image creation based on the topic and tweet content."""
        if tweet_content:
            prompt = f"""
            Create a visually captivating tech image for this software engineering tweet: "{tweet_content}". Topic: '{topic}'.

            Craft a highly detailed prompt (100+ words) for a 16:9 landscape image:

            - Directly visualize tweet's core hook/insight (e.g., shattered chain for "LLM chains", glowing diagram for system design) with metaphorical drama
            - Modern cyberpunk aesthetic: neon blues/greens on dark backgrounds, high contrast glows, particle effects, floating holographic code snippets or neural connections
            - Dynamic composition: asymmetric, rule-of-thirds, central focal break (exploding myth, unlocking door, speed lines)
            - Cinematic lighting: volumetric god rays, rim lighting on tech elements, lens flares for energy
            - Vibrant accents (electric cyan, fiery orange), professional polish, ultra-detailed 4K
            - NO text/words/typography anywhere
            - Single paragraph output, ready for AI image gen

            Make it thumb-stopping for devs scrolling X.
            """
        else:
            prompt = f"""
            Create a visually captivating tech image for this software engineering topic: '{topic}'.

            Craft a highly detailed prompt (100+ words) for a 16:9 landscape image:

            - Directly visualize tweet's core hook/insight (e.g., shattered chain for "LLM chains", glowing diagram for system design) with metaphorical drama
            - Modern cyberpunk aesthetic: neon blues/greens on dark backgrounds, high contrast glows, particle effects, floating holographic code snippets or neural connections
            - Dynamic composition: asymmetric, rule-of-thirds, central focal break (exploding myth, unlocking door, speed lines)
            - Cinematic lighting: volumetric god rays, rim lighting on tech elements, lens flares for energy
            - Vibrant accents (electric cyan, fiery orange), professional polish, ultra-detailed 4K
            - NO text/words/typography anywhere
            - Single paragraph output, ready for AI image gen

            Make it thumb-stopping for devs scrolling X.
            """
        
        response = self.model.generate_content(prompt)
        # Limit to 500 characters for image generation API
        image_prompt = response.text.strip()
        if len(image_prompt) > 500:
            image_prompt = image_prompt[:500]
        
        print(f"Generated image prompt: {image_prompt}")
        return image_prompt




