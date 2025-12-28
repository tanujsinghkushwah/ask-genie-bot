"""AskMeGenie Twitter Bot - A modular Twitter bot for tech content."""

__version__ = "1.0.0"

from src.bot import GenieTweetBot
from src.config import load_config
from src.constants import KEYWORDS, ULTIMATE_FALLBACK_DEFAULTS

__all__ = [
    'GenieTweetBot',
    'load_config',
    'KEYWORDS',
    'ULTIMATE_FALLBACK_DEFAULTS',
]




