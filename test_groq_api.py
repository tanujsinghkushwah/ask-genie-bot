"""Test script to debug Groq API key."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from groq import Groq

# Get the API key
api_key = os.environ.get("GROQ_API_KEY")

print(f"API Key loaded: {'Yes' if api_key else 'No'}")
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key prefix: {api_key[:10]}..." if api_key and len(api_key) > 10 else "N/A")

try:
    client = Groq(
        api_key=api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of fast language models",
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    print("\n✅ SUCCESS! Groq API is working correctly.")
    print(f"\nResponse: {chat_completion.choices[0].message.content[:200]}...")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPossible issues:")
    print("1. API key is invalid or expired")
    print("2. API key was not loaded from .env correctly")
    print("3. Environment variable name mismatch")
