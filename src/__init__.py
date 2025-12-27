"""AskMeGenie Twitter Bot - A modular Twitter bot for tech content."""

__version__ = "1.0.0"

from .bot import GenieTweetBot
from .config import load_config
from .constants import KEYWORDS, ULTIMATE_FALLBACK_DEFAULTS

__all__ = [
    'GenieTweetBot',
    'load_config',
    'KEYWORDS',
    'ULTIMATE_FALLBACK_DEFAULTS',
]




