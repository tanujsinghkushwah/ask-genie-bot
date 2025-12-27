"""Configuration management for Firebase Remote Config and environment variables."""

import os
import asyncio
import firebase_admin
from firebase_admin import credentials, remote_config
from dotenv import load_dotenv

from .constants import ULTIMATE_FALLBACK_DEFAULTS

# Load environment variables from .env file if it exists
load_dotenv()


def initialize_firebase_and_load_config():
    """Initializes Firebase app and loads Remote Config template."""
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    
    print("Initializing Remote Config server template...")
    # Initialize with ultimate fallbacks. Remote values will override these.
    template = remote_config.init_server_template(default_config=ULTIMATE_FALLBACK_DEFAULTS)
    
    print("Loading Remote Config template from Firebase backend...")
    try:
        asyncio.run(template.load())  # Fetches the template and merges with defaults
        print("Remote Config template loaded successfully.")
    except Exception as e:
        print(f"ERROR loading Remote Config template from backend: {e}")
        print("Proceeding with ULTIMATE_FALLBACK_DEFAULTS or specific get_config_value defaults.")
        # If load fails, template still contains ULTIMATE_FALLBACK_DEFAULTS

    print("Evaluating Remote Config template...")
    return template.evaluate()  # Returns a firebase_admin.remote_config.Config object


def get_config_value(evaluated_config, key, default_value=""):
    """Gets a config value from the evaluated Remote Config object, with fallback to .env file."""
    try:
        # Attempt to get the value as a string, common for env vars
        value = evaluated_config.get_string(key)
        source = evaluated_config.get_value_source(key)
        # print(f"Retrieved '{key}' from Remote Config: '{value}' (Source: {source})") # Optional: verbose logging
        return value
    except ValueError:
        # This can happen if the key exists but is not a string (e.g., boolean, number)
        # or, more commonly, if the key is not found (neither remote nor in init_server_template's defaults)
        # In this case, check environment variables (.env file) as fallback
        env_value = os.getenv(key)
        if env_value:
            # print(f"Retrieved '{key}' from environment variable: '{env_value}'") # Optional: verbose logging
            return env_value
        # print(f"Key '{key}' not found as string or not string type in evaluated_config. Using function default: '{default_value}'.") # Optional: verbose logging
        return default_value
    except Exception as e:
        print(f"Error fetching '{key}' from evaluated_config: {e}. Checking environment variables...")
        # Fallback to environment variable
        env_value = os.getenv(key)
        if env_value:
            return env_value
        print(f"Using function default: '{default_value}'.")
        return default_value


def load_config():
    """Load and return all configuration values."""
    # Initialize Firebase and Load Remote Config ONCE at startup
    evaluated_remote_config = initialize_firebase_and_load_config()
    
    # Twitter API credentials
    config = {
        'API_KEY': get_config_value(evaluated_remote_config, 'API_KEY', ULTIMATE_FALLBACK_DEFAULTS['API_KEY']),
        'API_KEY_SECRET': get_config_value(evaluated_remote_config, 'API_KEY_SECRET', ULTIMATE_FALLBACK_DEFAULTS['API_KEY_SECRET']),
        'ACCESS_TOKEN': get_config_value(evaluated_remote_config, 'ACCESS_TOKEN', ULTIMATE_FALLBACK_DEFAULTS['ACCESS_TOKEN']),
        'ACCESS_TOKEN_SECRET': get_config_value(evaluated_remote_config, 'ACCESS_TOKEN_SECRET', ULTIMATE_FALLBACK_DEFAULTS['ACCESS_TOKEN_SECRET']),
        'BEARER_TOKEN': get_config_value(evaluated_remote_config, 'BEARER_TOKEN', ULTIMATE_FALLBACK_DEFAULTS['BEARER_TOKEN']),
        'GEMINI_API_KEY': get_config_value(evaluated_remote_config, 'GEMINI_API_KEY', ULTIMATE_FALLBACK_DEFAULTS['GEMINI_API_KEY']),
        'MODEL_NAME': get_config_value(evaluated_remote_config, 'MODEL_NAME', ULTIMATE_FALLBACK_DEFAULTS['MODEL_NAME']),
    }
    
    return config




