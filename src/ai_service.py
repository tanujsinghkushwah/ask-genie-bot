"""AI service for multiple LLM providers (Groq, Gemini)."""

from typing import Optional
import google.generativeai as genai
from groq import Groq


class AIService:
    """Service for interacting with multiple AI providers (Groq, Gemini)."""
    
    def __init__(self, provider: str, api_key: str, model_name: str, fallback_api_key: Optional[str] = None, fallback_model: Optional[str] = None):
        """
        Initialize the AI service with provider, API key and model name.
        
        Args:
            provider: 'groq' or 'gemini'
            api_key: Primary API key
            model_name: Primary model name
            fallback_api_key: Fallback API key (optional)
            fallback_model: Fallback model name (optional)
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model_name = model_name
        self.fallback_api_key = fallback_api_key
        self.fallback_model = fallback_model
        self.conversation_history = {}
        
        # Initialize primary provider
        if self.provider == 'groq':
            self.client = Groq(api_key=api_key)
            self.gemini_model = None
        elif self.provider == 'gemini':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.client = None
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'groq' or 'gemini'.")
    
    def generate_response(self, prompt: str, conversation_id: Optional[str] = None) -> Optional[str]:
        """Generate an AI response using the configured provider with fallback support."""
        try:
            if self.provider == 'groq':
                return self._generate_groq_response(prompt, conversation_id)
            else:  # gemini
                return self._generate_gemini_response(prompt, conversation_id)
        except Exception as e:
            print(f"Error generating AI response with {self.provider}: {e}")
            # Try fallback if available
            if self.fallback_api_key and self.fallback_model and self.provider != 'gemini':
                print(f"Attempting fallback to Gemini...")
                try:
                    return self._generate_gemini_fallback(prompt, conversation_id)
                except Exception as fallback_error:
                    print(f"Fallback also failed: {fallback_error}")
            return None
    
    def _generate_groq_response(self, prompt: str, conversation_id: Optional[str] = None) -> str:
        """Generate response using Groq API."""
        messages = []
        
        # Add conversation history if available
        if conversation_id and conversation_id in self.conversation_history:
            messages = self.conversation_history[conversation_id]
        
        # Add current user message
        messages.append({"role": "user", "content": prompt})
        
        # Generate response
        if self.client is None:
            raise ValueError("Groq client not initialized")
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
        )
        
        response_text = chat_completion.choices[0].message.content
        
        # Update conversation history
        if conversation_id:
            messages.append({"role": "assistant", "content": response_text})
            self.conversation_history[conversation_id] = messages
        
        return response_text
    
    def _generate_gemini_response(self, prompt: str, conversation_id: Optional[str] = None) -> str:
        """Generate response using Gemini API."""
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
    
    def _generate_gemini_fallback(self, prompt: str, conversation_id: Optional[str] = None) -> str:
        """Generate response using Gemini as fallback."""
        if not self.fallback_api_key or not self.fallback_model:
            raise ValueError("Fallback API key or model not configured")
        genai.configure(api_key=self.fallback_api_key)
        fallback_model = genai.GenerativeModel(self.fallback_model)
        
        response = fallback_model.generate_content(prompt)
        return response.text
    
    def generate_image_prompt(self, topic: str, tweet_content: Optional[str] = None) -> Optional[str]:
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
        
        # Use generate_response which handles provider selection and fallback
        response_text = self.generate_response(prompt)
        
        if not response_text:
            return None
        
        # Limit to 500 characters for image generation API
        image_prompt = response_text.strip()
        if len(image_prompt) > 500:
            image_prompt = image_prompt[:500]
        
        print(f"Generated image prompt: {image_prompt}")
        return image_prompt




