"""AI service using LiteLLM for unified API interactions."""

import os
from typing import Optional, List, Dict
from litellm import completion
import litellm

# Suppress litellm logging if too verbose
litellm.suppress_instrumentation = True

class AIService:
    """Multi-provider AI service using LiteLLM with fallback support."""
    
    def __init__(self, provider: str, api_key: str, model_name: str, fallback_api_key: Optional[str] = None, fallback_model: Optional[str] = None):
        """Initialize with provider credentials and optional fallback."""
        self.provider = provider.lower()
        self.api_key = api_key
        self.model_name = model_name
        self.fallback_api_key = fallback_api_key
        self.fallback_model_name = fallback_model
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        
    def _get_model_string(self, provider: str, model: str) -> str:
        """Format model string for LiteLLM (e.g., 'openrouter/model')."""
        # If model starts with provider prefix, accept it as is
        if model.startswith(f"{provider}/"):
            return model
            
        if provider == 'openrouter':
            return f"openrouter/{model}"
            
        # For other cases/providers, if slash exists, assume it's fully qualified
        if "/" in model:
            return model
            
        return model

    def generate_response(self, prompt: str, conversation_id: Optional[str] = None) -> Optional[str]:
        """Generate AI response with automatic fallback on failure."""
        
        messages = []
        if conversation_id and conversation_id in self.conversation_history:
            # We copy history to avoid mutating it until success if we were using a different approach,
            # but standard practice is to use valid history.
            messages = list(self.conversation_history[conversation_id])
        
        current_messages = messages + [{"role": "user", "content": prompt}]
        
        primary_model = self._get_model_string(self.provider, self.model_name)
        
        try:
            response = completion(
                model=primary_model,
                messages=current_messages,
                api_key=self.api_key
            )
            response_text = response.choices[0].message.content
            
            if conversation_id:
                current_messages.append({"role": "assistant", "content": response_text})
                self.conversation_history[conversation_id] = current_messages
                
            return response_text
            
        except Exception as e:
            print(f"Error generating AI response with {primary_model}: {e}")
            
        except Exception as e:
            print(f"Error generating AI response with {primary_model}: {e}")
            
            # Fallback logic (generic)
            if self.fallback_api_key and self.fallback_model_name:
                print(f"Attempting fallback...")
                try:
                    fallback_model_str = self.fallback_model_name
                    if "/" not in fallback_model_str:
                         # Assume same provider or simplistic fallback if not fully qualified, 
                         # but ideally fallback model should be fully qualified or handled by provider logic
                         pass 

                    response = completion(
                        model=fallback_model_str,
                        messages=current_messages,
                        api_key=self.fallback_api_key
                    )
                    return response.choices[0].message.content
                except Exception as fallback_error:
                    print(f"Fallback also failed: {fallback_error}")
            return None

    def generate_image_prompt(self, topic: str, tweet_content: Optional[str] = None) -> Optional[str]:
        """Generate a detailed image creation prompt from topic and tweet content."""
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
        
        response_text = self.generate_response(prompt)
        
        if not response_text:
            return None
        
        image_prompt = response_text.strip()[:500]
        print(f"Generated image prompt: {image_prompt}")
        return image_prompt
