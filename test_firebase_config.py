import firebase_admin
from firebase_admin import credentials, remote_config
import asyncio # Required for template.load()
import traceback

# Define fallback defaults that might be used in bot.py, for context in test output
# These are not strictly used by the test script's core logic but help in understanding sources.
_hardcoded_fallback_defaults_for_context = {
    'API_KEY': 'YOUR_FALLBACK_TWITTER_API_KEY_IN_CODE_TEST_CONTEXT',
    'API_KEY_SECRET': 'YOUR_FALLBACK_TWITTER_API_KEY_SECRET_IN_CODE_TEST_CONTEXT',
    'GEMINI_API_KEY': 'YOUR_FALLBACK_GEMINI_API_KEY_IN_CODE_TEST_CONTEXT',
    # Add other keys if useful for test output context
}

# These are keys we expect to be in Remote Config or in our local defaults.
# The test will try to fetch these specifically.
EXPECTED_KEYS_TO_TEST = [
    'API_KEY',
    'API_KEY_SECRET',
    'ACCESS_TOKEN',
    'ACCESS_TOKEN_SECRET',
    'BEARER_TOKEN',
    'GEMINI_API_KEY',
    'IMAGE_ROUTER_API',
    'STABLE_HORDE_KEY',
    'TEST_SCRIPT_PARAM', # This one comes from local_test_defaults
    'ANOTHER_TEST_KEY'   # This one also from local_test_defaults
]

def initialize_firebase():
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Initialize with service account credentials
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)

def get_and_print_config_values():
    try:
        initialize_firebase()
        
        # Define local defaults specific to this test script's initialization of the template.
        # These will be present in `template.parameters` unless overridden by remote.
        local_test_defaults = {
            "TEST_SCRIPT_PARAM": "local_default_value_for_test_script",
            "ANOTHER_TEST_KEY": "another_local_default_from_script"
        }
        print(f"Initializing ServerTemplate with local_test_defaults: {local_test_defaults}")
        template = remote_config.init_server_template(default_config=local_test_defaults)
        
        print("\nLoading Remote Config template from Firebase backend...")
        asyncio.run(template.load()) # Fetches the template and merges with init_server_template's defaults
        print("Template loaded from backend.")

        print("\nEvaluating the loaded template to get effective values...")
        evaluated_config = template.evaluate() # Returns a firebase_admin.remote_config.Config object

        print("\nAttempting to get values for EXPECTED_KEYS_TO_TEST:")
        all_keys_successfully_read_as_string = True
        found_any_remote_key = False

        for key in EXPECTED_KEYS_TO_TEST:
            try:
                value = evaluated_config.get_string(key) # Or get_bool, get_long, get_double
                source = evaluated_config.get_value_source(key) # e.g., 'remote', 'default_config'
                print(f"  - Key '{key}': '{value}' (Source: {source})")
                if source == 'remote':
                    found_any_remote_key = True
            except ValueError as ve:
                # This occurs if the key exists but is not a string (e.g., boolean, number)
                # or if the key doesn't exist in a way that get_string can process (e.g. no default, no remote)
                print(f"  - Key '{key}': Could not get as STRING. Error: {ve}. Checking source...")
                try:
                    source = evaluated_config.get_value_source(key)
                    if source:
                        print(f"    Source for '{key}' is '{source}'. Try a different getter if it's not a string.")
                    else:
                        print(f"    Source for '{key}' is None/Empty. Key might be missing from remote and local defaults.")
                except Exception as source_e:
                     print(f"    Could not determine source for '{key}'. Error: {source_e}")
                all_keys_successfully_read_as_string = False
            except Exception as e:
                print(f"  - Key '{key}': UNEXPECTED error trying to get_string. Error: {e}")
                all_keys_successfully_read_as_string = False
        
        if not found_any_remote_key:
            print("\nWARNING: No keys were reported as successfully fetched with source 'remote'. ")
            print("This could mean the server template in Firebase is empty or all tested keys only used local defaults.")
            print("Please ensure your server-side Remote Config in Firebase console has parameters published.")

        if not all_keys_successfully_read_as_string:
            print("\nNote: Some EXPECTED_KEYS_TO_TEST could not be read as strings or were not found. ")
            print("If a key is configured in Firebase with a non-string type (boolean, number), use the appropriate getter (e.g., get_bool()).")
            print("If a key is missing, ensure it's in Firebase (Server template) or in local_test_defaults.")
            
        return True # Test script executed, review output for details

    except Exception as e:
        print(f"\nMAJOR ERROR in test script execution: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("--- Firebase Remote Config Test Script ---")
    success = get_and_print_config_values()
    if success:
        print("\n--- Test script finished. Please review the output above. ---")
    else:
        print("\n--- Test script FAILED due to a major error. Please review errors. ---") 