"""Constants used throughout the application."""

# Keywords to search for
KEYWORDS = [
    "Interview", "Software Engineer", "Leetcode", 
    "System Design", "High Level Design", "Low Level Design", 
    "AI", "Blockchain", "Crypto", "Cloud Computing", "DevOps",
    "Microservices", "Database", "Caching", "Operating Systems",
    "Kubernetes", "Docker", "Machine Learning", "Tech News", "Agentic Systems", "Tech History"
]

# Hardcoded ultimate fallbacks, used if Remote Config is entirely unavailable
# and get_config_value isn't called with a specific default.
# These are passed to init_server_template's default_config.
ULTIMATE_FALLBACK_DEFAULTS = {
    'API_KEY': 'YOUR_FALLBACK_API_KEY_IN_CODE',
    'API_KEY_SECRET': 'YOUR_FALLBACK_API_KEY_SECRET_IN_CODE',
    'ACCESS_TOKEN': 'YOUR_FALLBACK_ACCESS_TOKEN_IN_CODE',
    'ACCESS_TOKEN_SECRET': 'YOUR_FALLBACK_ACCESS_TOKEN_SECRET_IN_CODE',
    'GEMINI_API_KEY': 'YOUR_FALLBACK_GEMINI_API_KEY_IN_CODE',
    'BEARER_TOKEN': '',
    'MODEL_NAME': 'gemini-2.5-flash'
}




